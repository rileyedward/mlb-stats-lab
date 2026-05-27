"""``statslab`` CLI entry point."""

from __future__ import annotations

import typer

from mlb_stats_lab.cli import flush_cache as _flush_cache
from mlb_stats_lab.cli import list_templates as _list_templates
from mlb_stats_lab.cli import new_notebook as _new_notebook
from mlb_stats_lab.cli import new_report as _new_report
from mlb_stats_lab.cli.main import main_callback

app = typer.Typer(
    help="MLB Stats Lab — local Statcast analytics tool.",
    no_args_is_help=False,
    add_completion=True,
)
app.callback(invoke_without_command=True)(main_callback)
app.add_typer(_new_notebook.app, name="new-notebook")
app.add_typer(_new_report.app, name="new-report")
app.add_typer(_list_templates.app, name="list-templates")
app.add_typer(_flush_cache.app, name="flush-cache")


__all__ = ["app"]
