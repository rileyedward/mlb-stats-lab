"""``statslab`` CLI entry point."""

from __future__ import annotations

import typer

from mlb_stats_lab.cli import new_notebook as _new_notebook
from mlb_stats_lab.cli import new_report as _new_report
from mlb_stats_lab.cli.flush_cache import flush_cache
from mlb_stats_lab.cli.list_templates import list_templates
from mlb_stats_lab.cli.main import main_callback
from mlb_stats_lab.cli.new import new

app = typer.Typer(
    help="MLB Stats Lab — local Statcast analytics tool.",
    no_args_is_help=False,
    add_completion=True,
)
app.callback(invoke_without_command=True)(main_callback)

# Guided entry point + flat utility commands.
app.command("new")(new)
app.command("list-templates")(list_templates)
app.command("flush-cache")(flush_cache)

# Scriptable per-template command groups.
app.add_typer(_new_notebook.app, name="new-notebook")
app.add_typer(_new_report.app, name="new-report")


__all__ = ["app"]
