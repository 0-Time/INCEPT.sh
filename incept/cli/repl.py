"""Interactive REPL for INCEPT-SH."""

from __future__ import annotations

import os
import time

from rich.console import Console
from rich.markup import escape

from incept import __version__
from incept.cli.banner import render_banner

try:
    from incept.cli.clipboard import copy_text as _copy
except ImportError:

    def _copy(text: str) -> bool:
        return False


from incept.cli.commands import SlashCommandRegistry
from incept.cli.config import InceptConfig
from incept.core.engine import EngineResponse, InceptEngine

console = Console()


class InceptREPL:
    """Interactive Read-Eval-Print Loop for INCEPT-SH."""

    _MAX_HISTORY_TURNS = 6

    def __init__(self, config: InceptConfig) -> None:
        self.config = config
        self.commands = SlashCommandRegistry()
        self.query_history: list[str] = []
        self._chat_history: list[dict[str, str]] = []
        self._last_resp: EngineResponse | None = None
        self._engine = InceptEngine(think=config.think)

    def _print_banner(self) -> None:
        """Print the welcome banner."""
        ctx = self._engine.context_line
        status = (
            "[bold green]● ready[/bold green]"
            if self._engine.model_loaded
            else "[bold red]● no model[/bold red]"
        )
        render_banner(console, __version__, status, ctx)

    def get_prompt(self) -> str:
        """Return the current prompt string."""
        return ""  # We use rich prompt instead

    def handle_input(self, text: str) -> str | None:
        """Process a single line of input."""
        if not text.strip():
            return None

        # Slash commands
        if text.startswith("/"):
            parts = text.split(maxsplit=1)
            cmd_name = parts[0]
            cmd_args = parts[1] if len(parts) > 1 else ""

            if not self.commands.has(cmd_name):
                return (
                    f"[red]✗[/red] Unknown command: {cmd_name}. Type /help for available commands."
                )

            # /think requires access to the engine — handle before dispatch
            if cmd_name == "/think":
                arg = cmd_args.strip().lower()
                if arg == "on":
                    self._engine._think = True
                    return "  [green]✓ Reasoning: ON[/green]  [dim](model will think before answering)[/dim]"
                elif arg == "off":
                    self._engine._think = False
                    return "  [dim]✓ Reasoning: OFF[/dim]  [dim](default — faster responses)[/dim]"
                else:
                    state = "[green]ON[/green]" if self._engine._think else "[dim]OFF[/dim]"
                    return f"  Reasoning is currently {state}. Use [bold]/think on[/bold] or [bold]/think off[/bold]."

            result = self.commands.dispatch(cmd_name, cmd_args)

            if cmd_name == "/history":
                if self.query_history:
                    lines = ["[bold]Session history:[/bold]"]
                    for i, entry in enumerate(self.query_history, 1):
                        lines.append(f"  [dim]{i}.[/dim] {entry}")
                    return "\n".join(lines)
                return "[dim]Session history: (no entries yet)[/dim]"

            return result

        # Natural language request
        self.query_history.append(text)

        # Show thinking indicator
        t0 = time.time()
        resp = self._engine.ask(text, history=self._chat_history or None)
        elapsed = time.time() - t0

        # Record turn
        self._chat_history.append({"role": "user", "content": text})
        self._chat_history.append({"role": "assistant", "content": resp.text})
        if len(self._chat_history) > self._MAX_HISTORY_TURNS * 2:
            self._chat_history = self._chat_history[-(self._MAX_HISTORY_TURNS * 2) :]

        # Store for post-response action handling (E/C keys)
        self._last_resp = resp

        return self._format_response(resp, elapsed)

    @staticmethod
    def _format_response(resp: EngineResponse, elapsed: float = 0) -> str:
        """Format an engine response for terminal display."""
        time_str = f"[dim]{elapsed:.1f}s[/dim]" if elapsed > 0 else ""

        if resp.type == "command":
            risk = resp.risk or "safe"
            if risk == "safe":
                risk_badge = "[bold green]✓ SAFE[/bold green]"
                cmd_style = "bold green"
            elif risk == "caution":
                risk_badge = "[bold yellow]⚠ CAUTION[/bold yellow]"
                cmd_style = "bold yellow"
            elif risk == "dangerous":
                risk_badge = "[bold red]✗ DANGEROUS[/bold red]"
                cmd_style = "bold red"
            else:
                risk_badge = "[bold red]🛑 BLOCKED[/bold red]"
                cmd_style = "bold red"

            lines = [
                f"  {risk_badge}  {time_str}",
                "",
                f"  [{cmd_style}]  $ {escape(resp.text)}[/{cmd_style}]",
                "",
                "  [dim]╰─ [E]xecute  [C]opy  [Enter] skip[/dim]",
            ]
            return "\n".join(lines)

        if resp.type == "blocked":
            return f"  [bold red]🛑 BLOCKED[/bold red]  {resp.text}"
        if resp.type == "clarification":
            return f"  [bold yellow]? {resp.text}[/bold yellow]"

        return f"  [dim]{resp.text}[/dim]"

    def _handle_action(self, resp: EngineResponse, action: str) -> None:
        """Handle post-response action (execute/copy)."""
        action = action.strip().lower()
        if action == "e" and resp.type == "command":
            from incept.cli.actions import execute_command

            console.print(f"  [dim]Running:[/dim] [bold]{resp.text}[/bold]")
            console.print(f"  [dim]{'─' * 40}[/dim]")
            result = execute_command(resp.text, confirmed=True)
            if result.stdout:
                console.print(f"  {result.stdout}", end="")
            if result.stderr:
                console.print(f"  [red]{result.stderr}[/red]", end="")
            console.print(f"  [dim]{'─' * 40}[/dim]")
        elif action == "c" and resp.type == "command":
            try:
                _copy(resp.text)
                console.print("  [green]✓ Copied to clipboard[/green]")
            except Exception:
                console.print(f"  [dim]Command: {resp.text}[/dim]")

    def run(self) -> None:
        """Run the interactive REPL loop."""
        from prompt_toolkit import PromptSession
        from prompt_toolkit.formatted_text import HTML
        from prompt_toolkit.history import FileHistory
        from prompt_toolkit.styles import Style

        style = Style.from_dict(
            {
                "prompt": "#00d7ff bold",
                "pound": "#5f87af",
            }
        )

        self._print_banner()

        session: PromptSession[str] = PromptSession(
            history=FileHistory(os.path.expanduser(self.config.history_file)),
            style=style,
        )

        last_resp = None

        while True:
            try:
                text = session.prompt(
                    HTML("<prompt>INCEPT-SH</prompt> <pound>❯</pound> "),
                )
            except (EOFError, KeyboardInterrupt):
                console.print("\n  [dim cyan]🐧 Goodbye![/dim cyan]\n")
                break

            # Handle action on previous command
            if last_resp and last_resp.type == "command" and text.strip().lower() in ("e", "c"):
                self._handle_action(last_resp, text)
                last_resp = None
                continue

            last_resp = None
            result = self.handle_input(text)
            if result == "__exit__":
                console.print("\n  [dim cyan]🐧 Goodbye![/dim cyan]\n")
                break
            if result is not None:
                console.print(result)
                # Store response for action handling
                last_resp = self._last_resp
