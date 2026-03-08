"""INCEPT/Sh banner and branding."""

from __future__ import annotations

from rich.console import Console
from rich.text import Text

_PENGUIN_RAW = [
    r"    .--.",
    r"   |o_o |",
    r"   |:_/ |",
    r"  //   \ \\",
    r" (|     | )",
    r"/'\_   _/`\\",
    r"\___)=(___/",
]

_INCEPT_RAW = [
    "██╗███╗   ██╗ ██████╗███████╗██████╗ ████████╗",
    "██║████╗  ██║██╔════╝██╔════╝██╔══██╗╚══██╔══╝",
    "██║██╔██╗ ██║██║     █████╗  ██████╔╝   ██║   ",
    "██║██║╚██╗██║██║     ██╔══╝  ██╔═══╝    ██║   ",
    "██║██║ ╚████║╚██████╗███████╗██║        ██║   ",
    "╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝        ╚═╝   ",
]

_SEP = [" ┃ "] * 6

_SH_RAW = [
    "███████╗██╗  ██╗",
    "██╔════╝██║  ██║",
    "███████╗███████║",
    "╚════██║██╔══██║",
    "███████║██║  ██║",
    "╚══════╝╚═╝  ╚═╝",
]


def render_banner(console: Console, version: str, model_status: str, context: str) -> None:
    """Render the full welcome banner to a Rich console."""
    console.print()

    pad_width = 14
    max_rows = max(len(_PENGUIN_RAW), len(_INCEPT_RAW))

    for i in range(max_rows):
        line = Text("  ")

        # Penguin
        if i < len(_PENGUIN_RAW):
            p = Text(_PENGUIN_RAW[i].ljust(pad_width))
            p.stylize("bold cyan")
            line.append(p)
        else:
            line.append(Text(" " * pad_width))

        line.append("  ")

        # INCEPT
        if i < len(_INCEPT_RAW):
            t = Text(_INCEPT_RAW[i])
            t.stylize("bold white")
            line.append(t)

            # Separator
            s = Text(_SEP[i])
            s.stylize("bold white")
            line.append(s)

            # Sh
            sh = Text(_SH_RAW[i])
            sh.stylize("bold cyan")
            line.append(sh)

        console.print(line)

    console.print()
    console.print("  [dim italic]── Offline NL → Linux Command Engine ──[/dim italic]")
    console.print(
        "  [dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]"
    )
    console.print(
        f"  [dim cyan]v{version}[/dim cyan]  [dim]│[/dim]  {model_status}  [dim]│[/dim]  [dim yellow]{context}[/dim yellow]"
    )
    console.print(
        "  [dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]"
    )
    console.print(
        "  [dim]Type a request in plain English, or [bold]/help[/bold] for commands. [bold]Ctrl+D[/bold] to exit.[/dim]"
    )
    console.print()
