"""Recovery engine: suggests fixes for failed commands."""

from __future__ import annotations

import re

from pydantic import BaseModel

from incept.recovery.patterns import classify_error

# Commands that should never be auto-retried
_DESTRUCTIVE_PATTERNS = re.compile(r"\brm\b|\bdd\b|\bmkfs\b|\bformat\b")


class RecoveryResult(BaseModel):
    """Result of a recovery suggestion."""

    recovery_command: str = ""
    explanation: str = ""
    can_auto_retry: bool = False
    attempt_number: int = 1
    gave_up: bool = False


class RecoveryEngine:
    """Suggests recovery actions for failed commands.

    Args:
        max_retries: Maximum number of recovery attempts before giving up.
    """

    def __init__(self, max_retries: int = 3) -> None:
        self.max_retries = max_retries

    def suggest_recovery(
        self,
        original_command: str,
        stderr: str,
        *,
        allow_sudo: bool = True,
        attempt: int = 1,
    ) -> RecoveryResult:
        """Suggest a recovery action for a failed command.

        Args:
            original_command: The command that failed.
            stderr: The stderr output from the failed command.
            allow_sudo: Whether sudo is permitted.
            attempt: Current attempt number (1-based).

        Returns:
            RecoveryResult with suggested fix.
        """
        if attempt > self.max_retries:
            return RecoveryResult(
                recovery_command="",
                explanation=(
                    f"Recovery failed after {self.max_retries} attempts. "
                    "Please investigate manually or consult documentation."
                ),
                can_auto_retry=False,
                attempt_number=attempt,
                gave_up=True,
            )

        is_destructive = bool(_DESTRUCTIVE_PATTERNS.search(original_command))
        pattern, ctx = classify_error(stderr)

        if pattern is None:
            return RecoveryResult(
                recovery_command="",
                explanation="Unrecognized error. No automatic recovery available.",
                can_auto_retry=False,
                attempt_number=attempt,
                gave_up=False,
            )

        recovery_command, explanation, can_retry = self._build_recovery(
            pattern.name, original_command, ctx, allow_sudo=allow_sudo
        )

        if is_destructive:
            can_retry = False

        return RecoveryResult(
            recovery_command=recovery_command,
            explanation=explanation,
            can_auto_retry=can_retry,
            attempt_number=attempt,
            gave_up=False,
        )

    def _build_recovery(
        self,
        pattern_name: str,
        original_command: str,
        ctx: dict[str, str],
        *,
        allow_sudo: bool = True,
    ) -> tuple[str, str, bool]:
        """Build recovery command, explanation, and auto-retry flag."""
        if pattern_name == "apt_package_not_found":
            pkg = ctx.get("package", "")
            msg = (
                f"Package '{pkg}' not found. "
                "Updating package lists and searching for similar packages."
            )
            return (
                f"sudo apt update && apt-cache search {pkg}",
                msg,
                False,
            )

        if pattern_name == "dnf_package_not_found":
            pkg = ctx.get("package", "")
            return (
                f"dnf search {pkg}",
                f"Package '{pkg}' not found. Searching for similar packages.",
                False,
            )

        if pattern_name == "permission_denied":
            if allow_sudo:
                return (
                    f"sudo {original_command}",
                    "Permission denied. Retrying with sudo.",
                    True,
                )
            msg = (
                "Permission denied. Sudo is not allowed. "
                "Check file permissions or run as appropriate user."
            )
            return (original_command, msg, False)

        if pattern_name == "command_not_found":
            cmd = ctx.get("command", "")
            return (
                f"sudo apt install {cmd}",
                f"Command '{cmd}' not found. Attempting to install it.",
                False,
            )

        if pattern_name == "no_such_file":
            path = ctx.get("path", "")
            parent = "/".join(path.rstrip("/").split("/")[:-1]) or "/"
            basename = path.split("/")[-1]
            find_cmd = (
                f"find {parent} -maxdepth 2 -name '*{basename}*'"
                f" 2>/dev/null || ls {parent}"
            )
            msg = (
                f"Path '{path}' does not exist. "
                "Searching for similar files in parent directory."
            )
            return (find_cmd, msg, False)

        if pattern_name == "disk_full":
            return (
                "df -h && du -sh /tmp/* 2>/dev/null | sort -rh | head -10",
                "Disk is full. Checking disk usage to identify large files.",
                False,
            )

        if pattern_name == "flag_not_recognized":
            flag = ctx.get("flag", "")
            base_cmd = original_command.split()[0] if original_command.split() else ""
            cleaned = original_command.replace(flag, "").strip()
            return (
                cleaned,
                f"Flag '{flag}' is not recognized by '{base_cmd}'. Removed the invalid flag.",
                True,
            )

        return ("", "No recovery strategy available.", False)
