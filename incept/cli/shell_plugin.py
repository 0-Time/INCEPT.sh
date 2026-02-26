"""Shell plugin generator and installer for bash/zsh."""

from __future__ import annotations

import os
from pathlib import Path

_PLUGIN_DIR = Path(__file__).resolve().parent.parent.parent / "scripts" / "plugins"

_MARKER = "# incept shell plugin"

_SUPPORTED_SHELLS = ("bash", "zsh")


def generate_bash_plugin() -> str:
    """Return the bash plugin script content."""
    return (_PLUGIN_DIR / "incept.bash").read_text()


def generate_zsh_plugin() -> str:
    """Return the zsh plugin script content."""
    return (_PLUGIN_DIR / "incept.zsh").read_text()


def detect_shell() -> str:
    """Auto-detect the current shell (bash or zsh)."""
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    return "bash"


def _default_rc_path(shell: str) -> str:
    """Return the default rc file path for the given shell."""
    home = Path.home()
    if shell == "zsh":
        return str(home / ".zshrc")
    return str(home / ".bashrc")


def _source_line(shell: str) -> str:
    """Return the source line to add to the rc file."""
    script_name = f"incept.{shell}"
    script_path = _PLUGIN_DIR / script_name
    return f'{_MARKER}\nsource "{script_path}"\n'


def install_plugin(shell: str, rc_path: str | None = None) -> str:
    """Install the incept plugin for the given shell.

    Appends a source line to the shell rc file (idempotent).
    Returns a status message.
    """
    if shell not in _SUPPORTED_SHELLS:
        msg = f"Unsupported shell: {shell!r}. Supported: {', '.join(_SUPPORTED_SHELLS)}"
        raise ValueError(msg)

    if rc_path is None:
        rc_path = _default_rc_path(shell)

    rc = Path(rc_path)
    script_name = f"incept.{shell}"

    # Check if already installed
    if rc.exists():
        content = rc.read_text()
        if script_name in content:
            return f"Plugin already installed in {rc_path}"
    else:
        content = ""

    source = _source_line(shell)
    with open(rc_path, "a") as f:
        if content and not content.endswith("\n"):
            f.write("\n")
        f.write(source)

    return f"Plugin installed. Restart your shell or run: source {rc_path}"


def uninstall_plugin(shell: str, rc_path: str | None = None) -> str:
    """Uninstall the incept plugin from the given shell.

    Removes the source line from the shell rc file.
    Returns a status message.
    """
    if shell not in _SUPPORTED_SHELLS:
        msg = f"Unsupported shell: {shell!r}. Supported: {', '.join(_SUPPORTED_SHELLS)}"
        raise ValueError(msg)

    if rc_path is None:
        rc_path = _default_rc_path(shell)

    rc = Path(rc_path)
    if not rc.exists():
        return "Plugin not installed."

    lines = rc.read_text().splitlines(keepends=True)
    script_name = f"incept.{shell}"

    filtered = []
    skip_next = False
    for line in lines:
        if skip_next:
            skip_next = False
            continue
        if line.strip() == _MARKER:
            skip_next = True
            continue
        if script_name in line and "source" in line:
            continue
        filtered.append(line)

    rc.write_text("".join(filtered))
    return "Plugin uninstalled."
