"""Compiler functions for text processing and archive operations."""

from __future__ import annotations

from typing import Any

from incept.compiler.quoting import quote_value
from incept.core.context import EnvironmentContext
from incept.schemas.intents import IntentLabel

# ---------------------------------------------------------------------------
# Text Processing
# ---------------------------------------------------------------------------


def compile_search_text(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a grep command for searching text patterns.

    Supports basic, extended, and Perl-compatible regular expressions,
    recursive directory search, case-insensitive matching, and line-number
    output.
    """
    parts: list[str] = ["grep"]

    regex_type: str | None = params.get("regex_type")
    if regex_type == "perl":
        parts.append("-P")
    elif regex_type == "extended":
        parts.append("-E")
    # basic is the grep default -- no flag needed

    if params.get("recursive"):
        parts.append("-r")

    if params.get("ignore_case"):
        parts.append("-i")

    if params.get("show_line_numbers"):
        parts.append("-n")

    pattern: str = params["pattern"]
    parts.append(quote_value(pattern, ctx.shell))

    path: str | None = params.get("path")
    if path is not None:
        parts.append(quote_value(path, ctx.shell))

    return " ".join(parts)


def compile_replace_text(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a sed substitution command.

    Builds a ``sed 's/pattern/replacement/[g]'`` expression with optional
    in-place editing and backup suffix.
    """
    parts: list[str] = ["sed"]

    in_place: bool = params.get("in_place", False)
    backup: str | None = params.get("backup")

    if in_place:
        if backup is not None:
            parts.append(f"-i{quote_value(backup, ctx.shell)}")
        else:
            parts.append("-i")

    pattern: str = params["pattern"]
    replacement: str = params["replacement"]
    global_replace: bool = params.get("global_replace", True)

    modifier = "g" if global_replace else ""
    sed_expr = f"s/{pattern}/{replacement}/{modifier}"
    parts.append(quote_value(sed_expr, ctx.shell))

    file_path: str = params["file"]
    parts.append(quote_value(file_path, ctx.shell))

    return " ".join(parts)


def compile_sort_output(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a sort command.

    Supports reverse ordering, numeric sorting, unique filtering, and
    field-based key selection.
    """
    parts: list[str] = ["sort"]

    if params.get("reverse"):
        parts.append("-r")

    if params.get("numeric"):
        parts.append("-n")

    if params.get("unique"):
        parts.append("-u")

    field: int | None = params.get("field")
    if field is not None:
        parts.append(f"-k {field}")

    input_file: str | None = params.get("input_file")
    if input_file is not None:
        parts.append(quote_value(input_file, ctx.shell))

    return " ".join(parts)


def compile_count_lines(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a wc command for counting lines, words, or characters."""
    parts: list[str] = ["wc"]

    mode: str = params.get("mode", "lines")
    if mode == "lines":
        parts.append("-l")
    elif mode == "words":
        parts.append("-w")
    elif mode == "chars":
        parts.append("-c")

    input_file: str | None = params.get("input_file")
    if input_file is not None:
        parts.append(quote_value(input_file, ctx.shell))

    return " ".join(parts)


def compile_extract_columns(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile an awk command for extracting columns.

    Parses a comma-separated field specification (e.g. ``"1,3,5"``) into an
    awk print statement referencing the corresponding positional fields.
    """
    parts: list[str] = ["awk"]

    delimiter: str | None = params.get("delimiter")
    if delimiter is not None:
        parts.append(f"-F{quote_value(delimiter, ctx.shell)}")

    field_spec: str = params["field_spec"]
    fields = [f"${f.strip()}" for f in field_spec.split(",")]
    awk_program = "{print " + ", ".join(fields) + "}"
    parts.append(quote_value(awk_program, ctx.shell))

    input_file: str | None = params.get("input_file")
    if input_file is not None:
        parts.append(quote_value(input_file, ctx.shell))

    return " ".join(parts)


def compile_unique_lines(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``sort | uniq`` pipeline for unique-line filtering.

    Optionally prefixes each line with its occurrence count or restricts
    output to duplicated lines only.
    """
    uniq_parts: list[str] = ["uniq"]

    if params.get("count"):
        uniq_parts.append("-c")

    if params.get("only_duplicates"):
        uniq_parts.append("-d")

    input_file: str | None = params.get("input_file")
    if input_file is not None:
        return f"sort {quote_value(input_file, ctx.shell)} | {' '.join(uniq_parts)}"

    return f"sort | {' '.join(uniq_parts)}"


# ---------------------------------------------------------------------------
# Archive Operations
# ---------------------------------------------------------------------------


_TAR_FLAGS: dict[str, str] = {
    "tar.gz": "czf",
    "tar.bz2": "cjf",
    "tar.xz": "cJf",
}


def compile_compress_archive(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a tar or zip compression command.

    Selects the appropriate compression utility and flags based on the
    requested archive format (tar.gz, tar.bz2, tar.xz, or zip).
    """
    source: str = params["source"]
    fmt: str = params.get("format", "tar.gz")
    destination: str | None = params.get("destination")
    exclude_pattern: str | None = params.get("exclude_pattern")

    if fmt == "zip":
        parts: list[str] = ["zip", "-r"]
        dest = destination if destination is not None else f"{source}.zip"
        parts.append(quote_value(dest, ctx.shell))
        parts.append(quote_value(source, ctx.shell))
        if exclude_pattern is not None:
            parts.extend(["-x", quote_value(exclude_pattern, ctx.shell)])
        return " ".join(parts)

    # tar-based formats
    tar_flags = _TAR_FLAGS.get(fmt, "czf")
    parts = ["tar"]

    if exclude_pattern is not None:
        parts.extend(["--exclude", quote_value(exclude_pattern, ctx.shell)])

    dest = destination if destination is not None else f"{source}.{fmt}"
    parts.append(tar_flags)
    parts.append(quote_value(dest, ctx.shell))
    parts.append(quote_value(source, ctx.shell))

    return " ".join(parts)


def compile_extract_archive(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile an archive extraction command.

    Auto-detects the archive format from the file extension and selects
    the appropriate tool (tar or unzip) with correct decompression flags.
    """
    source: str = params["source"]
    destination: str | None = params.get("destination")
    lower = source.lower()

    # zip
    if lower.endswith(".zip"):
        parts: list[str] = ["unzip", quote_value(source, ctx.shell)]
        if destination is not None:
            parts.extend(["-d", quote_value(destination, ctx.shell)])
        return " ".join(parts)

    # tar-based: determine decompression flag from extension
    if lower.endswith((".tar.gz", ".tgz")):
        tar_flag = "xzf"
    elif lower.endswith(".tar.bz2"):
        tar_flag = "xjf"
    elif lower.endswith(".tar.xz"):
        tar_flag = "xJf"
    else:
        # Fallback: let tar auto-detect
        tar_flag = "xf"

    parts = ["tar", tar_flag, quote_value(source, ctx.shell)]
    if destination is not None:
        parts.extend(["-C", quote_value(destination, ctx.shell)])

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEXT_OPS_COMPILERS: dict[IntentLabel, Any] = {
    IntentLabel.search_text: compile_search_text,
    IntentLabel.replace_text: compile_replace_text,
    IntentLabel.sort_output: compile_sort_output,
    IntentLabel.count_lines: compile_count_lines,
    IntentLabel.extract_columns: compile_extract_columns,
    IntentLabel.unique_lines: compile_unique_lines,
    IntentLabel.compress_archive: compile_compress_archive,
    IntentLabel.extract_archive: compile_extract_archive,
}
