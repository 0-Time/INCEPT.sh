"""Rich output formatting for the CLI."""

from __future__ import annotations

from incept.safety.validator import RiskLevel

_RISK_LABELS = {
    RiskLevel.SAFE: "SAFE",
    RiskLevel.CAUTION: "CAUTION",
    RiskLevel.DANGEROUS: "DANGEROUS",
    RiskLevel.BLOCKED: "BLOCKED",
}

_RISK_COLORS = {
    RiskLevel.SAFE: "green",
    RiskLevel.CAUTION: "yellow",
    RiskLevel.DANGEROUS: "red",
    RiskLevel.BLOCKED: "bright_red",
}


class DisplayManager:
    """Formats output for the terminal using Rich (or plain text)."""

    def __init__(self, color: bool = True) -> None:
        self.color = color

    def format_command(self, command: str, risk_level: RiskLevel) -> str:
        """Format a command with risk-level indicator."""
        label = _RISK_LABELS.get(risk_level, "UNKNOWN")
        return f"[{label}] {command}"

    def format_clarification(self, question: str, options: list[str] | None = None) -> str:
        """Format a clarification question."""
        lines = [f"? {question}"]
        if options:
            for i, opt in enumerate(options, 1):
                lines.append(f"  {i}. {opt}")
        return "\n".join(lines)

    def format_multi_step(self, steps: list[str]) -> str:
        """Format a multi-step command plan."""
        lines = ["Multi-step plan:"]
        for i, step in enumerate(steps, 1):
            lines.append(f"  {i}. {step}")
        return "\n".join(lines)

    def format_recovery(self, recovery_command: str, explanation: str) -> str:
        """Format an error recovery suggestion."""
        lines = [
            "Recovery suggestion:",
            f"  Command: {recovery_command}",
            f"  Reason:  {explanation}",
        ]
        return "\n".join(lines)

    def welcome_banner(self) -> str:
        """Return the welcome banner text."""
        return (
            "INCEPT - Offline NL-to-Linux Command Compiler\n"
            "Type a natural language request, or /help for commands.\n"
            "Press Ctrl+D to exit.\n"
        )

    def action_prompt(self) -> str:
        """Return the action prompt text."""
        return "[E]xecute  [C]opy  [S]kip  > "
