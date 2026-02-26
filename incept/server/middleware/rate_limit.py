"""Per-client-IP token bucket rate limiter middleware."""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

_PUBLIC_PATHS = frozenset({"/v1/health", "/v1/health/ready", "/v1/metrics"})

_STALE_BUCKET_AGE = 300.0  # seconds before a bucket is considered stale


class _TokenBucket:
    """Token bucket for a single client IP."""

    __slots__ = ("max_tokens", "tokens", "last_refill", "refill_rate")

    def __init__(self, max_tokens: int) -> None:
        self.max_tokens = max_tokens
        self.tokens = float(max_tokens)
        self.last_refill = time.time()
        self.refill_rate = max_tokens / 60.0  # tokens per second

    def refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def consume(self) -> bool:
        """Try to consume a token. Returns True if allowed."""
        self.refill()
        if self.tokens < 1:
            return False
        self.tokens -= 1
        return True

    @property
    def remaining(self) -> int:
        return max(0, int(self.tokens))

    @property
    def retry_after(self) -> int:
        """Seconds until at least one token is available."""
        if self.tokens >= 1:
            return 0
        needed = 1.0 - self.tokens
        return max(1, int(needed / self.refill_rate) + 1)


def _get_client_ip(request: Request, trust_proxy: bool) -> str:
    """Extract client IP from request, optionally using X-Forwarded-For."""
    if trust_proxy:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
    client = request.client
    if client is not None:
        return client.host
    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-client-IP token bucket rate limiter (per minute)."""

    def __init__(
        self,
        app: object,
        requests_per_minute: int = 60,
        trust_proxy: bool = False,
    ) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self.max_tokens = requests_per_minute
        self.trust_proxy = trust_proxy
        self._buckets: dict[str, _TokenBucket] = {}
        self._last_cleanup = time.time()

    def _get_bucket(self, client_ip: str) -> _TokenBucket:
        bucket = self._buckets.get(client_ip)
        if bucket is None:
            bucket = _TokenBucket(self.max_tokens)
            self._buckets[client_ip] = bucket
        return bucket

    def _cleanup_stale_buckets(self) -> None:
        now = time.time()
        if now - self._last_cleanup < 60.0:  # cleanup at most once per minute
            return
        self._last_cleanup = now
        stale = [
            ip
            for ip, bucket in self._buckets.items()
            if now - bucket.last_refill > _STALE_BUCKET_AGE
        ]
        for ip in stale:
            del self._buckets[ip]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        self._cleanup_stale_buckets()

        client_ip = _get_client_ip(request, self.trust_proxy)
        bucket = self._get_bucket(client_ip)

        if not bucket.consume():
            return JSONResponse(
                {"detail": "Rate limit exceeded"},
                status_code=429,
                headers={
                    "Retry-After": str(bucket.retry_after),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(bucket.remaining)
        return response
