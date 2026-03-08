"""Tests for health endpoints."""

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


class TestHealthEndpoint:
    """GET /v1/health and /v1/health/ready tests."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "version" in data
        assert "uptime" in data

    @pytest.mark.asyncio
    async def test_health_version(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/health")
        data = resp.json()
        assert data["version"] == "0.1.0"

    @pytest.mark.asyncio
    async def test_health_not_ready_without_model(self, client: AsyncClient) -> None:
        # Default app starts without model = not ready for NL→command
        resp = await client.get("/v1/health/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ready"] is False

    @pytest.mark.asyncio
    async def test_health_ready_with_model(self, client: AsyncClient) -> None:
        # Simulate model being loaded
        client._transport.app.state.app_state.model_ready = True  # type: ignore[union-attr]
        resp = await client.get("/v1/health/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ready"] is True

    @pytest.mark.asyncio
    async def test_health_uptime_positive(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/health")
        data = resp.json()
        assert data["uptime"] >= 0
