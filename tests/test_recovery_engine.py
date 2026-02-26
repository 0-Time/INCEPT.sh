"""Tests for error recovery engine."""

from __future__ import annotations

from incept.recovery.engine import RecoveryEngine, RecoveryResult


class TestRecoveryStrategies:
    """Each error type produces the correct recovery suggestion."""

    def setup_method(self) -> None:
        self.engine = RecoveryEngine(max_retries=3)

    def test_apt_recovery_suggests_update(self) -> None:
        result = self.engine.suggest_recovery(
            "apt install nonexistent-pkg",
            "E: Unable to locate package nonexistent-pkg",
        )
        assert result is not None
        cmd = result.recovery_command
        assert "apt update" in cmd or "apt-cache search" in cmd
        assert result.explanation

    def test_dnf_recovery_suggests_search(self) -> None:
        result = self.engine.suggest_recovery(
            "dnf install missing-pkg",
            "No match for argument: missing-pkg",
        )
        assert result is not None
        assert "dnf search" in result.recovery_command or "search" in result.recovery_command
        assert result.explanation

    def test_permission_denied_suggests_sudo(self) -> None:
        result = self.engine.suggest_recovery(
            "cat /etc/shadow",
            "bash: /etc/shadow: Permission denied",
        )
        assert result is not None
        assert "sudo" in result.recovery_command
        assert result.can_auto_retry

    def test_permission_denied_no_sudo_when_disallowed(self) -> None:
        result = self.engine.suggest_recovery(
            "cat /etc/shadow",
            "bash: /etc/shadow: Permission denied",
            allow_sudo=False,
        )
        assert result is not None
        assert "sudo" not in result.recovery_command

    def test_command_not_found_suggests_install(self) -> None:
        result = self.engine.suggest_recovery(
            "htop",
            "bash: htop: command not found",
        )
        assert result is not None
        assert "install" in result.recovery_command.lower() or "apt" in result.recovery_command
        assert result.explanation

    def test_no_such_file_suggests_find(self) -> None:
        result = self.engine.suggest_recovery(
            "ls /missing/path",
            "ls: cannot access '/missing/path': No such file or directory",
        )
        assert result is not None
        assert "find" in result.recovery_command or "ls" in result.recovery_command
        assert result.explanation

    def test_disk_full_suggests_df_du(self) -> None:
        result = self.engine.suggest_recovery(
            "cp large.iso /tmp/",
            "write error: No space left on device",
        )
        assert result is not None
        assert "df" in result.recovery_command or "du" in result.recovery_command

    def test_flag_suggests_alternative(self) -> None:
        result = self.engine.suggest_recovery(
            "ls --colour",
            "ls: unrecognized option '--colour'",
        )
        assert result is not None
        assert result.explanation
        assert result.recovery_command

    def test_unknown_error_returns_generic(self) -> None:
        result = self.engine.suggest_recovery(
            "some-cmd",
            "weird unknown error",
        )
        assert result is not None
        assert result.recovery_command == ""
        assert not result.can_auto_retry


class TestRetryLimiter:
    """Retry tracking respects max_retries."""

    def setup_method(self) -> None:
        self.engine = RecoveryEngine(max_retries=3)

    def test_allows_up_to_max_retries(self) -> None:
        stderr = "bash: /etc/shadow: Permission denied"
        cmd = "cat /etc/shadow"
        for i in range(3):
            result = self.engine.suggest_recovery(cmd, stderr, attempt=i + 1)
            assert result is not None
            assert not result.gave_up
            assert result.attempt_number == i + 1

    def test_blocks_fourth_retry(self) -> None:
        result = self.engine.suggest_recovery(
            "cat /etc/shadow",
            "bash: /etc/shadow: Permission denied",
            attempt=4,
        )
        assert result is not None
        assert result.gave_up
        assert result.attempt_number == 4

    def test_gave_up_message_suggests_docs(self) -> None:
        result = self.engine.suggest_recovery(
            "cat /etc/shadow",
            "bash: /etc/shadow: Permission denied",
            attempt=4,
        )
        assert result is not None
        assert result.gave_up
        expl = result.explanation.lower()
        assert "manual" in expl or "documentation" in expl or "investigate" in expl


class TestDestructiveGuard:
    """Destructive commands should not be auto-retried."""

    def setup_method(self) -> None:
        self.engine = RecoveryEngine(max_retries=3)

    def test_rm_not_auto_retried(self) -> None:
        result = self.engine.suggest_recovery(
            "rm -rf /tmp/data",
            "bash: /tmp/data: Permission denied",
        )
        assert result is not None
        assert not result.can_auto_retry

    def test_dd_not_auto_retried(self) -> None:
        result = self.engine.suggest_recovery(
            "dd if=/dev/zero of=/dev/sda",
            "Permission denied",
        )
        assert result is not None
        assert not result.can_auto_retry

    def test_mkfs_not_auto_retried(self) -> None:
        result = self.engine.suggest_recovery(
            "mkfs.ext4 /dev/sda1",
            "Permission denied",
        )
        assert result is not None
        assert not result.can_auto_retry

    def test_safe_command_can_auto_retry(self) -> None:
        result = self.engine.suggest_recovery(
            "cat /etc/shadow",
            "bash: /etc/shadow: Permission denied",
        )
        assert result is not None
        assert result.can_auto_retry


class TestRecoveryExplanation:
    """Each recovery includes a meaningful explanation."""

    def setup_method(self) -> None:
        self.engine = RecoveryEngine(max_retries=3)

    def test_recovery_has_explanation(self) -> None:
        result = self.engine.suggest_recovery(
            "apt install foo",
            "E: Unable to locate package foo",
        )
        assert result is not None
        assert len(result.explanation) > 10

    def test_recovery_result_fields(self) -> None:
        result = self.engine.suggest_recovery(
            "cat /etc/shadow",
            "bash: /etc/shadow: Permission denied",
        )
        assert isinstance(result, RecoveryResult)
        assert isinstance(result.recovery_command, str)
        assert isinstance(result.explanation, str)
        assert isinstance(result.can_auto_retry, bool)
        assert isinstance(result.attempt_number, int)
        assert isinstance(result.gave_up, bool)
