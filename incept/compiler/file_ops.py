"""Compiler functions for file operation intents.

Translates file-operation IR params into shell command strings. Each public
function takes a flat ``params`` dict (matching the corresponding Pydantic
schema) and an ``EnvironmentContext``, and returns a ready-to-execute shell
command.
"""

from __future__ import annotations

from typing import Any

from incept.compiler.quoting import quote_value
from incept.core.context import EnvironmentContext
from incept.schemas.intents import IntentLabel

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_FIND_TYPE_MAP = {"file": "f", "directory": "d", "link": "l"}


def _q(value: str, ctx: EnvironmentContext) -> str:
    return quote_value(value, ctx.shell)


# ---------------------------------------------------------------------------
# Public compiler functions
# ---------------------------------------------------------------------------


def compile_find_files(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``find`` command from *find_files* params."""
    path = params.get("path") or "."
    parts: list[str] = ["find", _q(path, ctx)]

    name_pattern = params.get("name_pattern")
    if name_pattern is not None:
        parts.extend(["-name", _q(name_pattern, ctx)])

    file_type = params.get("type")
    if file_type is not None:
        parts.extend(["-type", _FIND_TYPE_MAP.get(file_type, file_type)])

    size_gt = params.get("size_gt")
    if size_gt is not None:
        parts.extend(["-size", f"+{size_gt}"])

    size_lt = params.get("size_lt")
    if size_lt is not None:
        parts.extend(["-size", f"-{size_lt}"])

    mtime_days_gt = params.get("mtime_days_gt")
    if mtime_days_gt is not None:
        parts.extend(["-mtime", f"+{mtime_days_gt}"])

    mtime_days_lt = params.get("mtime_days_lt")
    if mtime_days_lt is not None:
        parts.extend(["-mtime", f"-{mtime_days_lt}"])

    user = params.get("user")
    if user is not None:
        parts.extend(["-user", _q(user, ctx)])

    permissions = params.get("permissions")
    if permissions is not None:
        parts.extend(["-perm", _q(permissions, ctx)])

    return " ".join(parts)


def compile_copy_files(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``cp`` command from *copy_files* params."""
    parts: list[str] = ["cp"]

    if params.get("recursive"):
        parts.append("-r")
    if params.get("preserve_attrs"):
        parts.append("-p")

    parts.append(_q(params["source"], ctx))
    parts.append(_q(params["destination"], ctx))
    return " ".join(parts)


def compile_move_files(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``mv`` command from *move_files* params."""
    parts: list[str] = [
        "mv",
        _q(params["source"], ctx),
        _q(params["destination"], ctx),
    ]
    return " ".join(parts)


def compile_delete_files(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile an ``rm`` command from *delete_files* params.

    Raises ``ValueError`` when the target is ``/`` or empty to prevent
    catastrophic recursive deletion.
    """
    target: str = params.get("target", "")
    if not target or target.strip() == "/":
        raise ValueError(
            "Refusing to compile delete command: "
            "target is root or empty (would destroy filesystem)"
        )

    parts: list[str] = ["rm"]

    if params.get("recursive"):
        parts.append("-r")
    if params.get("force"):
        parts.append("-f")

    parts.append(_q(target, ctx))
    return " ".join(parts)


def compile_change_permissions(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a ``chmod`` command from *change_permissions* params."""
    parts: list[str] = ["chmod"]

    if params.get("recursive"):
        parts.append("-R")

    parts.append(_q(params["permissions"], ctx))
    parts.append(_q(params["target"], ctx))
    return " ".join(parts)


def compile_change_ownership(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a ``chown`` command from *change_ownership* params."""
    parts: list[str] = ["chown"]

    if params.get("recursive"):
        parts.append("-R")

    owner: str = params["owner"]
    group: str | None = params.get("group")
    owner_spec = f"{owner}:{group}" if group else owner

    parts.append(_q(owner_spec, ctx))
    parts.append(_q(params["target"], ctx))
    return " ".join(parts)


def compile_create_directory(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a ``mkdir`` command from *create_directory* params."""
    parts: list[str] = ["mkdir"]

    if params.get("parents"):
        parts.append("-p")

    parts.append(_q(params["path"], ctx))
    return " ".join(parts)


def compile_list_directory(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile an ``ls`` command from *list_directory* params."""
    parts: list[str] = ["ls"]

    if params.get("long_format"):
        parts.append("-l")
    if params.get("all_files"):
        parts.append("-a")

    sort_by = params.get("sort_by")
    if sort_by == "size":
        parts.append("-S")
    elif sort_by == "time":
        parts.append("-t")
    # "name" is the default sort order for ls, no flag needed.

    path = params.get("path")
    if path is not None:
        parts.append(_q(path, ctx))

    return " ".join(parts)


def compile_disk_usage(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``du`` command from *disk_usage* params."""
    parts: list[str] = ["du"]

    if params.get("human_readable", True):
        parts.append("-h")

    max_depth = params.get("max_depth")
    if max_depth is not None:
        if ctx.distro_family == "debian":
            parts.append(f"--max-depth={max_depth}")
        else:
            parts.extend(["-d", str(max_depth)])

    path = params.get("path")
    if path is not None:
        parts.append(_q(path, ctx))

    return " ".join(parts)


def compile_view_file(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a file-viewing command from *view_file* params.

    Uses ``cat`` by default, ``head -n`` when *lines* is set (and
    *from_end* is false), or ``tail -n`` when *from_end* is true.
    """
    file_path = _q(params["file"], ctx)
    lines: int | None = params.get("lines")

    if lines is not None and params.get("from_end"):
        return f"tail -n {lines} {file_path}"
    if lines is not None:
        return f"head -n {lines} {file_path}"
    return f"cat {file_path}"


def compile_create_symlink(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile an ``ln -s`` command from *create_symlink* params."""
    parts: list[str] = [
        "ln",
        "-s",
        _q(params["target"], ctx),
        _q(params["link_name"], ctx),
    ]
    return " ".join(parts)


def compile_compare_files(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a ``diff`` command from *compare_files* params."""
    context_lines: int | None = params.get("context_lines")

    if context_lines is not None:
        parts: list[str] = ["diff", f"-C {context_lines}"]
    else:
        parts = ["diff", "-u"]

    parts.append(_q(params["file1"], ctx))
    parts.append(_q(params["file2"], ctx))
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Registry mapping: IntentLabel -> compiler function
# ---------------------------------------------------------------------------

FILE_OPS_COMPILERS: dict[IntentLabel, Any] = {
    IntentLabel.find_files: compile_find_files,
    IntentLabel.copy_files: compile_copy_files,
    IntentLabel.move_files: compile_move_files,
    IntentLabel.delete_files: compile_delete_files,
    IntentLabel.change_permissions: compile_change_permissions,
    IntentLabel.change_ownership: compile_change_ownership,
    IntentLabel.create_directory: compile_create_directory,
    IntentLabel.list_directory: compile_list_directory,
    IntentLabel.disk_usage: compile_disk_usage,
    IntentLabel.view_file: compile_view_file,
    IntentLabel.create_symlink: compile_create_symlink,
    IntentLabel.compare_files: compile_compare_files,
}
