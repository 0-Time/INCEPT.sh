"""Shell quoting utilities for safe command generation."""

from __future__ import annotations

import shlex


def needs_ansi_c_quoting(value: str) -> bool:
    """Check if a value contains control characters that need ANSI-C quoting."""
    return any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in value)


def ansi_c_quote(value: str) -> str:
    """Quote a string using bash $'...' ANSI-C quoting for control characters."""
    result: list[str] = []
    for ch in value:
        code = ord(ch)
        if ch == "'":
            result.append("\\'")
        elif ch == "\\":
            result.append("\\\\")
        elif ch == "\n":
            result.append("\\n")
        elif ch == "\t":
            result.append("\\t")
        elif ch == "\r":
            result.append("\\r")
        elif ch == "\a":
            result.append("\\a")
        elif ch == "\b":
            result.append("\\b")
        elif ch == "\f":
            result.append("\\f")
        elif ch == "\v":
            result.append("\\v")
        elif code < 0x20 or code == 0x7F:
            result.append(f"\\x{code:02x}")
        else:
            result.append(ch)
    return "$'" + "".join(result) + "'"


def quote_value(value: str, shell: str = "bash") -> str:
    """Safely quote a value for shell use.

    Uses shlex.quote (POSIX single-quoting) as the default.
    Falls back to ANSI-C quoting for bash/zsh when control characters are present.
    Empty strings are quoted as ''.
    Glob patterns and already-safe strings are returned as-is.
    """
    if not value:
        return "''"

    # If value contains control chars and shell supports ANSI-C quoting, use it
    if needs_ansi_c_quoting(value):
        if shell in ("bash", "zsh"):
            return ansi_c_quote(value)
        # For POSIX sh, use shlex.quote which handles most cases
        return shlex.quote(value)

    # shlex.quote handles all POSIX quoting needs
    return shlex.quote(value)
