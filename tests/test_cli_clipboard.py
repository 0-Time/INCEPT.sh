"""Tests for clipboard detection and copy."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from incept.cli.clipboard import copy_text, detect_clipboard_tool


class TestClipboard:
    """Cross-platform clipboard tests."""

    @patch("shutil.which")
    def test_detect_pbcopy_macos(self, mock_which: MagicMock) -> None:
        mock_which.side_effect = lambda cmd: "/usr/bin/pbcopy" if cmd == "pbcopy" else None
        tool = detect_clipboard_tool()
        assert tool == "pbcopy"

    @patch("shutil.which")
    def test_detect_xclip_linux(self, mock_which: MagicMock) -> None:
        def side_effect(cmd: str) -> str | None:
            if cmd == "pbcopy":
                return None
            if cmd == "xclip":
                return "/usr/bin/xclip"
            return None

        mock_which.side_effect = side_effect
        tool = detect_clipboard_tool()
        assert tool == "xclip"

    @patch("shutil.which")
    def test_detect_xsel_fallback(self, mock_which: MagicMock) -> None:
        def side_effect(cmd: str) -> str | None:
            if cmd == "xsel":
                return "/usr/bin/xsel"
            return None

        mock_which.side_effect = side_effect
        tool = detect_clipboard_tool()
        assert tool == "xsel"

    @patch("shutil.which")
    def test_no_tool_available(self, mock_which: MagicMock) -> None:
        mock_which.return_value = None
        tool = detect_clipboard_tool()
        assert tool is None

    @patch("subprocess.run")
    @patch("incept.cli.clipboard.detect_clipboard_tool")
    def test_copy_text_success(self, mock_detect: MagicMock, mock_run: MagicMock) -> None:
        mock_detect.return_value = "pbcopy"
        mock_run.return_value = MagicMock(returncode=0)
        result = copy_text("echo hello")
        assert result is True

    @patch("incept.cli.clipboard.detect_clipboard_tool")
    def test_copy_text_no_tool(self, mock_detect: MagicMock) -> None:
        mock_detect.return_value = None
        result = copy_text("echo hello")
        assert result is False
