"""Tests for one-shot CLI mode."""

from __future__ import annotations

from click.testing import CliRunner

from incept.cli.main import main


class TestOneShotMode:
    """CLI one-shot mode: incept "query"."""

    def test_returns_command(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["find all log files"])
        assert result.exit_code == 0

    def test_minimal_flag(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--minimal", "find all log files"])
        assert result.exit_code == 0

    def test_exits_after(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["list directory contents"])
        assert result.exit_code == 0

    def test_version_flag(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
