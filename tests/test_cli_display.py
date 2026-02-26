"""Tests for Rich output formatting."""

from __future__ import annotations

from incept.cli.display import DisplayManager
from incept.safety.validator import RiskLevel


class TestDisplayManager:
    """Rich-based output formatting tests."""

    def setup_method(self) -> None:
        self.dm = DisplayManager(color=True)
        self.dm_nocolor = DisplayManager(color=False)

    def test_format_safe_command(self) -> None:
        output = self.dm.format_command("ls -la", RiskLevel.SAFE)
        assert "ls -la" in output

    def test_format_caution_command(self) -> None:
        output = self.dm.format_command("sudo apt install nginx", RiskLevel.CAUTION)
        assert "sudo apt install nginx" in output

    def test_format_dangerous_command(self) -> None:
        output = self.dm.format_command("sudo rm -rf /var/log", RiskLevel.DANGEROUS)
        assert "sudo rm -rf /var/log" in output

    def test_format_blocked_command(self) -> None:
        output = self.dm.format_command("rm -rf /", RiskLevel.BLOCKED)
        assert "BLOCKED" in output.upper() or "rm -rf /" in output

    def test_format_clarification(self) -> None:
        output = self.dm.format_clarification("What file do you want to find?", ["*.log", "*.txt"])
        assert "What file do you want to find?" in output

    def test_format_multi_step(self) -> None:
        steps = ["apt update", "apt install nginx"]
        output = self.dm.format_multi_step(steps)
        assert "apt update" in output
        assert "apt install nginx" in output

    def test_format_error_recovery(self) -> None:
        output = self.dm.format_recovery("sudo cat /etc/shadow", "Retrying with sudo.")
        assert "sudo cat /etc/shadow" in output

    def test_no_color_mode(self) -> None:
        output = self.dm_nocolor.format_command("ls", RiskLevel.SAFE)
        assert "ls" in output

    def test_welcome_banner(self) -> None:
        banner = self.dm.welcome_banner()
        assert "INCEPT" in banner.upper() or "incept" in banner.lower()

    def test_action_prompt(self) -> None:
        prompt = self.dm.action_prompt()
        assert len(prompt) > 0
