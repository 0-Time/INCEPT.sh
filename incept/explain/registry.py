"""Parser registry: dispatches command strings to the appropriate parser."""

from __future__ import annotations

import re
from collections.abc import Callable

from incept.explain.parsers import (
    ParseResult,
    parse_apt_get,
    parse_brew,
    parse_crontab,
    parse_curl,
    parse_dnf,
    parse_docker,
    parse_find,
    parse_git,
    parse_grep,
    parse_pacman,
    parse_sed,
    parse_ssh,
    parse_systemctl,
    parse_tar,
    parse_ufw,
    parse_wget,
    parse_zypper,
)

# Ordered list of (prefix_pattern, parser_function).
# Tried in order; first match wins.
_PARSERS: list[tuple[re.Pattern[str], Callable[[str], ParseResult | None]]] = [
    (re.compile(r"^apt(?:-get)?\s"), parse_apt_get),
    (re.compile(r"^dnf\s"), parse_dnf),
    (re.compile(r"^yum\s"), parse_dnf),
    (re.compile(r"^pacman\s"), parse_pacman),
    (re.compile(r"^zypper\s"), parse_zypper),
    (re.compile(r"^brew\s"), parse_brew),
    (re.compile(r"^systemctl\s"), parse_systemctl),
    (re.compile(r"^docker\s"), parse_docker),
    (re.compile(r"^git\s"), parse_git),
    (re.compile(r"^find\s"), parse_find),
    (re.compile(r"^grep\s"), parse_grep),
    (re.compile(r"^sed\s"), parse_sed),
    (re.compile(r"^tar\s"), parse_tar),
    (re.compile(r"^ssh"), parse_ssh),
    (re.compile(r"^ufw\s"), parse_ufw),
    (re.compile(r"^curl\s"), parse_curl),
    (re.compile(r"^wget\s"), parse_wget),
    (re.compile(r"^crontab"), parse_crontab),
]


def parse_command(cmd: str) -> ParseResult | None:
    """Parse a shell command string into a ParseResult.

    Strips leading ``sudo``, then tries each registered parser in order.
    Returns the first successful ParseResult, or None if unrecognized.
    """
    if not cmd or not cmd.strip():
        return None

    # Strip sudo prefix
    cleaned = re.sub(r"^\s*sudo\s+", "", cmd.strip())

    # Handle pipe: parse only the first command in the pipeline
    first_cmd = cleaned.split("|")[0].strip()

    for pattern, parser in _PARSERS:
        if pattern.search(first_cmd):
            result = parser(first_cmd)
            if result is not None:
                return result

    return None
