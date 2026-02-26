"""Tests for GET /v1/intents endpoint."""

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


class TestIntentsEndpoint:
    """GET /v1/intents endpoint tests."""

    @pytest.mark.asyncio
    async def test_returns_intents(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/intents")
        assert resp.status_code == 200
        data = resp.json()
        assert "intents" in data
        assert len(data["intents"]) == 75

    @pytest.mark.asyncio
    async def test_special_intents_excluded(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/intents")
        data = resp.json()
        intents = data["intents"]
        assert "CLARIFY" not in intents
        assert "OUT_OF_SCOPE" not in intents
        assert "UNSAFE_REQUEST" not in intents

    @pytest.mark.asyncio
    async def test_intents_have_descriptions(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/intents")
        data = resp.json()
        for name, desc in data["intents"].items():
            assert isinstance(desc, str)
            assert len(desc) > 5, f"Intent {name} has too short description"
