"""Tests for X-Request-ID propagation middleware."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from incept.server.app import create_app
from incept.server.config import ServerConfig


@pytest.fixture
def test_config() -> ServerConfig:
    return ServerConfig(api_key=None, rate_limit=1000)


@pytest.fixture
async def client(test_config: ServerConfig) -> AsyncClient:
    app = create_app(test_config)
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c  # type: ignore[misc]


class TestRequestIdMiddleware:
    """X-Request-ID generation and propagation."""

    @pytest.mark.asyncio
    async def test_generates_if_missing(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/health")
        request_id = resp.headers.get("X-Request-ID")
        assert request_id is not None
        assert len(request_id) > 0

    @pytest.mark.asyncio
    async def test_preserves_client_id(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/v1/health",
            headers={"X-Request-ID": "my-custom-id-456"},
        )
        assert resp.headers.get("X-Request-ID") == "my-custom-id-456"

    @pytest.mark.asyncio
    async def test_in_response_header(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/command",
            json={"nl": "find log files"},
            headers={"X-Request-ID": "req-789"},
        )
        assert resp.headers.get("X-Request-ID") == "req-789"
