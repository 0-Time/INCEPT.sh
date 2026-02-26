"""Tests for session store."""

from __future__ import annotations

import time

import pytest

from incept.session.models import Session, Turn
from incept.session.store import SessionLimitError, SessionStore


class TestSessionStore:
    """Session lifecycle and management."""

    def setup_method(self) -> None:
        self.store = SessionStore(timeout_seconds=2, max_turns=5)

    def test_create_returns_id(self) -> None:
        session_id = self.store.create()
        assert isinstance(session_id, str)
        assert len(session_id) > 0

    def test_get_by_id(self) -> None:
        sid = self.store.create()
        session = self.store.get(sid)
        assert session is not None
        assert session.session_id == sid

    def test_nonexistent_returns_none(self) -> None:
        assert self.store.get("nonexistent-id") is None

    def test_add_turn(self) -> None:
        sid = self.store.create()
        turn = Turn(request="install nginx", intent="install_package", command="apt install nginx")
        self.store.add_turn(sid, turn)
        session = self.store.get(sid)
        assert session is not None
        assert len(session.turns) == 1
        assert session.turns[0].request == "install nginx"

    def test_timeout_expiry(self) -> None:
        store = SessionStore(timeout_seconds=0, max_turns=5)
        sid = store.create()
        time.sleep(0.01)
        store.cleanup_expired()
        assert store.get(sid) is None

    def test_size_limit_drops_oldest_turns(self) -> None:
        store = SessionStore(timeout_seconds=60, max_turns=3)
        sid = store.create()
        for i in range(5):
            store.add_turn(sid, Turn(request=f"cmd {i}", command=f"echo {i}"))
        session = store.get(sid)
        assert session is not None
        assert len(session.turns) == 3
        assert session.turns[0].request == "cmd 2"

    def test_context_updates(self) -> None:
        sid = self.store.create()
        self.store.update_context(sid, {"safe_mode": False})
        session = self.store.get(sid)
        assert session is not None
        assert session.context_updates == {"safe_mode": False}

    def test_multiple_sessions(self) -> None:
        sid1 = self.store.create()
        sid2 = self.store.create()
        assert sid1 != sid2
        assert self.store.get(sid1) is not None
        assert self.store.get(sid2) is not None


class TestMaxSessions:
    """Max session count enforcement (Story 8.3c)."""

    def test_create_within_limit(self) -> None:
        store = SessionStore(timeout_seconds=60, max_turns=5, max_sessions=5)
        for _ in range(5):
            store.create()
        # All 5 should exist
        assert len(store._sessions) == 5

    def test_create_over_limit_raises(self) -> None:
        store = SessionStore(timeout_seconds=60, max_turns=5, max_sessions=3)
        for _ in range(3):
            store.create()
        with pytest.raises(SessionLimitError):
            store.create()

    def test_expired_freed_before_limit_check(self) -> None:
        store = SessionStore(timeout_seconds=0, max_turns=5, max_sessions=3)
        for _ in range(3):
            store.create()
        # All sessions immediately expired (timeout=0)
        time.sleep(0.01)
        # This should succeed because expired sessions are cleaned first
        sid = store.create()
        assert store.get(sid) is not None

    def test_max_sessions_zero_unlimited(self) -> None:
        store = SessionStore(timeout_seconds=60, max_turns=5, max_sessions=0)
        for _ in range(100):
            store.create()
        assert len(store._sessions) == 100

    def test_limit_enforced_after_cleanup_still_full(self) -> None:
        store = SessionStore(timeout_seconds=3600, max_turns=5, max_sessions=2)
        store.create()
        store.create()
        # No expired sessions to clean up, so should still raise
        with pytest.raises(SessionLimitError):
            store.create()

    def test_create_succeeds_after_manual_cleanup(self) -> None:
        store = SessionStore(timeout_seconds=0, max_turns=5, max_sessions=2)
        store.create()
        store.create()
        time.sleep(0.01)
        store.cleanup_expired()
        # Now there's room
        sid = store.create()
        assert store.get(sid) is not None

    def test_default_max_sessions_is_1000(self) -> None:
        store = SessionStore()
        assert store.max_sessions == 1000

    def test_session_limit_error_is_exception(self) -> None:
        assert issubclass(SessionLimitError, Exception)

    def test_session_limit_error_message(self) -> None:
        store = SessionStore(timeout_seconds=60, max_turns=5, max_sessions=1)
        store.create()
        try:
            store.create()
            pytest.fail("Expected SessionLimitError")
        except SessionLimitError as exc:
            assert "limit" in str(exc).lower() or "max" in str(exc).lower()

    def test_max_sessions_config_propagated(self) -> None:
        store = SessionStore(max_sessions=42)
        assert store.max_sessions == 42


class TestSessionModels:
    """Turn and Session field validation."""

    def test_turn_defaults(self) -> None:
        turn = Turn(request="hello")
        assert turn.request == "hello"
        assert turn.intent == ""
        assert turn.command == ""
        assert turn.outcome == ""
        assert turn.subject == ""

    def test_turn_with_all_fields(self) -> None:
        turn = Turn(
            request="start nginx",
            intent="start_service",
            command="systemctl start nginx",
            outcome="success",
            subject="nginx",
        )
        assert turn.subject == "nginx"

    def test_session_prev_line(self) -> None:
        session = Session(session_id="test")
        assert session.prev_line() is None
        session.turns.append(
            Turn(request="install nginx", command="apt install nginx", subject="nginx")
        )
        assert session.prev_line() == "nginx"

    def test_session_created_at(self) -> None:
        session = Session(session_id="test")
        assert session.created_at > 0
        assert session.last_active > 0
