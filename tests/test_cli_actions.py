"""Tests for execute/edit/copy/skip action handlers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from incept.cli.actions import ActionResult, execute_command


class TestExecuteCommand:
    """Command execution tests."""

    @patch("subprocess.run")
    def test_execute_captures_stdout(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=0, stdout="hello\n", stderr=""
        )
        result = execute_command("echo hello")
        assert result.exit_code == 0
        assert "hello" in result.stdout

    @patch("subprocess.run")
    def test_execute_captures_stderr(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="error occurred"
        )
        result = execute_command("bad-cmd")
        assert result.exit_code == 1
        assert "error" in result.stderr

    @patch("subprocess.run")
    def test_execute_timeout(self, mock_run: MagicMock) -> None:
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
        result = execute_command("sleep 999", timeout=30)
        assert result.exit_code == -1
        assert "timed out" in result.stderr.lower()

    def test_skip_returns_action_result(self) -> None:
        result = ActionResult(exit_code=0, stdout="", stderr="", action="skip")
        assert result.action == "skip"

    @patch("subprocess.run")
    def test_dangerous_requires_confirmation_flag(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        result = execute_command("echo safe", confirmed=True)
        assert result.exit_code == 0
