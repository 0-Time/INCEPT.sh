"""CLI entry point for INCEPT/Sh."""

from __future__ import annotations

import sys

import click
from rich.console import Console

from incept import __version__
from incept.cli.config import load_config

console = Console()


def _run_repl(*, think: bool = False) -> None:
    """Start the interactive REPL."""
    from incept.cli.repl import InceptREPL

    config = load_config()
    config.think = think
    repl = InceptREPL(config)
    repl.run()


def _oneshot(
    query: str, *, execute: bool = False, minimal: bool = False, think: bool = False
) -> None:
    """Handle a one-shot query."""
    from rich.markup import escape

    from incept.core.engine import InceptEngine

    engine = InceptEngine(think=think)
    resp = engine.ask(query)

    if resp.type == "command":
        if minimal:
            # Raw command only — for piping
            click.echo(resp.text)
        else:
            risk = resp.risk or "safe"
            if risk == "safe":
                console.print(f"  [bold green]$ {escape(resp.text)}[/bold green]")
            elif risk == "caution":
                console.print(f"  [bold yellow]⚠ $ {escape(resp.text)}[/bold yellow]")
            else:
                console.print(f"  [bold red]✗ $ {escape(resp.text)}[/bold red]")
    elif resp.type == "blocked":
        console.print(f"  [bold red]🛑 {resp.text}[/bold red]")
        sys.exit(1)
    elif resp.type == "clarification":
        console.print(f"  [bold yellow]? {resp.text}[/bold yellow]")
    else:
        console.print(f"  {resp.text}")

    if execute and resp.type == "command":
        from incept.cli.actions import execute_command

        console.print(f"  [dim]{'─' * 40}[/dim]")
        result = execute_command(resp.text, confirmed=True)
        if result.stdout:
            click.echo(result.stdout, nl=False)
        if result.stderr:
            click.echo(result.stderr, nl=False, err=True)


@click.group(invoke_without_command=True)
@click.argument("query", required=False, nargs=-1)
@click.option(
    "-c",
    "--command",
    "cmd_query",
    type=str,
    default=None,
    help="One-shot query (e.g. incept -c 'find large files')",
)
@click.option("--exec", "execute", is_flag=True, help="Execute the generated command")
@click.option("-m", "--minimal", is_flag=True, help="Output only the raw command (for piping)")
@click.option("--think", is_flag=True, default=False, help="Enable model reasoning")
@click.option(
    "--no-think", "no_think", is_flag=True, default=False, help="Disable reasoning (default)"
)
@click.version_option(__version__, prog_name="INCEPT/Sh")
@click.pass_context
def main(
    ctx: click.Context,
    query: tuple[str, ...],
    cmd_query: str | None,
    execute: bool,
    minimal: bool,
    think: bool,
    no_think: bool,
) -> None:
    """🐧 INCEPT/Sh — Offline NL → Linux Command Engine.

    \b
    Examples:
      incept                              # interactive mode
      incept "find large files"           # one-shot query
      incept -c "grep hello in all files" # one-shot with -c flag
      incept -c "disk usage" --exec       # generate + execute
      incept -c "list ports" -m           # raw command only (for piping)
      incept -c "list ports" -m | bash    # generate and pipe to bash
    """
    if ctx.invoked_subcommand is not None:
        return

    enable_think = think and not no_think

    # Determine query from -c or positional args
    final_query = cmd_query or (" ".join(query) if query else None)

    if final_query is None:
        _run_repl(think=enable_think)
        return

    _oneshot(final_query, execute=execute, minimal=minimal, think=enable_think)


@main.command()
@click.option("--host", default="0.0.0.0", help="Bind host")
@click.option("--port", default=8080, type=int, help="Bind port")
def serve(host: str, port: int) -> None:
    """Start the API server."""
    import uvicorn

    from incept.server.app import create_app
    from incept.server.config import ServerConfig

    config = ServerConfig(host=host, port=port)
    app = create_app(config)
    uvicorn.run(app, host=host, port=port)


@main.group()
def plugin() -> None:
    """Shell plugin management."""


@plugin.command()
@click.option("--shell", "shell_type", default=None, help="Shell type: bash or zsh")
def install(shell_type: str | None) -> None:
    """Install the shell plugin (Ctrl+I keybinding)."""
    from incept.cli.shell_plugin import detect_shell, install_plugin

    shell = shell_type or detect_shell()
    msg = install_plugin(shell)
    click.echo(msg)


@plugin.command()
@click.option("--shell", "shell_type", default=None, help="Shell type: bash or zsh")
def uninstall(shell_type: str | None) -> None:
    """Uninstall the shell plugin."""
    from incept.cli.shell_plugin import detect_shell, uninstall_plugin

    shell = shell_type or detect_shell()
    msg = uninstall_plugin(shell)
    click.echo(msg)
