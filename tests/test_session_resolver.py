"""Tests for cross-turn reference resolution."""

from __future__ import annotations

from incept.session.models import Session, Turn
from incept.session.resolver import resolve_references


class TestReferenceResolution:
    """Resolve pronouns and references using session history."""

    def _session_with_turns(self, *turns: Turn) -> Session:
        s = Session(session_id="test")
        s.turns.extend(turns)
        return s

    def test_it_resolves_to_last_subject(self) -> None:
        session = self._session_with_turns(
            Turn(request="install nginx", command="apt install nginx", subject="nginx"),
        )
        result = resolve_references("start it", session)
        assert "nginx" in result
        assert "it" not in result.lower().split()

    def test_them_resolves_to_last_subject(self) -> None:
        session = self._session_with_turns(
            Turn(
                request="find log files",
                command="find /var/log -name '*.log'",
                subject="log files",
            ),
        )
        result = resolve_references("delete them", session)
        assert "log files" in result

    def test_that_service_resolves(self) -> None:
        session = self._session_with_turns(
            Turn(request="start nginx", command="systemctl start nginx", subject="nginx"),
        )
        result = resolve_references("stop that service", session)
        assert "nginx" in result

    def test_no_reference_no_change(self) -> None:
        session = self._session_with_turns(
            Turn(request="install nginx", command="apt install nginx", subject="nginx"),
        )
        result = resolve_references("install apache2", session)
        assert result == "install apache2"

    def test_no_previous_turn_no_resolution(self) -> None:
        session = Session(session_id="test")
        result = resolve_references("start it", session)
        assert result == "start it"

    def test_install_then_start(self) -> None:
        session = self._session_with_turns(
            Turn(request="install nginx", command="apt install nginx", subject="nginx"),
        )
        result = resolve_references("start it", session)
        assert "nginx" in result

    def test_ambiguous_kept_when_no_subject(self) -> None:
        session = self._session_with_turns(
            Turn(request="list processes", command="ps aux", subject=""),
        )
        result = resolve_references("kill it", session)
        # No subject to resolve — keep original
        assert result == "kill it"

    def test_multiple_turns_uses_most_recent(self) -> None:
        session = self._session_with_turns(
            Turn(request="install nginx", command="apt install nginx", subject="nginx"),
            Turn(request="install redis", command="apt install redis", subject="redis"),
        )
        result = resolve_references("start it", session)
        assert "redis" in result
        assert "nginx" not in result

    def test_the_file_resolves(self) -> None:
        session = self._session_with_turns(
            Turn(
                request="view config.yaml",
                command="cat config.yaml",
                subject="config.yaml",
            ),
        )
        result = resolve_references("edit the file", session)
        assert "config.yaml" in result

    def test_empty_text_returns_empty(self) -> None:
        session = self._session_with_turns(
            Turn(request="install nginx", command="apt install nginx", subject="nginx"),
        )
        result = resolve_references("", session)
        assert result == ""
