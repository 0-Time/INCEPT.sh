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
    """--explain CLI flag triggers explain pipeline."""

    def test_explain_flag_basic(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--explain", "apt-get install nginx"])
        assert result.exit_code == 0
        assert "install" in result.output.lower()

    def test_explain_flag_includes_risk(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--explain", "apt-get install nginx"])
        assert result.exit_code == 0
        # Output should mention risk level
        lower = result.output.lower()
        assert "risk" in lower or "safe" in lower

    def test_explain_flag_unknown_command(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--explain", "frobnicator --quux"])
        assert result.exit_code == 0
        lower = result.output.lower()
        assert "unrecognized" in lower or "unknown" in lower
