"""Tests for FastAPI app factory."""

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


class TestAppFactory:
    """App factory creates working FastAPI application."""

    @pytest.mark.asyncio
    async def test_create_app_returns_fastapi(self, test_config: ServerConfig) -> None:
        from fastapi import FastAPI

        app = create_app(test_config)
        assert isinstance(app, FastAPI)

    @pytest.mark.asyncio
    async def test_has_health_route(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/health")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_has_command_route(self, client: AsyncClient) -> None:
        resp = await client.post("/v1/command", json={"nl": "find log files"})
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_has_intents_route(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/intents")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_has_metrics_route(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/metrics")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_has_feedback_route(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/feedback",
            json={
                "session_id": "test",
                "command": "echo hi",
                "outcome": "success",
            },
        )
        assert resp.status_code == 200
