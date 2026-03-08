"""Tests for CLI /explain and --explain flag."""

from __future__ import annotations

from click.testing import CliRunner

from incept.cli.commands import SlashCommandRegistry
from incept.cli.main import main


class TestExplainSlashCommand:
    """The /explain slash command is registered and callable."""

    def test_explain_registered(self) -> None:
        registry = SlashCommandRegistry()
        assert registry.has("/explain")

    def test_explain_dispatch(self) -> None:
        registry = SlashCommandRegistry()
        result = registry.dispatch("/explain", "apt-get install nginx")
        assert "install" in result.lower()

    def test_explain_empty_args(self) -> None:
        registry = SlashCommandRegistry()
        result = registry.dispatch("/explain", "")
        assert result  # Should return help or error message


class TestExplainCliFlag:
    """v2 removed the --explain CLI flag (model handles explanations natively).

    These tests verify the flag is no longer accepted.
    """

    def test_explain_flag_removed(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--explain", "apt-get install nginx"])
        # --explain is no longer a valid option
        assert result.exit_code != 0
