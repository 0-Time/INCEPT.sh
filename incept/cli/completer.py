"""Tab completion for slash commands."""

from __future__ import annotations

from dataclasses import dataclass

_SLASH_COMMANDS = [
    "/help", "/context", "/safe", "/verbose",
    "/history", "/clear", "/exit", "/quit",
]


@dataclass
class Completion:
    """A tab completion suggestion."""

    text: str
    display: str = ""


class SlashCompleter:
    """Completer for /slash commands in the REPL."""

    def __init__(self, commands: list[str] | None = None) -> None:
        self.commands = commands or _SLASH_COMMANDS

    def get_completions_for(self, text: str) -> list[Completion]:
        """Return completions matching the given prefix."""
        if not text.startswith("/"):
            return []
        return [
            Completion(text=cmd, display=cmd)
            for cmd in self.commands
            if cmd.startswith(text)
        ]
