"""Tests for POST /v1/feedback endpoint."""

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


class TestFeedbackEndpoint:
    """POST /v1/feedback endpoint tests."""

    @pytest.mark.asyncio
    async def test_success_feedback_ack(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/feedback",
            json={
                "session_id": "test-sess",
                "command": "apt install nginx",
                "outcome": "success",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "acknowledged"

    @pytest.mark.asyncio
    async def test_failure_with_stderr_triggers_recovery(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/feedback",
            json={
                "session_id": "test-sess",
                "command": "apt install nonexistent-pkg",
                "outcome": "failure",
                "stderr": "E: Unable to locate package nonexistent-pkg",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "recovery"
        assert "recovery" in data

    @pytest.mark.asyncio
    async def test_recovery_suggests_sudo_for_permission(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/feedback",
            json={
                "session_id": "test-sess",
                "command": "cat /etc/shadow",
                "outcome": "failure",
                "stderr": "bash: /etc/shadow: Permission denied",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "recovery"
        assert "sudo" in data["recovery"]["recovery_command"]

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/feedback",
            json={
                "session_id": "test-sess",
                "command": "cat /etc/shadow",
                "outcome": "failure",
                "stderr": "bash: /etc/shadow: Permission denied",
                "attempt": 5,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "recovery"
        assert data["recovery"]["gave_up"] is True
