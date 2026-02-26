"""Tests for POST /v1/explain endpoint."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from incept.server.app import create_app
from incept.server.config import ServerConfig


@pytest.fixture()
def app():
    config = ServerConfig()
    return create_app(config)


class TestExplainEndpoint:
    """POST /v1/explain returns structured explanation."""

    @pytest.mark.asyncio
    async def test_explain_success(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/v1/explain", json={"command": "grep -r error /var/log"}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "intent" in data
            assert "explanation" in data
            assert data["intent"] == "search_text"

    @pytest.mark.asyncio
    async def test_explain_empty_body(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/v1/explain", json={})
            assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_explain_unknown_command(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/v1/explain", json={"command": "frobnicator --quux"}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["intent"] is None

    @pytest.mark.asyncio
    async def test_explain_has_risk_level(self, app) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/v1/explain", json={"command": "apt-get install nginx"}
            )
            data = resp.json()
            assert "risk_level" in data

    @pytest.mark.asyncio
    async def test_explain_rate_limited(self, app) -> None:
        """Explain endpoint is rate-limited like other endpoints."""
        low_limit_app = create_app(ServerConfig(rate_limit=2))
        transport = ASGITransport(app=low_limit_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            responses = []
            for _ in range(5):
                resp = await client.post(
                    "/v1/explain", json={"command": "ls"}
                )
                responses.append(resp.status_code)
            assert 429 in responses
