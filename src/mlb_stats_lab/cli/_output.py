"""Rich-backed output helpers for the CLI."""

from __future__ import annotations

import sys

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
