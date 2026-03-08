"""Tests for CLI main entry point dispatch."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from incept.cli.main import main


class TestCLIMain:
    """CLI entry point routing."""

    def test_version_flag(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_query_arg_oneshot(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["find log files"])
        assert result.exit_code == 0

    def test_minimal_flag_with_query(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--minimal", "find log files"])
        assert result.exit_code == 0

    @patch("incept.cli.main._run_repl")
    def test_no_args_launches_repl(self, mock_repl: MagicMock) -> None:
        runner = CliRunner()
        runner.invoke(main, [])
        mock_repl.assert_called_once()

    def test_serve_subcommand(self) -> None:
        from click.testing import CliRunner as _Runner

        runner = _Runner()
        # Verify serve is a registered subcommand on the CLI group
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "serve" in result.output.lower()
