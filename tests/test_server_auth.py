"""Tests for API key authentication middleware."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from incept.server.app import create_app
from incept.server.config import ServerConfig


@pytest.fixture
def auth_config() -> ServerConfig:
    return ServerConfig(api_key="secret-key-123", rate_limit=1000)


@pytest.fixture
async def auth_client(auth_config: ServerConfig) -> AsyncClient:
    app = create_app(auth_config)
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c  # type: ignore[misc]


@pytest.fixture
def noauth_config() -> ServerConfig:
    return ServerConfig(api_key=None, rate_limit=1000)


@pytest.fixture
async def noauth_client(noauth_config: ServerConfig) -> AsyncClient:
    app = create_app(noauth_config)
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c  # type: ignore[misc]


class TestAuthMiddleware:
    """API key authentication tests."""

    @pytest.mark.asyncio
    async def test_valid_key_passes(self, auth_client: AsyncClient) -> None:
        resp = await auth_client.post(
            "/v1/command",
            json={"nl": "find log files"},
            headers={"Authorization": "Bearer secret-key-123"},
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_invalid_key_returns_401(self, auth_client: AsyncClient) -> None:
        resp = await auth_client.post(
            "/v1/command",
            json={"nl": "find log files"},
            headers={"Authorization": "Bearer wrong-key"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_key_returns_401(self, auth_client: AsyncClient) -> None:
        resp = await auth_client.post(
            "/v1/command",
            json={"nl": "find log files"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_disabled_allows_all(self, noauth_client: AsyncClient) -> None:
        resp = await noauth_client.post(
            "/v1/command",
            json={"nl": "find log files"},
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_bypasses_auth(self, auth_client: AsyncClient) -> None:
        resp = await auth_client.get("/v1/health")
        assert resp.status_code == 200
