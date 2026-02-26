"""API key authentication middleware."""

from __future__ import annotations

import hmac

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Paths that bypass auth
_PUBLIC_PATHS = frozenset({"/v1/health", "/v1/health/ready"})


class AuthMiddleware(BaseHTTPMiddleware):
    """Validate Bearer token against configured API key."""

    def __init__(self, app: object, api_key: str | None = None) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip auth if not configured
        if self.api_key is None:
            return await call_next(request)

        # Skip auth for public paths
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Missing API key"}, status_code=401)

        token = auth_header[7:]
        if not hmac.compare_digest(token, self.api_key):
            return JSONResponse({"detail": "Invalid API key"}, status_code=401)

        return await call_next(request)
