"""Inverse command parsers: command string → ParseResult(intent, params).

Each parser function handles a specific command prefix and returns a
ParseResult on match, or None if the command doesn't match.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ParseResult:
    """Result of parsing a shell command into intent + params."""

    intent: str
    params: dict[str, str | bool | None] = field(default_factory=dict)
    confidence: float = 0.9


# ---------------------------------------------------------------------------
# Package managers
# ---------------------------------------------------------------------------


def parse_apt_get(cmd: str) -> ParseResult | None:
    """Parse apt-get / apt commands."""
    m = re.match(r"apt(?:-get)?\s+(\S+)(?:\s+(.*))?", cmd)
    if not m:
        return None
    action = m.group(1)
    rest = (m.group(2) or "").strip()

    if action == "install":
        pkg = _extract_last_word(rest)
        return ParseResult("install_package", {"package": pkg})
    if action in ("remove", "purge"):
        pkg = _extract_last_word(rest)
        return ParseResult(
            "remove_package",
            {"package": pkg, "purge_config": action == "purge"},
        )
    if action == "update":
        return ParseResult("update_packages", {"upgrade_all": False})
    if action == "upgrade":
        return ParseResult("update_packages", {"upgrade_all": True})
    return None


def parse_dnf(cmd: str) -> ParseResult | None:
    """Parse dnf / yum commands."""
    m = re.match(r"(?:dnf|yum)\s+(\S+)(?:\s+(.*))?", cmd)
    if not m:
        return None
    action = m.group(1)
    rest = (m.group(2) or "").strip()

    if action == "install":
        return ParseResult("install_package", {"package": _extract_last_word(rest)})
    if action == "remove":
        return ParseResult("remove_package", {"package": _extract_last_word(rest)})
    if action in ("upgrade", "update"):
        return ParseResult("update_packages", {"upgrade_all": True})
    if action in ("check-update",):
        return ParseResult("update_packages", {"upgrade_all": False})
    if action == "search":
        return ParseResult("search_package", {"query": _extract_last_word(rest)})
    return None


def parse_pacman(cmd: str) -> ParseResult | None:
    """Parse pacman commands."""
    m = re.match(r"pacman\s+(-\S+)(?:\s+(.*))?", cmd)
    if not m:
        return None
    flags = m.group(1)
    rest = (m.group(2) or "").strip()

    if flags.startswith("-S") and "u" in flags:
        return ParseResult("update_packages", {"upgrade_all": True})
    if flags.startswith("-Ss"):
        return ParseResult("search_package", {"query": rest})
    if flags.startswith("-S"):
        return ParseResult("install_package", {"package": _extract_last_word(rest)})
    if flags.startswith("-R"):
        return ParseResult("remove_package", {"package": _extract_last_word(rest)})
    if flags.startswith("-Sy") and "u" not in flags:
        return ParseResult("update_packages", {"upgrade_all": False})
    return None


def parse_zypper(cmd: str) -> ParseResult | None:
    """Parse zypper commands."""
    m = re.match(r"zypper\s+(\S+)(?:\s+(.*))?", cmd)
    if not m:
        return None
    action = m.group(1)
    rest = (m.group(2) or "").strip()

    if action in ("install", "in"):
        return ParseResult("install_package", {"package": _extract_last_word(rest)})
    if action in ("remove", "rm"):
        return ParseResult("remove_package", {"package": _extract_last_word(rest)})
    if action == "search":
        return ParseResult("search_package", {"query": _extract_last_word(rest)})
    if action in ("refresh", "update"):
        return ParseResult("update_packages", {"upgrade_all": action == "update"})
    return None


def parse_brew(cmd: str) -> ParseResult | None:
    """Parse Homebrew commands."""
    m = re.match(r"brew\s+(\S+)(?:\s+(.*))?", cmd)
    if not m:
        return None
    action = m.group(1)
    rest = (m.group(2) or "").strip()

    if action == "install":
        return ParseResult("install_package", {"package": _extract_last_word(rest)})
    if action == "uninstall":
        return ParseResult("remove_package", {"package": _extract_last_word(rest)})
    if action == "update":
        return ParseResult("update_packages", {"upgrade_all": False})
    if action == "upgrade":
        return ParseResult("update_packages", {"upgrade_all": True})
    if action == "search":
        return ParseResult("search_package", {"query": _extract_last_word(rest)})
    if action == "services":
        return _parse_brew_services(rest)
    return None


def _parse_brew_services(rest: str) -> ParseResult | None:
    m = re.match(r"(\S+)(?:\s+(\S+))?", rest)
    if not m:
        return None
    sub = m.group(1)
    svc = m.group(2) or ""
    mapping = {
        "start": "start_service",
        "stop": "stop_service",
        "restart": "restart_service",
        "info": "service_status",
        "list": "service_status",
    }
    intent = mapping.get(sub)
    if intent:
        return ParseResult(intent, {"service_name": svc})
    return None


# ---------------------------------------------------------------------------
# Service management
# ---------------------------------------------------------------------------


def parse_systemctl(cmd: str) -> ParseResult | None:
    """Parse systemctl commands."""
    m = re.match(r"systemctl\s+(\S+)\s+(\S+)", cmd)
    if not m:
        return None
    action = m.group(1)
    unit = m.group(2)

    mapping = {
        "start": "start_service",
        "stop": "stop_service",
        "restart": "restart_service",
        "enable": "enable_service",
        "disable": "enable_service",
        "status": "service_status",
    }
    intent = mapping.get(action)
    if intent:
        return ParseResult(intent, {"service_name": unit})
    return None


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------


def parse_find(cmd: str) -> ParseResult | None:
    """Parse find commands."""
    m = re.match(r"find\s+(\S+)(.*)", cmd)
    if not m:
        return None
    path = m.group(1)
    rest = m.group(2)

    params: dict[str, str | bool | None] = {"path": path}

    name_m = re.search(r"-name\s+['\"]?([^'\"]+)['\"]?", rest)
    if name_m:
        params["name_pattern"] = name_m.group(1).strip()

    type_m = re.search(r"-type\s+(\S)", rest)
    if type_m:
        params["type"] = type_m.group(1)

    return ParseResult("find_files", params)


def parse_grep(cmd: str) -> ParseResult | None:
    """Parse grep commands."""
    m = re.match(r"grep\s+(.*)", cmd)
    if not m:
        return None
    rest = m.group(1)

    params: dict[str, str | bool | None] = {}

    recursive = bool(re.search(r"(?:^|\s)-[a-zA-Z]*r", rest))
    if recursive:
        params["recursive"] = True

    ignore_case = bool(re.search(r"(?:^|\s)-[a-zA-Z]*i", rest))
    if ignore_case:
        params["ignore_case"] = True

    # Extract pattern: last non-flag token before optional file
    tokens = rest.split()
    non_flag = [t for t in tokens if not t.startswith("-")]
    if non_flag:
        params["pattern"] = non_flag[0].strip("'\"")

    return ParseResult("search_text", params)


def parse_sed(cmd: str) -> ParseResult | None:
    """Parse sed substitution commands."""
    if not re.match(r"sed\b", cmd):
        return None
    m = re.search(r"s[/|]([^/|]+)[/|]([^/|]*)[/|]", cmd)
    if m:
        return ParseResult(
            "replace_text",
            {"pattern": m.group(1), "replacement": m.group(2)},
        )
    return None


# ---------------------------------------------------------------------------
# Archive operations
# ---------------------------------------------------------------------------


def parse_tar(cmd: str) -> ParseResult | None:
    """Parse tar commands."""
    m = re.match(r"tar\s+(.*)", cmd)
    if not m:
        return None
    rest = m.group(1)

    if re.search(r"-[a-zA-Z]*x", rest):
        return ParseResult("extract_archive", {})
    if re.search(r"-[a-zA-Z]*c", rest):
        return ParseResult("compress_archive", {})
    return None


# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------


def parse_docker(cmd: str) -> ParseResult | None:
    """Parse docker commands."""
    m = re.match(r"docker\s+(\S+)(?:\s+(.*))?", cmd)
    if not m:
        return None
    action = m.group(1)
    rest = (m.group(2) or "").strip()

    mapping = {
        "run": "docker_run",
        "ps": "docker_ps",
        "stop": "docker_stop",
        "logs": "docker_logs",
        "build": "docker_build",
        "exec": "docker_exec",
    }
    intent = mapping.get(action)
    if intent:
        return ParseResult(intent, {"args": rest})
    return None


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------


def parse_git(cmd: str) -> ParseResult | None:
    """Parse git commands."""
    m = re.match(r"git\s+(\S+)(?:\s+(.*))?", cmd)
    if not m:
        return None
    action = m.group(1)
    rest = (m.group(2) or "").strip()

    mapping = {
        "status": "git_status",
        "commit": "git_commit",
        "push": "git_push",
        "pull": "git_pull",
        "log": "git_log",
        "diff": "git_diff",
        "branch": "git_branch",
    }
    intent = mapping.get(action)
    if intent:
        return ParseResult(intent, {"args": rest})
    return None


# ---------------------------------------------------------------------------
# SSH
# ---------------------------------------------------------------------------


def parse_ssh(cmd: str) -> ParseResult | None:
    """Parse ssh, ssh-keygen, ssh-copy-id commands."""
    if cmd.startswith("ssh-keygen"):
        return ParseResult("generate_ssh_key", {})
    if cmd.startswith("ssh-copy-id"):
        return ParseResult("copy_ssh_key", {})
    m = re.match(r"ssh\s+(.+)", cmd)
    if m:
        return ParseResult("ssh_connect", {"target": m.group(1)})
    return None


# ---------------------------------------------------------------------------
# Firewall
# ---------------------------------------------------------------------------


def parse_ufw(cmd: str) -> ParseResult | None:
    """Parse ufw commands."""
    m = re.match(r"ufw\s+(\S+)(?:\s+(.*))?", cmd)
    if not m:
        return None
    action = m.group(1)
    rest = (m.group(2) or "").strip()

    if action == "allow":
        return ParseResult("firewall_allow", {"port": rest.split("/")[0]})
    if action == "deny":
        return ParseResult("firewall_deny", {"port": rest.split("/")[0]})
    if action in ("status", "show"):
        return ParseResult("firewall_list", {})
    return None


# ---------------------------------------------------------------------------
# Network downloads
# ---------------------------------------------------------------------------


def parse_curl(cmd: str) -> ParseResult | None:
    """Parse curl commands."""
    if not re.match(r"curl\b", cmd):
        return None
    params: dict[str, str | bool | None] = {}

    o_match = re.search(r"-o\s+(\S+)", cmd)
    if o_match:
        params["output_path"] = o_match.group(1)

    # Extract URL (last token that looks like a URL or just last token)
    tokens = cmd.split()
    urls = [t for t in tokens if t.startswith("http")]
    if urls:
        params["url"] = urls[0]

    return ParseResult("download_file", params)


def parse_wget(cmd: str) -> ParseResult | None:
    """Parse wget commands."""
    if not re.match(r"wget\b", cmd):
        return None
    tokens = cmd.split()
    urls = [t for t in tokens if t.startswith("http")]
    params: dict[str, str | bool | None] = {}
    if urls:
        params["url"] = urls[0]
    return ParseResult("download_file", params)


# ---------------------------------------------------------------------------
# Scheduling
# ---------------------------------------------------------------------------


def parse_crontab(cmd: str) -> ParseResult | None:
    """Parse crontab commands."""
    if not re.match(r"crontab\b", cmd):
        return None
    if "-l" in cmd:
        return ParseResult("list_cron", {})
    if "-e" in cmd:
        return ParseResult("schedule_cron", {})
    if "-r" in cmd:
        return ParseResult("remove_cron", {})
    return ParseResult("list_cron", {})


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _extract_last_word(s: str) -> str:
    """Extract the last non-flag token from a string."""
    tokens = s.split()
    # Walk backwards to find the first non-flag token
    for t in reversed(tokens):
        if not t.startswith("-"):
            return t
    return s.strip()
