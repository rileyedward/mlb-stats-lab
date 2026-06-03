"""Rich-backed output helpers for the CLI."""

from __future__ import annotations

import sys
from collections.abc import Iterator
from contextlib import contextmanager

try:
    from rich.console import Console

    _console: Console | None = Console()
except Exception:
    _console = None


def _print(prefix: str, msg: str, style: str = "") -> None:
    if _console is None:
        sys.stdout.write(f"{prefix} {msg}\n")
        sys.stdout.flush()
    else:
        _console.print(f"[{style}]{prefix}[/{style}] {msg}" if style else f"{prefix} {msg}")


def success(msg: str) -> None:
    _print("✓", msg, style="green")


def info(msg: str) -> None:
    _print("•", msg)


def warn(msg: str) -> None:
    _print("⚠", msg, style="yellow")


def fail(msg: str) -> None:
    _print("✗", msg, style="red")


def step(msg: str) -> None:
    _print("→", msg, style="cyan")


@contextmanager
def status(msg: str) -> Iterator[None]:
    """Spinner while a slow step runs (plain line if rich is unavailable)."""
    if _console is None:
        step(msg)
        yield
        return
    with _console.status(f"[cyan]{msg}[/cyan]", spinner="dots"):
        yield


def summary(title: str, rows: dict[str, str]) -> None:
    """A boxed key/value summary at the end of a command."""
    if _console is None:
        _print("✓", title, style="green")
        for k, v in rows.items():
            sys.stdout.write(f"    {k}: {v}\n")
        sys.stdout.flush()
        return
    from rich.panel import Panel
    from rich.table import Table

    table = Table.grid(padding=(0, 2))
    table.add_column(justify="right", style="dim")
    table.add_column()
    for k, v in rows.items():
        table.add_row(k, v)
    _console.print(Panel(table, title=f"[green]{title}[/green]", title_align="left", expand=False))
