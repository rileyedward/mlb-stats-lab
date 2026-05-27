"""Top-level callback (``--version``, ``--verbose``)."""

from __future__ import annotations

import os

import typer

from mlb_stats_lab import __version__


def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Print version and exit."),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose logging."),
) -> None:
    if version:
        typer.echo(f"statslab {__version__}")
        raise typer.Exit()
    if verbose:
        os.environ["STATSLAB_VERBOSE"] = "1"
    if ctx.invoked_subcommand is None and not version:
        typer.echo(ctx.get_help())
