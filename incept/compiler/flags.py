"""Version-aware flag lookup for shell commands."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_FLAG_TABLE_DIR = Path(__file__).parent / "flag_tables"


@lru_cache(maxsize=32)
def _load_flag_table(command: str) -> dict[str, Any]:
    """Load a flag table JSON for a command. Cached."""
    path = _FLAG_TABLE_DIR / f"{command}.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)  # type: ignore[no-any-return]


def _version_gte(version: str, min_version: str) -> bool:
    """Compare version strings (e.g., '8.25' >= '8.0')."""
    try:
        v_parts = [int(x) for x in version.split(".")]
        m_parts = [int(x) for x in min_version.split(".")]
        # Pad shorter list with zeros
        max_len = max(len(v_parts), len(m_parts))
        v_parts.extend([0] * (max_len - len(v_parts)))
        m_parts.extend([0] * (max_len - len(m_parts)))
        return v_parts >= m_parts
    except (ValueError, AttributeError):
        return True  # If version parsing fails, assume compatible


class FlagLookup:
    """Version-aware flag lookup utility.

    Usage:
        flags = FlagLookup("grep", distro_family="debian", version="3.7")
        flag = flags.get("pcre")  # returns "-P" or fallback "-E"
    """

    def __init__(
        self,
        command: str,
        distro_family: str = "debian",
        version: str = "",
    ) -> None:
        self.command = command
        self.distro_family = distro_family
        self.version = version
        self._table = _load_flag_table(command)

    def get(self, flag_name: str, default: str | None = None) -> str | None:
        """Get a flag string, with version-aware fallback.

        Returns the flag if version meets minimum, otherwise the fallback.
        Returns default if flag_name is not in the table.
        """
        entry = self._table.get(flag_name)
        if entry is None:
            return default

        flag: str = str(entry.get("flag", ""))
        min_versions = entry.get("min_version", {})
        fallback_raw = entry.get("fallback")
        fallback: str | None = str(fallback_raw) if fallback_raw is not None else None

        # Determine which min_version to check
        variant = "gnu"  # default to GNU
        if self.distro_family in ("bsd", "macos"):
            variant = "bsd"

        min_ver = min_versions.get(variant) if isinstance(min_versions, dict) else None

        # If no min_version set, flag is always available
        if min_ver is None:
            return flag

        # Check version compatibility
        if self.version and not _version_gte(self.version, min_ver):
            return fallback if fallback is not None else default

        return flag

    def get_flag(self, flag_name: str) -> str:
        """Get a flag string, raising KeyError if not found."""
        result = self.get(flag_name)
        if result is None:
            raise KeyError(f"Flag {flag_name!r} not found for command {self.command!r}")
        return result

    def has_flag(self, flag_name: str) -> bool:
        """Check if a flag is available (considering version)."""
        return self.get(flag_name) is not None
