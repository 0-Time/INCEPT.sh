"""Interactive REPL for INCEPT."""

from __future__ import annotations

from incept.cli.commands import SlashCommandRegistry
from incept.cli.config import InceptConfig
from incept.cli.display import DisplayManager
from incept.core.pipeline import run_pipeline


class InceptREPL:
    """Interactive Read-Eval-Print Loop for INCEPT."""

    def __init__(self, config: InceptConfig) -> None:
        self.config = config
        self.display = DisplayManager(color=config.color)
        self.commands = SlashCommandRegistry()
        self.history: list[str] = []

    def get_welcome_banner(self) -> str:
        """Return the welcome banner."""
        return self.display.welcome_banner()

    def get_prompt(self) -> str:
        """Return the current prompt string."""
        return self.config.prompt

    def handle_input(self, text: str) -> str | None:
        """Process a single line of input.

        Returns output text, "__exit__" to quit, or None for no output.
        """
        if not text.strip():
            return None

        # Slash commands
        if text.startswith("/"):
            parts = text.split(maxsplit=1)
            cmd_name = parts[0]
            cmd_args = parts[1] if len(parts) > 1 else ""

            if not self.commands.has(cmd_name):
                return f"Unknown command: {cmd_name}. Type /help for available commands."

            result = self.commands.dispatch(cmd_name, cmd_args)

            # Special handling for /history
            if cmd_name == "/history":
                if self.history:
                    lines = ["Session history:"]
                    for i, entry in enumerate(self.history, 1):
                        lines.append(f"  {i}. {entry}")
                    return "\n".join(lines)
                return "Session history: (no entries yet)"

            return result

        # Natural language request
        self.history.append(text)
        pipeline_result = run_pipeline(
            nl_request=text,
            verbosity=self.config.verbosity,
        )
        return self._format_pipeline_result(pipeline_result)

    def _format_pipeline_result(self, result: object) -> str:
        """Format pipeline result for display."""
        from incept.core.pipeline import PipelineResponse
        from incept.safety.validator import RiskLevel

        if not isinstance(result, PipelineResponse):
            return str(result)

        if not result.responses:
            return "No matching command found. Try rephrasing your request."

        lines: list[str] = []
        for resp in result.responses:
            if resp.command:
                risk = RiskLevel(resp.command.risk_level)
                lines.append(self.display.format_command(resp.command.command, risk))
                if resp.command.explanation:
                    lines.append(f"  {resp.command.explanation}")
            elif resp.clarification:
                lines.append(
                    self.display.format_clarification(
                        resp.clarification.question,
                        resp.clarification.options,
                    )
                )
            elif resp.error:
                lines.append(f"Error: {resp.error.error}")
                if hasattr(resp.error, "reason"):
                    lines.append(f"  Reason: {resp.error.reason}")
        return "\n".join(lines)

    def run(self) -> None:
        """Run the interactive REPL loop using prompt_toolkit."""
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import FileHistory

        print(self.get_welcome_banner())

        session: PromptSession[str] = PromptSession(
            history=FileHistory(self.config.history_file),
        )

        while True:
            try:
                text = session.prompt(self.get_prompt())
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            result = self.handle_input(text)
            if result == "__exit__":
                print("Goodbye!")
                break
            if result is not None:
                print(result)
