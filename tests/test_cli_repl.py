"""Tests for interactive REPL."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from incept.cli.config import InceptConfig
from incept.cli.repl import InceptREPL


class TestInceptREPL:
    """REPL behavior tests."""

    def setup_method(self) -> None:
        self.config = InceptConfig()
        self.repl = InceptREPL(self.config)

    def test_welcome_banner_on_start(self) -> None:
        banner = self.repl.get_welcome_banner()
        assert "incept" in banner.lower() or "INCEPT" in banner

    def test_prompt_text_normal(self) -> None:
        prompt = self.repl.get_prompt()
        assert prompt == "incept> "

    def test_prompt_text_safe_mode(self) -> None:
        config = InceptConfig(safe_mode=True, prompt="incept [safe]> ")
        repl = InceptREPL(config)
        assert "safe" in repl.get_prompt().lower()

    def test_empty_input_continues(self) -> None:
        result = self.repl.handle_input("")
        assert result is None  # No action

    def test_slash_command_dispatched(self) -> None:
        result = self.repl.handle_input("/help")
        assert result is not None
        assert isinstance(result, str)

    def test_nl_request_calls_pipeline(self) -> None:
        with patch("incept.cli.repl.run_pipeline") as mock_pipeline:
            mock_pipeline.return_value = MagicMock(
                status="success",
                responses=[],
                model_dump=lambda: {"status": "success", "responses": []},
            )
            self.repl.handle_input("find log files")
            mock_pipeline.assert_called_once()

    def test_exit_command(self) -> None:
        result = self.repl.handle_input("/exit")
        assert result == "__exit__"

    def test_quit_command(self) -> None:
        result = self.repl.handle_input("/quit")
        assert result == "__exit__"

    def test_unknown_slash_command(self) -> None:
        result = self.repl.handle_input("/nonexistent")
        assert result is not None
        assert "unknown" in result.lower()

    def test_history_command(self) -> None:
        self.repl.handle_input("find log files")
        result = self.repl.handle_input("/history")
        assert result is not None
