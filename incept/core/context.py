"""Context resolver: environment detection and parsing."""

from __future__ import annotations

import json
import subprocess
from typing import Literal

from pydantic import BaseModel


class EnvironmentContext(BaseModel):
    """Structured environment context for command generation."""

    # Distro info
    distro_id: str = "debian"
    distro_version: str = ""
    distro_family: Literal["debian", "rhel", "arch", "suse", "macos"] = "debian"
    kernel_version: str = ""

    # Shell info
    shell: str = "bash"
    shell_version: str = ""
    coreutils_version: str = ""

    # User info
    user: str = "user"
    is_root: bool = False
    cwd: str = "/home/user"

    # Settings
    safe_mode: bool = True
    verbosity: Literal["quiet", "normal", "verbose"] = "normal"
    allow_sudo: bool = True


class ContextSettings(BaseModel):
    """User-configurable settings extracted from context."""

    safe_mode: bool = True
    verbosity: Literal["quiet", "normal", "verbose"] = "normal"
    allow_sudo: bool = True


def parse_context(json_str: str) -> EnvironmentContext:
    """Parse a JSON context string into an EnvironmentContext.

    Applies safe defaults for any missing fields.
    Accepts either a flat JSON object with all fields, or a nested
    object with "environment" and "settings" sub-objects.
    """
    try:
        data = json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return EnvironmentContext()

    if not isinstance(data, dict):
        return EnvironmentContext()

    # Handle nested format: { "environment": {...}, "settings": {...} }
    if "environment" in data:
        env = data.get("environment", {})
        settings = data.get("settings", {})
        if isinstance(env, dict):
            merged = {**env}
            if isinstance(settings, dict):
                merged.update(settings)
            return EnvironmentContext(
                **{k: v for k, v in merged.items() if k in EnvironmentContext.model_fields}
            )

    # Handle flat format
    return EnvironmentContext(
        **{k: v for k, v in data.items() if k in EnvironmentContext.model_fields}
    )


# Bash script for environment detection (noqa: E501 — shell script lines)
CONTEXT_SNAPSHOT_SCRIPT = (  # noqa: E501
    "#!/bin/bash\n"
    "# context_snapshot.sh — collects environment info for INCEPT\n"
    'if [ "$(uname -s)" = "Darwin" ]; then\n'
    '  DID="macos"\n'
    '  DVER=$(sw_vers -productVersion 2>/dev/null)\n'
    '  DFAM="macos"\n'
    "else\n"
    "  DID=$(. /etc/os-release 2>/dev/null && echo $ID || echo unknown)\n"
    "  DVER=$(. /etc/os-release 2>/dev/null && echo $VERSION_ID)\n"
    "  DFAM=$(. /etc/os-release 2>/dev/null && echo $ID_LIKE "
    "| awk '{print $1}')\n"
    "fi\n"
    "KVER=$(uname -r 2>/dev/null)\n"
    "SH=$(basename ${SHELL:-/bin/bash})\n"
    "SHVER=$(${SHELL:-/bin/bash} --version 2>/dev/null "
    "| head -1 | grep -oP '[\\d.]+')\n"
    "CUVER=$(ls --version 2>/dev/null "
    "| head -1 | grep -oP '[\\d.]+')\n"
    "USR=$(whoami)\n"
    'ISROOT=$([ "$(id -u)" -eq 0 ] && echo true || echo false)\n'
    "CWD=$(pwd)\n"
    "cat <<EOF\n"
    "{\n"
    '  "distro_id": "$DID",\n'
    '  "distro_version": "$DVER",\n'
    '  "distro_family": "$DFAM",\n'
    '  "kernel_version": "$KVER",\n'
    '  "shell": "$SH",\n'
    '  "shell_version": "$SHVER",\n'
    '  "coreutils_version": "$CUVER",\n'
    '  "user": "$USR",\n'
    '  "is_root": $ISROOT,\n'
    '  "cwd": "$CWD"\n'
    "}\n"
    "EOF\n"
)


def run_context_snapshot() -> EnvironmentContext:
    """Execute the context snapshot script and return an EnvironmentContext.

    Falls back to defaults if the script fails or returns invalid JSON.
    """
    try:
        result = subprocess.run(
            ["bash", "-c", CONTEXT_SNAPSHOT_SCRIPT],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return EnvironmentContext()
        return parse_context(result.stdout)
    except (subprocess.TimeoutExpired, OSError):
        return EnvironmentContext()
