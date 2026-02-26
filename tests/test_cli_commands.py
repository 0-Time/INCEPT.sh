"""Tests for slash command registry."""

from __future__ import annotations

from incept.cli.commands import SlashCommandRegistry


class TestSlashCommands:
    """All slash commands are registered and dispatch correctly."""

    def setup_method(self) -> None:
        self.registry = SlashCommandRegistry()

    def test_help_registered(self) -> None:
        assert self.registry.has("/help")

    def test_context_registered(self) -> None:
        assert self.registry.has("/context")

    def test_safe_on_registered(self) -> None:
        assert self.registry.has("/safe")

    def test_verbose_registered(self) -> None:
        assert self.registry.has("/verbose")

    def test_history_registered(self) -> None:
        assert self.registry.has("/history")

    def test_clear_registered(self) -> None:
        assert self.registry.has("/clear")

    def test_exit_registered(self) -> None:
        assert self.registry.has("/exit")

    def test_quit_registered(self) -> None:
        assert self.registry.has("/quit")

    def test_unknown_command(self) -> None:
        assert not self.registry.has("/nonexistent")

    def test_dispatch_returns_result(self) -> None:
        result = self.registry.dispatch("/help", "")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_all_commands(self) -> None:
        commands = self.registry.get_command_names()
        assert "/help" in commands
        assert "/exit" in commands
        assert len(commands) >= 8
