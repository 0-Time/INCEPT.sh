"""Slash command registry for INCEPT/Sh REPL."""

from __future__ import annotations

from collections.abc import Callable


class SlashCommandRegistry:
    """Registry of /slash commands available in the REPL."""

    def __init__(self) -> None:
        self._commands: dict[str, tuple[Callable[[str], str], str]] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register("/help", self._cmd_help, "Show available commands")
        self.register("/context", self._cmd_context, "Show system context")
        self.register("/safe", self._cmd_safe, "Toggle safe mode: /safe on|off")
        self.register("/verbose", self._cmd_verbose, "Set verbosity: minimal|normal|detailed")
        self.register("/history", self._cmd_history, "Show query history")
        self.register("/clear", self._cmd_clear, "Clear the screen")
        self.register("/exit", self._cmd_exit, "Exit INCEPT/Sh")
        self.register("/quit", self._cmd_quit, "Exit INCEPT/Sh")
        self.register("/explain", self._cmd_explain, "Explain a command: /explain <cmd>")
        self.register("/plugin", self._cmd_plugin, "Shell plugin info")

    def register(self, name: str, handler: Callable[[str], str], description: str) -> None:
        self._commands[name] = (handler, description)

    def has(self, name: str) -> bool:
        return name in self._commands

    def dispatch(self, name: str, args: str) -> str:
        if name not in self._commands:
            return f"  [red]✗[/red] Unknown command: {name}."
        handler, _ = self._commands[name]
        return handler(args)

    def get_command_names(self) -> list[str]:
        return list(self._commands.keys())

    def get_descriptions(self) -> dict[str, str]:
        return {name: desc for name, (_, desc) in self._commands.items()}

    # ── Built-in handlers ────────────────────────────────

    def _cmd_help(self, args: str) -> str:
        lines = [
            "",
            "  [bold cyan]🐧 INCEPT/Sh Commands[/bold cyan]",
            "  [dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
        ]
        for name, (_, desc) in self._commands.items():
            lines.append(f"  [bold]{name:14s}[/bold] [dim]{desc}[/dim]")
        lines.append("")
        lines.append("  [dim]Or just type any natural language request.[/dim]")
        lines.append("")
        return "\n".join(lines)

    def _cmd_context(self, args: str) -> str:
        return "  [dim]Context:[/dim] (detected at startup — see banner)"

    def _cmd_safe(self, args: str) -> str:
        if args.strip().lower() == "off":
            return "  [yellow]⚠ Safe mode: OFF[/yellow]"
        return "  [green]✓ Safe mode: ON[/green]"

    def _cmd_verbose(self, args: str) -> str:
        level = args.strip().lower()
        if level in ("minimal", "normal", "detailed"):
            return f"  [green]✓[/green] Verbosity: [bold]{level}[/bold]"
        return "  Usage: /verbose minimal|normal|detailed"

    def _cmd_history(self, args: str) -> str:
        return "  [dim]No history yet.[/dim]"

    def _cmd_clear(self, args: str) -> str:
        return "\033[2J\033[H"

    def _cmd_exit(self, args: str) -> str:
        return "__exit__"

    def _cmd_quit(self, args: str) -> str:
        return "__exit__"

    def _cmd_explain(self, args: str) -> str:
        if not args.strip():
            return "  Usage: /explain <command>\n  Example: /explain awk '{print $1}' file.txt"
        from incept.explain.pipeline import run_explain_pipeline
        resp = run_explain_pipeline(args.strip())
        lines = [
            f"  [bold]Command:[/bold]  {resp.command}",
            f"  [bold]Intent:[/bold]   {resp.intent}" if resp.intent else "",
            f"  [bold]Explain:[/bold]  {resp.explanation}",
            f"  [bold]Risk:[/bold]     {resp.risk_level}",
        ]
        return "\n".join(ln for ln in lines if ln)

    def _cmd_plugin(self, args: str) -> str:
        return (
            "\n  [bold cyan]Shell Plugin[/bold cyan]\n"
            "  [dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]\n"
            "  Install:   [bold]incept plugin install[/bold]\n"
            "  Uninstall: [bold]incept plugin uninstall[/bold]\n"
            "  Binds [bold]Ctrl+I[/bold] to invoke INCEPT inline.\n"
        )
