"""Tests for context snapshot script execution."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from incept.core.context import (
    CONTEXT_SNAPSHOT_SCRIPT,
    EnvironmentContext,
    run_context_snapshot,
)


class TestContextScript:
    """Context snapshot bash script and Python wrapper."""

    def test_script_produces_valid_json_template(self) -> None:
        # The script itself is a template; verify it contains JSON structure
        assert '"distro_id"' in CONTEXT_SNAPSHOT_SCRIPT
        assert '"user"' in CONTEXT_SNAPSHOT_SCRIPT
        assert '"cwd"' in CONTEXT_SNAPSHOT_SCRIPT

    @patch("subprocess.run")
    def test_wrapper_returns_environment_context(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "distro_id": "ubuntu",
                "distro_version": "22.04",
                "distro_family": "debian",
                "kernel_version": "5.15.0",
                "shell": "bash",
                "shell_version": "5.1",
                "coreutils_version": "8.32",
                "user": "testuser",
                "is_root": False,
                "cwd": "/home/testuser",
            }),
        )
        ctx = run_context_snapshot()
        assert isinstance(ctx, EnvironmentContext)
        assert ctx.distro_id == "ubuntu"
        assert ctx.user == "testuser"

    @patch("subprocess.run")
    def test_handles_missing_os_release(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "distro_id": "unknown",
                "user": "root",
                "is_root": True,
                "cwd": "/root",
            }),
        )
        ctx = run_context_snapshot()
        assert ctx.distro_id == "unknown"

    @patch("subprocess.run")
    def test_handles_script_failure(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        ctx = run_context_snapshot()
        # Should return defaults on failure
        assert isinstance(ctx, EnvironmentContext)
        assert ctx.distro_id == "debian"  # default

    @patch("subprocess.run")
    def test_handles_invalid_json(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="not json")
        ctx = run_context_snapshot()
        assert isinstance(ctx, EnvironmentContext)
