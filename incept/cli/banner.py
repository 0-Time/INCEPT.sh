"""INCEPT/Sh banner and branding."""

from __future__ import annotations

from rich.text import Text


# Raw penguin lines (no markup — we'll style them manually)
_PENGUIN_RAW = [
    r"    .--.",
    r"   |o_o |",
    r"   |:_/ |",
    r"  //   \ \\",
    r" (|     | )",
    r"/'\_   _/`\\",
    r"\___)=(___/",
]

_LOGO_RAW = [
    "██╗███╗   ██╗ ██████╗███████╗██████╗ ████████╗",
    "██║████╗  ██║██╔════╝██╔════╝██╔══██╗╚══██╔══╝",
    "██║██╔██╗ ██║██║     █████╗  ██████╔╝   ██║   ",
    "██║██║╚██╗██║██║     ██╔══╝  ██╔═══╝    ██║   ",
    "██║██║ ╚████║╚██████╗███████╗██║        ██║   ",
    "╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝        ╚═╝   ",
    "                /Sh                             ",
]


def render_banner(console, version: str, model_status: str, context: str) -> None:
    """Render the full welcome banner directly to a Rich console."""
    console.print()

    pad_width = 14  # Width for penguin column
    max_rows = max(len(_PENGUIN_RAW), len(_LOGO_RAW))

    for i in range(max_rows):
        line = Text("  ")
        # Penguin part
        if i < len(_PENGUIN_RAW):
            p = _PENGUIN_RAW[i]
            ptext = Text(p.ljust(pad_width))
            ptext.stylize("bold cyan")
            line.append(ptext)
        else:
            line.append(Text(" " * pad_width))

        line.append(Text("  "))

        # Logo part
        if i < len(_LOGO_RAW):
            ltext = Text(_LOGO_RAW[i])
            if i < len(_LOGO_RAW) - 1:
                ltext.stylize("bold white")
            else:
                ltext.stylize("bold cyan")
            line.append(ltext)

        console.print(line)

    console.print()
    console.print("  [dim italic]── Offline NL → Linux Command Engine ──[/dim italic]")
    console.print("  [dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]")
    console.print(f"  [dim cyan]v{version}[/dim cyan]  [dim]│[/dim]  {model_status}  [dim]│[/dim]  [dim yellow]{context}[/dim yellow]")
    console.print("  [dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]")
    console.print("  [dim]Type a request in plain English, or [bold]/help[/bold] for commands. [bold]Ctrl+D[/bold] to exit.[/dim]")
    console.print()
