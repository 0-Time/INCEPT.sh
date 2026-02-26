"""Error pattern registry: classify stderr output into known error types."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ErrorPattern:
    """A recognizable error pattern from command stderr."""

    name: str
    pattern: re.Pattern[str]
    extract_context: Callable[[re.Match[str]], dict[str, str]] = field(
        default_factory=lambda: _noop_extract
    )


def _noop_extract(m: re.Match[str]) -> dict[str, str]:
    return {}


def _extract_apt_pkg(m: re.Match[str]) -> dict[str, str]:
    return {"package": m.group(1)}


def _extract_dnf_pkg(m: re.Match[str]) -> dict[str, str]:
    return {"package": m.group(1)}


def _extract_perm_path(m: re.Match[str]) -> dict[str, str]:
    return {"path": m.group(1)}


def _extract_cmd(m: re.Match[str]) -> dict[str, str]:
    return {"command": m.group(1)}


def _extract_file_path(m: re.Match[str]) -> dict[str, str]:
    return {"path": m.group(1)}


def _extract_flag(m: re.Match[str]) -> dict[str, str]:
    return {"flag": m.group(1)}


ERROR_PATTERNS: list[ErrorPattern] = [
    ErrorPattern(
        name="apt_package_not_found",
        pattern=re.compile(r"Unable to locate package\s+(\S+)"),
        extract_context=_extract_apt_pkg,
    ),
    ErrorPattern(
        name="dnf_package_not_found",
        pattern=re.compile(r"No match for argument:\s+(\S+)"),
        extract_context=_extract_dnf_pkg,
    ),
    ErrorPattern(
        name="permission_denied",
        pattern=re.compile(r"['\"]?([^'\":\s]+)['\"]?:\s*Permission denied"),
        extract_context=_extract_perm_path,
    ),
    ErrorPattern(
        name="command_not_found",
        pattern=re.compile(
            r"(?:bash|zsh|sh):\s*(?:line \d+:\s*)?"
            r"(?:command not found:\s*(\S+)|(\S+):\s*command not found)"
        ),
        extract_context=lambda m: {"command": m.group(1) or m.group(2) or ""},
    ),
    ErrorPattern(
        name="no_such_file",
        pattern=re.compile(r"cannot (?:access|open|stat)\s+'([^']+)'.*No such file or directory"),
        extract_context=_extract_file_path,
    ),
    ErrorPattern(
        name="disk_full",
        pattern=re.compile(r"No space left on device"),
        extract_context=lambda m: {},
    ),
    ErrorPattern(
        name="flag_not_recognized",
        pattern=re.compile(r"unrecognized option\s+'(--?\S+)'"),
        extract_context=_extract_flag,
    ),
]


def classify_error(stderr: str) -> tuple[ErrorPattern | None, dict[str, str]]:
    """Match stderr against known error patterns.

    Returns (matched_pattern, extracted_context) or (None, {}) if no match.
    """
    if not stderr:
        return None, {}

    for ep in ERROR_PATTERNS:
        match = ep.pattern.search(stderr)
        if match:
            ctx = ep.extract_context(match)
            return ep, ctx

    return None, {}
