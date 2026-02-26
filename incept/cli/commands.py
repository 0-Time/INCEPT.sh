"""Slash command registry for the REPL."""

from __future__ import annotations

from collections.abc import Callable


class SlashCommandRegistry:
    """Registry of /slash commands available in the REPL."""

    def __init__(self) -> None:
        self._commands: dict[str, tuple[Callable[[str], str], str]] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register("/help", self._cmd_help, "Show available commands")
        self.register("/context", self._cmd_context, "Show current environment context")
        self.register("/safe", self._cmd_safe, "Toggle safe mode: /safe on|off")
        self.register(
            "/verbose", self._cmd_verbose, "Set verbosity: minimal|normal|detailed"
        )
        self.register("/history", self._cmd_history, "Show command history")
        self.register("/clear", self._cmd_clear, "Clear the screen")
        self.register("/exit", self._cmd_exit, "Exit the REPL")
        self.register("/quit", self._cmd_quit, "Exit the REPL")
        self.register(
            "/explain", self._cmd_explain, "Explain a shell command: /explain <command>"
        )
        self.register(
            "/plugin", self._cmd_plugin, "Shell plugin: /plugin install|uninstall"
        )

    def register(self, name: str, handler: Callable[[str], str], description: str) -> None:
        """Register a slash command."""
        self._commands[name] = (handler, description)

    def has(self, name: str) -> bool:
        """Check if a command is registered."""
        return name in self._commands

    def dispatch(self, name: str, args: str) -> str:
        """Execute a slash command and return its output."""
        if name not in self._commands:
            return f"Unknown command: {name}. Type /help for available commands."
        handler, _ = self._commands[name]
        return handler(args)

    def get_command_names(self) -> list[str]:
        """Return all registered command names."""
        return list(self._commands.keys())

    def get_descriptions(self) -> dict[str, str]:
        """Return command names mapped to descriptions."""
        return {name: desc for name, (_, desc) in self._commands.items()}

    # ── Built-in command handlers ────────────────────────────────────

    def _cmd_help(self, args: str) -> str:
        lines = ["Available commands:"]
        for name, (_, desc) in self._commands.items():
            lines.append(f"  {name:12s} {desc}")
        lines.append("\nType any natural language request to generate a Linux command.")
        return "\n".join(lines)

    def _cmd_context(self, args: str) -> str:
        return "Environment context: (use /context to display after context detection)"

    def _cmd_safe(self, args: str) -> str:
        if args.strip().lower() == "off":
            return "Safe mode: OFF"
        return "Safe mode: ON"

    def _cmd_verbose(self, args: str) -> str:
        level = args.strip().lower()
        if level in ("minimal", "normal", "detailed"):
            return f"Verbosity set to: {level}"
        return "Usage: /verbose minimal|normal|detailed"

    def _cmd_history(self, args: str) -> str:
        return "Session history: (no entries yet)"

    def _cmd_clear(self, args: str) -> str:
        return "\033[2J\033[H"

    def _cmd_exit(self, args: str) -> str:
        return "__exit__"

    def _cmd_quit(self, args: str) -> str:
        return "__exit__"

    def _cmd_explain(self, args: str) -> str:
        if not args.strip():
            return "Usage: /explain <command>\nExample: /explain apt-get install nginx"
        from incept.explain.pipeline import run_explain_pipeline

        resp = run_explain_pipeline(args.strip())
        lines = [f"Command: {resp.command}"]
        if resp.intent:
            lines.append(f"Intent:  {resp.intent}")
        lines.append(f"Explain: {resp.explanation}")
        lines.append(f"Risk:    {resp.risk_level}")
        return "\n".join(lines)

    def _cmd_plugin(self, args: str) -> str:
        return (
            "Shell plugin installation:\n"
            "  incept plugin install [--shell bash|zsh]\n"
            "  incept plugin uninstall\n"
            "Binds Ctrl+I to invoke incept inline from your shell."
        )
