"""In-memory session store."""

from __future__ import annotations

import time
import uuid
from typing import Any

from incept.session.models import Session, Turn


class SessionLimitError(Exception):
    """Raised when the maximum number of concurrent sessions is reached."""


class SessionStore:
    """In-memory session storage with timeout and size limits.

    Args:
        timeout_seconds: Seconds before a session expires.
        max_turns: Maximum turns kept per session (oldest dropped).
    """

    def __init__(
        self,
        timeout_seconds: int = 1800,
        max_turns: int = 20,
        max_sessions: int = 1000,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_turns = max_turns
        self.max_sessions = max_sessions
        self._sessions: dict[str, Session] = {}

    def create(self) -> str:
        """Create a new session and return its ID.

        Raises SessionLimitError if max_sessions is reached and no expired
        sessions can be freed.
        """
        if self.max_sessions > 0 and len(self._sessions) >= self.max_sessions:
            self.cleanup_expired()
            if len(self._sessions) >= self.max_sessions:
                raise SessionLimitError(
                    f"Maximum session limit ({self.max_sessions}) reached"
                )
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = Session(session_id=session_id)
        return session_id

    def get(self, session_id: str) -> Session | None:
        """Get a session by ID, or None if not found."""
        return self._sessions.get(session_id)

    def add_turn(self, session_id: str, turn: Turn) -> None:
        """Add a turn to a session, trimming oldest if over max_turns."""
        session = self._sessions.get(session_id)
        if session is None:
            return
        session.turns.append(turn)
        session.last_active = time.time()
        # Trim oldest turns if over limit
        if len(session.turns) > self.max_turns:
            session.turns = session.turns[-self.max_turns :]

    def update_context(self, session_id: str, updates: dict[str, Any]) -> None:
        """Merge context updates into a session."""
        session = self._sessions.get(session_id)
        if session is None:
            return
        session.context_updates.update(updates)
        session.last_active = time.time()

    def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count of removed sessions."""
        now = time.time()
        expired = [
            sid
            for sid, s in self._sessions.items()
            if now - s.last_active > self.timeout_seconds
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)
