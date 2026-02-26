"""Per-request timeout middleware."""

from __future__ import annotations

import asyncio

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Enforce per-request timeout."""

    def __init__(self, app: object, timeout: float = 30.0) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await asyncio.wait_for(call_next(request), timeout=self.timeout)
        except TimeoutError:
            return JSONResponse(
                {"detail": "Request timed out"},
                status_code=504,
            )
