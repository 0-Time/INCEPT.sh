"""Request/response Pydantic models for the API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class CommandRequest(BaseModel):
    """POST /v1/command request body."""

    nl: str = Field(..., min_length=1, max_length=2000)
    context: dict[str, Any] | None = None
    verbosity: Literal["minimal", "normal", "detailed"] = "normal"
    session_id: str | None = None

    @field_validator("nl")
    @classmethod
    def reject_null_bytes(cls, v: str) -> str:
        if "\x00" in v:
            msg = "Input must not contain null bytes"
            raise ValueError(msg)
        return v


class FeedbackRequest(BaseModel):
    """POST /v1/feedback request body."""

    session_id: str = ""
    command: str
    outcome: Literal["success", "failure"]
    stderr: str = ""
    attempt: int = 1


class HealthResponse(BaseModel):
    """GET /v1/health response."""

    version: str
    uptime: float
    status: str = "ok"


class ReadyResponse(BaseModel):
    """GET /v1/health/ready response."""

    ready: bool
