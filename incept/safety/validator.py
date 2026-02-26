"""Command validator: syntax checking, banned patterns, risk classification, sudo audit."""

from __future__ import annotations

import re
from enum import StrEnum

from pydantic import BaseModel, Field

from incept.core.context import EnvironmentContext

# fmt: off
# ── Banned pattern registry (from spec Section 8.3) ──────────────────────────

_BANNED_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Fork bombs
    (re.compile(r":\(\)\{.*:\|:"), "fork bomb"),
    (re.compile(r"\.\(\)\{.*\.\|\.\}"), "fork bomb variant"),
    # Destructive rm
    (re.compile(r"\brm\s+(-\w*r\w*f|-\w*f\w*r)\s+/(\s|$)"), "rm -rf /"),
    (re.compile(r"\brm\s+(-\w*r\w*f|-\w*f\w*r)\s+/\*"), "rm -rf /*"),
    (re.compile(r"\brm\s+--no-preserve-root"), "rm --no-preserve-root"),
    # dd to disk devices
    (re.compile(r"\bdd\b.*of=/dev/[sh]d[a-z]"), "dd to disk device"),
    (re.compile(r"\bdd\b.*of=/dev/nvme"), "dd to nvme device"),
    # Pipe to shell (curl/wget piped to bash/sh)
    (re.compile(r"\bcurl\b.*\|\s*(ba)?sh\b"), "pipe curl to shell"),
    (re.compile(r"\bwget\b.*\|\s*(ba)?sh\b"), "pipe wget to shell"),
    (re.compile(r"\bcurl\b.*\|\s*sudo\s+(ba)?sh\b"), "pipe curl to sudo shell"),
    # mkfs on system devices
    (re.compile(r"\bmkfs\S*\s.*/dev/[sh]d[a-z]"), "mkfs on disk device"),
    (re.compile(r"\bmkfs\S*\s.*/dev/nvme"), "mkfs on nvme device"),
    # Dangerous chmod on system dirs
    (re.compile(r"\bchmod\s+(-R\s+)?777\s+/($|\s)"), "chmod 777 /"),
    (re.compile(r"\bchmod\s+(-R\s+)?777\s+/(etc|usr|bin|sbin|boot|dev)"), "chmod 777 on system dir"),
    # Dangerous chown on system dirs
    (re.compile(r"\bchown\s+(-R\s+)?.*\s+/($|\s)"), "chown on /"),
    # Shutdown/reboot
    (re.compile(r"\b(shutdown|reboot|halt|poweroff)\b"), "system shutdown/reboot"),
    # iptables flush
    (re.compile(r"\biptables\s+-F\b"), "iptables flush"),
    # Python/perl reverse shells
    (re.compile(r"\bpython[23]?\s+-c\s+.*socket.*connect"), "python reverse shell"),
    (re.compile(r"\bperl\s+-e\s+.*socket.*connect"), "perl reverse shell"),
    # Base64 decode and execute
    (re.compile(r"\bbase64\s+-d.*\|\s*(ba)?sh\b"), "base64 decode to shell"),
    # Prompt injection patterns
    (re.compile(r"ignore\s+(previous|above|all)\s+(instructions?|prompts?)", re.IGNORECASE), "prompt injection"),
    (re.compile(r"you\s+are\s+now\s+(a|an)\s+", re.IGNORECASE), "role injection"),
]

# Safe-mode additional patterns (blocked only when safe_mode=True)
_SAFE_MODE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bchmod\s+777\b"), "chmod 777 (safe mode)"),
    (re.compile(r"\bchmod\s+666\b"), "chmod 666 (safe mode)"),
    (re.compile(r"\beval\s+"), "eval command (safe mode)"),
    (re.compile(r">\s*/dev/[sh]d"), "redirect to device (safe mode)"),
    (re.compile(r"\bsudo\s+su\b"), "sudo su (safe mode)"),
]

# System-critical paths
_SYSTEM_PATHS = frozenset({
    "/etc", "/boot", "/usr", "/bin", "/sbin", "/dev",
    "/lib", "/lib64", "/proc", "/sys",
})

_WRITE_INDICATORS = re.compile(
    r"\brm\b|\bmv\b|\bcp\b.*\s+/|\bdd\b|\b>\s*/|\btee\s+/|\binstall\b|\bchmod\b|\bchown\b"
    r"|\bmkdir\b|\brmdir\b|\btouch\b|\bln\b"
)
# fmt: on


class RiskLevel(StrEnum):
    """Risk classification for commands."""

    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"
    BLOCKED = "blocked"


class ValidationResult(BaseModel):
    """Result of command validation."""

    is_valid: bool = True
    risk_level: RiskLevel = RiskLevel.SAFE
    is_syntax_valid: bool = True
    is_banned: bool = False
    banned_reason: str | None = None
    requires_sudo: bool = False
    sudo_allowed: bool = True
    path_warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def check_syntax(command: str) -> tuple[bool, str | None]:
    """Validate command syntax using bashlex.

    Returns (is_valid, error_message).
    """
    try:
        import bashlex

        bashlex.parse(command)
        return True, None
    except Exception as e:
        return False, str(e)


def check_banned_patterns(
    command: str, safe_mode: bool = True
) -> tuple[bool, str | None]:
    """Check if command matches any banned pattern.

    Returns (is_banned, reason).
    """
    for pattern, reason in _BANNED_PATTERNS:
        if pattern.search(command):
            return True, reason

    if safe_mode:
        for pattern, reason in _SAFE_MODE_PATTERNS:
            if pattern.search(command):
                return True, reason

    return False, None


def classify_risk(command: str, ctx: EnvironmentContext) -> RiskLevel:
    """Classify the risk level of a command."""
    # Check banned patterns first
    is_banned, _ = check_banned_patterns(command, ctx.safe_mode)
    if is_banned:
        return RiskLevel.BLOCKED

    # Check for sudo usage
    has_sudo = bool(re.search(r"\bsudo\b", command))

    # Check for writes to system paths
    writes_system = False
    for sys_path in _SYSTEM_PATHS:
        if sys_path in command and _WRITE_INDICATORS.search(command):
            writes_system = True
            break

    # Dangerous: writes to system paths with sudo
    if writes_system and has_sudo:
        return RiskLevel.DANGEROUS

    # Caution: sudo or system path writes or destructive operations
    if has_sudo or writes_system:
        return RiskLevel.CAUTION

    # Check for potentially destructive commands
    if re.search(r"\brm\b|\bdd\b|\bmkfs\b|\bkill\b.*-9", command):
        return RiskLevel.CAUTION

    return RiskLevel.SAFE


def check_sudo(command: str, ctx: EnvironmentContext) -> tuple[bool, bool]:
    """Check sudo usage against context settings.

    Returns (requires_sudo, sudo_allowed).
    """
    has_sudo = bool(re.search(r"\bsudo\b", command))
    return has_sudo, ctx.allow_sudo or not has_sudo


def check_path_safety(command: str) -> list[str]:
    """Check if command writes to system-critical paths.

    Returns list of warning messages.
    """
    warnings: list[str] = []
    for sys_path in _SYSTEM_PATHS:
        if sys_path in command and _WRITE_INDICATORS.search(command):
            warnings.append(f"Command modifies system path: {sys_path}")
    return warnings


def validate_command(
    command: str, ctx: EnvironmentContext
) -> ValidationResult:
    """Full validation pipeline for a generated command.

    Steps:
    1. Syntax check (bashlex)
    2. Banned pattern check
    3. Risk classification
    4. Sudo audit
    5. Path safety check
    """
    result = ValidationResult()

    # 1. Syntax check
    is_syntax_valid, syntax_error = check_syntax(command)
    result.is_syntax_valid = is_syntax_valid
    if not is_syntax_valid:
        result.errors.append(f"Syntax error: {syntax_error}")

    # 2. Banned patterns
    is_banned, banned_reason = check_banned_patterns(command, ctx.safe_mode)
    result.is_banned = is_banned
    result.banned_reason = banned_reason
    if is_banned:
        result.is_valid = False
        result.risk_level = RiskLevel.BLOCKED
        result.errors.append(f"Banned pattern: {banned_reason}")
        return result  # Early return — blocked commands fail immediately

    # 3. Risk classification
    result.risk_level = classify_risk(command, ctx)

    # 4. Sudo audit
    requires_sudo, sudo_allowed = check_sudo(command, ctx)
    result.requires_sudo = requires_sudo
    result.sudo_allowed = sudo_allowed
    if requires_sudo and not sudo_allowed:
        result.is_valid = False
        result.errors.append("Command requires sudo but sudo is not allowed")

    # 5. Path safety
    path_warnings = check_path_safety(command)
    result.path_warnings = path_warnings
    result.warnings.extend(path_warnings)

    # Set overall validity
    if result.errors:
        result.is_valid = False

    return result
