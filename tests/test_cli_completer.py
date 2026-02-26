"""Tests for tab completion."""

from __future__ import annotations

from incept.cli.completer import SlashCompleter


class TestSlashCompleter:
    """Tab completion for slash commands."""

    def setup_method(self) -> None:
        self.completer = SlashCompleter()

    def test_slash_commands_complete(self) -> None:
        completions = list(self.completer.get_completions_for("/"))
        assert len(completions) > 0

    def test_partial_match(self) -> None:
        completions = list(self.completer.get_completions_for("/he"))
        names = [c.text for c in completions]
        assert "/help" in names

    def test_no_match(self) -> None:
        completions = list(self.completer.get_completions_for("/zzz"))
        assert len(completions) == 0

    def test_full_match(self) -> None:
        completions = list(self.completer.get_completions_for("/help"))
        names = [c.text for c in completions]
        assert "/help" in names

    def test_non_slash_no_completions(self) -> None:
        completions = list(self.completer.get_completions_for("find"))
        assert len(completions) == 0
