"""Jinja environment + ``render_report`` / ``render_html`` entry points."""

from __future__ import annotations

import dataclasses
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from mlb_stats_lab.config import get_config
from mlb_stats_lab.reports.filters import FILTERS
from mlb_stats_lab.reports.pdf import html_to_pdf


def _env() -> Environment:
    cfg = get_config()
    env = Environment(
        loader=FileSystemLoader(str(cfg.paths.pdf_templates_dir)),
        undefined=StrictUndefined,
        autoescape=False,
    )
    for name, fn in FILTERS.items():
        env.filters[name] = fn
    return env


def _to_dict(context: Any) -> dict[str, Any]:
    if isinstance(context, dict):
        return context
    if dataclasses.is_dataclass(context) and not isinstance(context, type):
        return dataclasses.asdict(context)
    raise TypeError(f"context must be dict or dataclass, got {type(context)!r}")


def render_html(template: str, context: Any) -> str:
    """Render a template to HTML only."""
    env = _env()
    tpl = env.get_template(f"{template}.html.j2")
    data = _to_dict(context)
    data.setdefault("generated_at", datetime.now().isoformat(timespec="seconds"))
    return tpl.render(**data)


def render_report(
    template: str,
    context: Any,
    output_path: str | Path,
    *,
    open_after: bool = False,
) -> Path:
    """Render a template + context to PDF on disk."""
    cfg = get_config()
    out = Path(output_path)
    if not out.is_absolute():
        out = cfg.paths.output_dir / out

    html = render_html(template, context)
    html_to_pdf(html, out, base_url=cfg.paths.pdf_templates_dir)

    if open_after:
        import subprocess
        import sys

        try:
            if sys.platform == "darwin":
                subprocess.run(["open", str(out)], check=False)
            elif sys.platform.startswith("linux"):
                subprocess.run(["xdg-open", str(out)], check=False)
            elif sys.platform == "win32":
                subprocess.run(["cmd", "/c", "start", "", str(out)], check=False)
        except Exception:
            pass

    return out


def list_pdf_templates() -> list[str]:
    cfg = get_config()
    dir_ = cfg.paths.pdf_templates_dir
    if not dir_.exists():
        return []
    return sorted(
        p.name.replace(".html.j2", "") for p in dir_.glob("*.html.j2") if not p.name.startswith("_")
    )
