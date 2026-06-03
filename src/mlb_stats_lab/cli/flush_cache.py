"""``statslab flush-cache``."""

from __future__ import annotations

import typer

from mlb_stats_lab.cli import _output as out
from mlb_stats_lab.data.cache import flush


def flush_cache(
    older_than_days: int | None = typer.Option(
        None, "--older-than-days", help="Only remove files older than N days. Omit to remove all."
    ),
) -> None:
    """Remove pybaseball cache files."""
    n = flush(older_than_days=older_than_days)
    out.success(f"Removed {n} cached files.")
