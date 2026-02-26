"""Session and Turn data models."""

from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, Field


class Turn(BaseModel):
    """A single request-response turn in a session."""

    request: str
    intent: str = ""
    command: str = ""
    outcome: str = ""
    subject: str = ""
    timestamp: float = Field(default_factory=time.time)


class Session(BaseModel):
    """A conversation session with turn history."""

    session_id: str
    turns: list[Turn] = Field(default_factory=list)
    context_updates: dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    last_active: float = Field(default_factory=time.time)

    def prev_line(self) -> str | None:
        """Return the subject from the most recent turn, or None."""
        if not self.turns:
            return None
        subject = self.turns[-1].subject
        return subject if subject else None
