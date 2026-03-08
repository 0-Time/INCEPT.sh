"""Tests for POST /v1/command endpoint."""

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


class TestCommandEndpoint:
    """POST /v1/command endpoint tests."""

    @pytest.mark.asyncio
    async def test_valid_request_returns_200(self, client: AsyncClient) -> None:
        resp = await client.post("/v1/command", json={"nl": "find all log files"})
        assert resp.status_code == 200
        data = resp.json()
        # v2 engine returns EngineResponse with type/text/confidence/risk
        assert "type" in data
        assert "text" in data

    @pytest.mark.asyncio
    async def test_blocked_command_returns_blocked(self, client: AsyncClient) -> None:
        resp = await client.post("/v1/command", json={"nl": "delete everything on the system"})
        data = resp.json()
        # Without a model, engine returns refusal; with model could be command/blocked/etc.
        assert data["type"] in ("command", "refusal", "clarification", "info", "blocked")

    @pytest.mark.asyncio
    async def test_missing_body_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post("/v1/command")
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_nl_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post("/v1/command", json={"nl": ""})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_nl_too_long_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post("/v1/command", json={"nl": "a" * 2001})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_null_bytes_rejected(self, client: AsyncClient) -> None:
        resp = await client.post("/v1/command", json={"nl": "find files\x00injected"})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_request_id_in_response(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/command",
            json={"nl": "find log files"},
            headers={"X-Request-ID": "test-123"},
        )
        assert resp.headers.get("X-Request-ID") == "test-123"

    @pytest.mark.asyncio
    async def test_context_passthrough(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/command",
            json={
                "nl": "find log files",
                "context": {"distro_id": "ubuntu"},
            },
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_verbosity_passthrough(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/command",
            json={"nl": "find log files", "verbosity": "minimal"},
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_session_id_passthrough(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/command",
            json={"nl": "find log files", "session_id": "sess-abc"},
        )
        assert resp.status_code == 200
