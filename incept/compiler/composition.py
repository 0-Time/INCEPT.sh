"""Composition handler for multi-step pipeline commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from incept.schemas.ir import PipelineIR


# Composition operators
_COMPOSITION_OPERATORS: dict[str, str] = {
    "sequential": " && ",
    "pipe": " | ",
    "independent": "; ",
    "subshell": None,  # type: ignore[dict-item]  # Special handling
    "xargs": " | xargs ",
}


def resolve_variable_bindings(
    commands: list[str], bindings: dict[str, str]
) -> list[str]:
    """Resolve variable bindings in a command list.

    Replaces $PREV_OUTPUT and other variable references with shell constructs.
    """
    resolved: list[str] = []
    for i, cmd in enumerate(commands):
        result = cmd
        for var_name, var_expr in bindings.items():
            result = result.replace(f"${var_name}", var_expr)
        # Replace $PREV_OUTPUT with reference to previous command's output
        if "$PREV_OUTPUT" in result and i > 0:
            result = result.replace("$PREV_OUTPUT", "$PREV_OUTPUT")
        resolved.append(result)
    return resolved


def compose_commands(commands: list[str], pipeline_ir: PipelineIR) -> str:
    """Compose multiple commands into a single shell expression.

    Handles sequential (&&), pipe (|), independent (;), subshell ($()),
    and xargs (| xargs) composition.
    """
    if not commands:
        return ""

    if len(commands) == 1:
        return commands[0]

    # Resolve any variable bindings
    resolved = resolve_variable_bindings(commands, pipeline_ir.variable_bindings)

    composition = pipeline_ir.composition

    if composition == "subshell":
        # Wrap each sub-command in $() and chain with &&
        parts = [f"$({cmd})" for cmd in resolved[:-1]]
        # Last command uses the subshell outputs
        return " && ".join(parts + [resolved[-1]])

    if composition == "xargs":
        # First command pipes to xargs with second command
        if len(resolved) == 2:
            return f"{resolved[0]} | xargs {resolved[1]}"
        # For more than 2, chain with | xargs between each
        result = resolved[0]
        for cmd in resolved[1:]:
            result += f" | xargs {cmd}"
        return result

    operator = _COMPOSITION_OPERATORS.get(composition, " && ")
    return operator.join(resolved)
