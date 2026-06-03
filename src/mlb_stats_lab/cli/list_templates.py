"""``statslab list-templates``."""

from __future__ import annotations

from mlb_stats_lab.cli import _output as out
from mlb_stats_lab.cli.registry import TEMPLATES
from mlb_stats_lab.reports.engine import list_pdf_templates


def list_templates() -> None:
    """List notebook + PDF templates."""
    out.info("NOTEBOOK TEMPLATES")
    for name, spec in sorted(TEMPLATES.items()):
        mark = " " if spec.notebook_path.exists() else "*"
        print(f"  {mark}{name:<24} {spec.description}")

    out.info("PDF TEMPLATES")
    pdfs = list_pdf_templates()
    if not pdfs:
        print("  (none)")
    for name in pdfs:
        print(f"   {name}")
