"""Tests for shell plugin scripts and installer — Story 8.4."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from incept.cli.shell_plugin import (
    generate_bash_plugin,
    generate_zsh_plugin,
    install_plugin,
    uninstall_plugin,
)

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts" / "plugins"


# ===================================================================
# Bash script tests
# ===================================================================


class TestBashScript:
    """Tests for scripts/plugins/incept.bash."""

    def test_script_exists(self) -> None:
        assert (SCRIPTS_DIR / "incept.bash").is_file()

    def test_syntax_valid(self) -> None:
        result = subprocess.run(
            ["bash", "-n", str(SCRIPTS_DIR / "incept.bash")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_defines_widget_function(self) -> None:
        content = (SCRIPTS_DIR / "incept.bash").read_text()
        assert "_incept_widget" in content

    def test_binds_ctrl_i(self) -> None:
        content = (SCRIPTS_DIR / "incept.bash").read_text()
        assert "\\C-i" in content or "^I" in content

    def test_calls_incept_minimal(self) -> None:
        content = (SCRIPTS_DIR / "incept.bash").read_text()
        assert "incept" in content
        assert "--minimal" in content

    def test_reads_readline_line(self) -> None:
        content = (SCRIPTS_DIR / "incept.bash").read_text()
        assert "READLINE_LINE" in content

    def test_handles_empty_input(self) -> None:
        content = (SCRIPTS_DIR / "incept.bash").read_text()
        # Should check for empty input before calling incept
        assert "READLINE_LINE" in content
        # Verify there's a guard for empty input
        assert "-z" in content or "-n" in content or '""' in content


# ===================================================================
# Zsh script tests
# ===================================================================


class TestZshScript:
    """Tests for scripts/plugins/incept.zsh."""

    def test_script_exists(self) -> None:
        assert (SCRIPTS_DIR / "incept.zsh").is_file()

    def test_syntax_valid(self) -> None:
        result = subprocess.run(
            ["zsh", "-n", str(SCRIPTS_DIR / "incept.zsh")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_defines_zle_widget(self) -> None:
        content = (SCRIPTS_DIR / "incept.zsh").read_text()
        assert "incept-widget" in content

    def test_registers_zle_widget(self) -> None:
        content = (SCRIPTS_DIR / "incept.zsh").read_text()
        assert "zle -N" in content

    def test_binds_ctrl_i(self) -> None:
        content = (SCRIPTS_DIR / "incept.zsh").read_text()
        assert "'^I'" in content or "\\C-i" in content or "^I" in content

    def test_calls_incept_minimal(self) -> None:
        content = (SCRIPTS_DIR / "incept.zsh").read_text()
        assert "incept" in content
        assert "--minimal" in content

    def test_reads_buffer(self) -> None:
        content = (SCRIPTS_DIR / "incept.zsh").read_text()
        assert "BUFFER" in content

    def test_handles_empty_input(self) -> None:
        content = (SCRIPTS_DIR / "incept.zsh").read_text()
        # Should check for empty buffer before calling incept
        assert "BUFFER" in content
        assert "-z" in content or "-n" in content or '""' in content


# ===================================================================
# Generator tests
# ===================================================================


class TestGenerators:
    """Tests for generate_bash_plugin / generate_zsh_plugin."""

    def test_generate_bash_returns_string(self) -> None:
        result = generate_bash_plugin()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_bash_contains_function(self) -> None:
        result = generate_bash_plugin()
        assert "_incept_widget" in result

    def test_generate_zsh_returns_string(self) -> None:
        result = generate_zsh_plugin()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_zsh_contains_widget(self) -> None:
        result = generate_zsh_plugin()
        assert "incept-widget" in result


# ===================================================================
# Installer tests
# ===================================================================


class TestInstaller:
    """Tests for install_plugin / uninstall_plugin."""

    def test_install_bash_creates_source_line(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False) as f:
            f.write("# existing config\n")
            rc_path = f.name
        try:
            install_plugin("bash", rc_path=rc_path)
            content = Path(rc_path).read_text()
            assert "source" in content or "." in content
            assert "incept.bash" in content
        finally:
            os.unlink(rc_path)

    def test_install_zsh_creates_source_line(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".zshrc", delete=False) as f:
            f.write("# existing config\n")
            rc_path = f.name
        try:
            install_plugin("zsh", rc_path=rc_path)
            content = Path(rc_path).read_text()
            assert "source" in content or "." in content
            assert "incept.zsh" in content
        finally:
            os.unlink(rc_path)

    def test_install_idempotent(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False) as f:
            f.write("# existing config\n")
            rc_path = f.name
        try:
            install_plugin("bash", rc_path=rc_path)
            install_plugin("bash", rc_path=rc_path)
            content = Path(rc_path).read_text()
            # Should only appear once
            assert content.count("incept.bash") == 1
        finally:
            os.unlink(rc_path)

    def test_uninstall_removes_source_line(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False) as f:
            f.write("# existing config\n")
            rc_path = f.name
        try:
            install_plugin("bash", rc_path=rc_path)
            uninstall_plugin("bash", rc_path=rc_path)
            content = Path(rc_path).read_text()
            assert "incept.bash" not in content
            # Original content preserved
            assert "# existing config" in content
        finally:
            os.unlink(rc_path)

    def test_uninstall_noop_when_not_installed(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False) as f:
            f.write("# existing config\n")
            rc_path = f.name
        try:
            uninstall_plugin("bash", rc_path=rc_path)
            content = Path(rc_path).read_text()
            assert content == "# existing config\n"
        finally:
            os.unlink(rc_path)

    def test_install_creates_rc_if_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rc_path = os.path.join(tmpdir, ".bashrc")
            install_plugin("bash", rc_path=rc_path)
            assert Path(rc_path).is_file()
            content = Path(rc_path).read_text()
            assert "incept.bash" in content

    def test_invalid_shell_raises(self) -> None:
        with pytest.raises(ValueError, match="shell"):
            install_plugin("fish", rc_path="/tmp/test_rc")

    def test_uninstall_invalid_shell_raises(self) -> None:
        with pytest.raises(ValueError, match="shell"):
            uninstall_plugin("fish", rc_path="/tmp/test_rc")


# ===================================================================
# Shell auto-detection
# ===================================================================


class TestShellDetection:
    """Tests for shell type auto-detection."""

    def test_detect_from_shell_env(self) -> None:
        from incept.cli.shell_plugin import detect_shell

        # We're on zsh per the environment
        detected = detect_shell()
        assert detected in ("bash", "zsh")
