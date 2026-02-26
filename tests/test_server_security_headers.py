"""Tests for security headers middleware."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from incept.server.app import create_app
from incept.server.config import ServerConfig


@pytest.fixture()
def app():
    config = ServerConfig()
    return create_app(config)


class TestSecurityHeaders:
    """Security headers present on all responses."""

    @pytest.mark.asyncio
    async def test_x_content_type_options(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/v1/health")
            assert resp.headers.get("x-content-type-options") == "nosniff"

    @pytest.mark.asyncio
    async def test_x_frame_options(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/v1/health")
            assert resp.headers.get("x-frame-options") == "DENY"

    @pytest.mark.asyncio
    async def test_strict_transport_security(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/v1/health")
            hsts = resp.headers.get("strict-transport-security")
            assert hsts is not None
            assert "max-age" in hsts

    @pytest.mark.asyncio
    async def test_content_security_policy(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/v1/health")
            csp = resp.headers.get("content-security-policy")
            assert csp is not None
            assert "default-src" in csp

    @pytest.mark.asyncio
    async def test_referrer_policy(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/v1/health")
            assert resp.headers.get("referrer-policy") is not None

    @pytest.mark.asyncio
    async def test_permissions_policy(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/v1/health")
            assert resp.headers.get("permissions-policy") is not None

    @pytest.mark.asyncio
    async def test_cache_control(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/v1/health")
            assert resp.headers.get("cache-control") == "no-store"

    @pytest.mark.asyncio
    async def test_headers_on_non_health_endpoint(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/v1/intents")
            assert resp.headers.get("x-content-type-options") == "nosniff"
            assert resp.headers.get("x-frame-options") == "DENY"
            assert resp.headers.get("cache-control") == "no-store"

    @pytest.mark.asyncio
    async def test_headers_on_404(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/nonexistent")
            assert resp.headers.get("x-content-type-options") == "nosniff"

    @pytest.mark.asyncio
    async def test_custom_response_headers_not_overwritten(self, app) -> None:
        """Security headers don't overwrite existing response headers."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/v1/health")
            # content-type should still be set by FastAPI
            assert "application/json" in resp.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_health_ready_has_security_headers(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/v1/health/ready")
            assert resp.headers.get("x-content-type-options") == "nosniff"
            assert resp.headers.get("x-frame-options") == "DENY"
