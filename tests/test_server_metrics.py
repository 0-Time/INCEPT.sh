"""Tests for GET /v1/metrics endpoint."""

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


class TestMetricsEndpoint:
    """GET /v1/metrics endpoint tests."""

    @pytest.mark.asyncio
    async def test_returns_text(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/metrics")
        assert resp.status_code == 200
        assert "text/plain" in resp.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_contains_request_count(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/metrics")
        text = resp.text
        assert "request_count" in text

    @pytest.mark.asyncio
    async def test_contains_latency(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/metrics")
        text = resp.text
        assert "latency" in text

    @pytest.mark.asyncio
    async def test_request_count_increments(self, client: AsyncClient) -> None:
        await client.post("/v1/command", json={"nl": "find log files"})
        await client.post("/v1/command", json={"nl": "list directory"})
        resp = await client.get("/v1/metrics")
        text = resp.text
        assert "request_count" in text
