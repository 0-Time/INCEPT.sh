"""Cross-platform clipboard support."""

from __future__ import annotations

import shutil
import subprocess


def detect_clipboard_tool() -> str | None:
    """Detect available clipboard tool.

    Returns tool name (pbcopy, xclip, xsel) or None.
    """
    for tool in ("pbcopy", "xclip", "xsel"):
        if shutil.which(tool):
            return tool
    return None


def copy_text(text: str) -> bool:
    """Copy text to system clipboard.

    Returns True on success, False if no clipboard tool available.
    """
    tool = detect_clipboard_tool()
    if tool is None:
        return False

    cmd: list[str]
    if tool == "pbcopy":
        cmd = ["pbcopy"]
    elif tool == "xclip":
        cmd = ["xclip", "-selection", "clipboard"]
    elif tool == "xsel":
        cmd = ["xsel", "--clipboard", "--input"]
    else:
        return False

    try:
        result = subprocess.run(cmd, input=text, text=True, check=False)
        return result.returncode == 0
    except OSError:
        return False
