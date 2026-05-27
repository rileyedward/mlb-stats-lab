"""``statslab list-templates``."""

from __future__ import annotations

import typer

from mlb_stats_lab.cli import _output as out
from mlb_stats_lab.cli.registry import TEMPLATES
from mlb_stats_lab.reports.engine import list_pdf_templates

app = typer.Typer()


@app.callback(invoke_without_command=True)
def list_templates() -> None:
    """List notebook + PDF templates."""
    out.info("NOTEBOOK TEMPLATES")
    for name, spec in sorted(TEMPLATES.items()):
        exists = spec.notebook_path.exists()
        mark = " " if exists else "*"
        print(f"  {mark}{name:<24} {spec.description}")

    out.info("PDF TEMPLATES")
    pdfs = list_pdf_templates()
    if not pdfs:
        print("  (none)")
    for name in pdfs:
        print(f"   {name}")
