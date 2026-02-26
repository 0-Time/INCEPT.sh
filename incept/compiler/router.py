"""Intent router: dispatches IR to the correct compiler function."""

from __future__ import annotations

from typing import Any, Protocol

from incept.compiler.composition import compose_commands
from incept.core.context import EnvironmentContext
from incept.schemas.intents import IntentLabel
from incept.schemas.ir import AnyIR, ClarificationIR, PipelineIR, SingleIR


class CompilerFunc(Protocol):
    """Protocol for compiler functions."""

    def __call__(
        self, params: dict[str, Any], ctx: EnvironmentContext
    ) -> str: ...


class CompileResult:
    """Result of compiling an IR to a shell command."""

    def __init__(
        self,
        command: str,
        requires_sudo: bool = False,
        warnings: list[str] | None = None,
    ) -> None:
        self.command = command
        self.requires_sudo = requires_sudo
        self.warnings = warnings or []

    def __str__(self) -> str:
        prefix = "sudo " if self.requires_sudo else ""
        return f"{prefix}{self.command}"

    @property
    def full_command(self) -> str:
        """Return the command with sudo prefix if needed."""
        prefix = "sudo " if self.requires_sudo else ""
        return f"{prefix}{self.command}"


class IntentRouter:
    """Routes SingleIR to the correct compiler function by intent label."""

    def __init__(self) -> None:
        self._registry: dict[IntentLabel, CompilerFunc] = {}

    def register(self, intent: IntentLabel, func: CompilerFunc) -> None:
        """Register a compiler function for an intent."""
        self._registry[intent] = func

    def register_many(self, mapping: dict[IntentLabel, CompilerFunc]) -> None:
        """Register multiple compiler functions at once."""
        self._registry.update(mapping)

    def has_compiler(self, intent: IntentLabel) -> bool:
        """Check if a compiler is registered for an intent."""
        return intent in self._registry

    def compile_single(
        self, ir: SingleIR, ctx: EnvironmentContext
    ) -> CompileResult:
        """Compile a SingleIR to a shell command string."""
        if ir.intent in (
            IntentLabel.CLARIFY,
            IntentLabel.OUT_OF_SCOPE,
            IntentLabel.UNSAFE_REQUEST,
        ):
            raise ValueError(f"Cannot compile special intent: {ir.intent}")

        func = self._registry.get(ir.intent)
        if func is None:
            raise KeyError(f"No compiler registered for intent: {ir.intent}")

        command = func(ir.params, ctx)
        return CompileResult(
            command=command,
            requires_sudo=ir.requires_sudo and ctx.allow_sudo,
        )

    def compile_pipeline(
        self, ir: PipelineIR, ctx: EnvironmentContext
    ) -> CompileResult:
        """Compile a PipelineIR to a composed shell command."""
        commands: list[str] = []
        for step in ir.steps:
            result = self.compile_single(step, ctx)
            cmd = result.command
            if result.requires_sudo:
                cmd = f"sudo {cmd}"
            commands.append(cmd)

        composed = compose_commands(commands, ir)
        return CompileResult(command=composed, requires_sudo=False)

    def compile(self, ir: AnyIR, ctx: EnvironmentContext) -> CompileResult:
        """Compile any IR type to a shell command."""
        if isinstance(ir, ClarificationIR):
            raise ValueError("Cannot compile a ClarificationIR to a command")
        if isinstance(ir, PipelineIR):
            return self.compile_pipeline(ir, ctx)
        return self.compile_single(ir, ctx)
