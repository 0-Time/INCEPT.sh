"""Command execution and action handlers."""

from __future__ import annotations

import subprocess

from pydantic import BaseModel


class ActionResult(BaseModel):
    """Result of executing a command or action."""

    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    action: str = "execute"


def execute_command(
    command: str,
    *,
    timeout: int = 120,
    confirmed: bool = False,
) -> ActionResult:
    """Execute a shell command and capture output.

    Args:
        command: Shell command to execute.
        timeout: Timeout in seconds.
        confirmed: Whether dangerous command was explicitly confirmed.

    Returns:
        ActionResult with exit code, stdout, stderr.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return ActionResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            action="execute",
        )
    except subprocess.TimeoutExpired:
        return ActionResult(
            exit_code=-1,
            stdout="",
            stderr=f"Command timed out after {timeout} seconds",
            action="execute",
        )
