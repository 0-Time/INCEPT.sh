"""Tests for error recovery pattern matching."""

from __future__ import annotations

from incept.recovery.patterns import ERROR_PATTERNS, classify_error


class TestErrorPatternRegistry:
    """Test that all 7 error patterns match expected error messages."""

    def test_apt_package_not_found(self) -> None:
        stderr = "E: Unable to locate package nonexistent-pkg"
        pattern, ctx = classify_error(stderr)
        assert pattern is not None
        assert pattern.name == "apt_package_not_found"
        assert ctx["package"] == "nonexistent-pkg"

    def test_dnf_package_not_found(self) -> None:
        stderr = "Error: No matching packages to list\nNo match for argument: missing-pkg"
        pattern, ctx = classify_error(stderr)
        assert pattern is not None
        assert pattern.name == "dnf_package_not_found"
        assert ctx["package"] == "missing-pkg"

    def test_permission_denied(self) -> None:
        stderr = "bash: /etc/shadow: Permission denied"
        pattern, ctx = classify_error(stderr)
        assert pattern is not None
        assert pattern.name == "permission_denied"
        assert ctx["path"] == "/etc/shadow"

    def test_command_not_found(self) -> None:
        stderr = "bash: htop: command not found"
        pattern, ctx = classify_error(stderr)
        assert pattern is not None
        assert pattern.name == "command_not_found"
        assert ctx["command"] == "htop"

    def test_no_such_file(self) -> None:
        stderr = "ls: cannot access '/missing/path': No such file or directory"
        pattern, ctx = classify_error(stderr)
        assert pattern is not None
        assert pattern.name == "no_such_file"
        assert ctx["path"] == "/missing/path"

    def test_disk_full(self) -> None:
        stderr = "write error: No space left on device"
        pattern, ctx = classify_error(stderr)
        assert pattern is not None
        assert pattern.name == "disk_full"

    def test_flag_not_recognized(self) -> None:
        stderr = "ls: unrecognized option '--colour'"
        pattern, ctx = classify_error(stderr)
        assert pattern is not None
        assert pattern.name == "flag_not_recognized"
        assert ctx["flag"] == "--colour"

    def test_unknown_error_returns_none(self) -> None:
        stderr = "some random gibberish error output"
        pattern, ctx = classify_error(stderr)
        assert pattern is None
        assert ctx == {}

    def test_empty_stderr_returns_none(self) -> None:
        pattern, ctx = classify_error("")
        assert pattern is None
        assert ctx == {}

    def test_registry_has_seven_patterns(self) -> None:
        assert len(ERROR_PATTERNS) == 7

    def test_all_patterns_have_names(self) -> None:
        names = {p.name for p in ERROR_PATTERNS}
        expected = {
            "apt_package_not_found",
            "dnf_package_not_found",
            "permission_denied",
            "command_not_found",
            "no_such_file",
            "disk_full",
            "flag_not_recognized",
        }
        assert names == expected

    def test_permission_denied_alternative_format(self) -> None:
        stderr = "cp: cannot create regular file '/root/test': Permission denied"
        pattern, ctx = classify_error(stderr)
        assert pattern is not None
        assert pattern.name == "permission_denied"

    def test_command_not_found_zsh_format(self) -> None:
        stderr = "zsh: command not found: docker"
        pattern, ctx = classify_error(stderr)
        assert pattern is not None
        assert pattern.name == "command_not_found"
        assert ctx["command"] == "docker"
