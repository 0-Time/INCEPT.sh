"""CLI entry point using Click."""

from __future__ import annotations

from typing import Literal

import click

from incept import __version__
from incept.cli.config import load_config
from incept.core.pipeline import run_pipeline


def _run_repl() -> None:
    """Start the interactive REPL."""
    from incept.cli.repl import InceptREPL

    config = load_config()
    repl = InceptREPL(config)
    repl.run()


@click.group(invoke_without_command=True)
@click.argument("query", required=False)
@click.option("--exec", "execute", is_flag=True, help="Execute the generated command")
@click.option("--minimal", is_flag=True, help="Output only the command string")
@click.option("--explain", "explain", is_flag=True, help="Explain a shell command")
@click.version_option(__version__)
@click.pass_context
def main(
    ctx: click.Context,
    query: str | None,
    execute: bool,
    minimal: bool,
    explain: bool,
) -> None:
    """INCEPT - Offline NL-to-Linux-command compiler.

    Run without arguments for interactive mode.
    Pass a query for one-shot mode.
    Use --explain to explain a shell command instead of generating one.
    """
    if ctx.invoked_subcommand is not None:
        return

    if query is None:
        _run_repl()
        return

    # Explain mode
    if explain:
        from incept.explain.pipeline import run_explain_pipeline

        explain_resp = run_explain_pipeline(query)
        click.echo(f"Command: {explain_resp.command}")
        if explain_resp.intent:
            click.echo(f"Intent:  {explain_resp.intent}")
        click.echo(f"Explain: {explain_resp.explanation}")
        click.echo(f"Risk:    {explain_resp.risk_level}")
        return

    # One-shot mode
    verbosity: Literal["minimal", "normal", "detailed"] = "minimal" if minimal else "normal"
    result = run_pipeline(nl_request=query, verbosity=verbosity)

    if result.responses:
        for resp in result.responses:
            if resp.command:
                if minimal:
                    click.echo(resp.command.command)
                else:
                    click.echo(f"Command: {resp.command.command}")
                    if resp.command.explanation:
                        click.echo(f"  {resp.command.explanation}")
            elif resp.clarification:
                click.echo(f"? {resp.clarification.question}")
            elif resp.error:
                err = resp.error
                if isinstance(err, dict):
                    click.echo(f"Error: {err.get('error', 'Unknown')}")
                else:
                    click.echo(f"Error: {err.error}")
    else:
        click.echo("No matching command found.")

    if execute and result.responses:
        for resp in result.responses:
            if resp.command:
                from incept.cli.actions import execute_command

                action_result = execute_command(resp.command.command, confirmed=True)
                if action_result.stdout:
                    click.echo(action_result.stdout, nl=False)
                if action_result.stderr:
                    click.echo(action_result.stderr, nl=False, err=True)


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
