"""Tests for rate limiting middleware."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from incept.server.app import create_app
from incept.server.config import ServerConfig


@pytest.fixture
def rate_config() -> ServerConfig:
    return ServerConfig(api_key=None, rate_limit=3)


@pytest.fixture
async def client(rate_config: ServerConfig) -> AsyncClient:
    app = create_app(rate_config)
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c  # type: ignore[misc]


class TestRateLimitMiddleware:
    """Token bucket rate limiter tests."""

    @pytest.mark.asyncio
    async def test_under_limit_passes(self, client: AsyncClient) -> None:
        resp = await client.post("/v1/command", json={"nl": "find log files"})
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_over_limit_returns_429(self, client: AsyncClient) -> None:
        for _ in range(3):
            await client.post("/v1/command", json={"nl": "find log files"})
        resp = await client.post("/v1/command", json={"nl": "find log files"})
        assert resp.status_code == 429

    @pytest.mark.asyncio
    async def test_health_bypasses_rate_limit(self, client: AsyncClient) -> None:
        # Exhaust rate limit
        for _ in range(5):
            await client.post("/v1/command", json={"nl": "find files"})
        # Health should still work
        resp = await client.get("/v1/health")
        assert resp.status_code == 200
