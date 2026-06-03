"""Notebook presentation helpers — styled output for templates.

Thin wrappers over pandas ``Styler`` and ``IPython.display`` so generated
notebooks render clean tables, stat strips, and section headers instead of raw
``display(series.to_frame("value"))`` dumps. No analysis logic lives here.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from mlb_stats_lab.viz.theme import NEUTRAL_PRIMARY, team_color

__all__ = ["metric_row", "report_header", "section", "stat_table"]


def _html(markup: str) -> Any:
    """Render an HTML string in a notebook (no-op object outside IPython)."""
    from IPython.display import HTML  # local import: only needed in notebooks

    return HTML(markup)


def _fmt(value: Any) -> str:
    """Format a scalar for display: rates as .3f, counts as ints, pass strings."""
    if isinstance(value, str):
        return value
    if isinstance(value, (int,)) and not isinstance(value, bool):
        return f"{value:,}"
    try:
        f = float(value)
    except (TypeError, ValueError):
        return "—"
    if f != f:  # NaN
        return "—"
    if f.is_integer() and abs(f) >= 1:
        return f"{int(f):,}"
    if abs(f) < 1:
        return f"{f:.3f}"
    return f"{f:.1f}"


def report_header(title: str, subtitle: str | None = None, team: str | None = None) -> Any:
    """A team-colored banner for the top of a report notebook."""
    primary = team_color(team, "primary") if team else NEUTRAL_PRIMARY
    secondary = team_color(team, "secondary") if team else "#888888"
    sub = (
        f'<div style="opacity:.85;font-size:14px;margin-top:6px;">{subtitle}</div>'
        if subtitle
        else ""
    )
    return _html(
        f'<div style="background:{primary};color:#fff;padding:20px 24px;border-radius:8px;'
        f'border-left:8px solid {secondary};font-family:-apple-system,Segoe UI,Roboto,sans-serif;">'
        f'<div style="font-size:26px;font-weight:700;letter-spacing:-.02em;">{title}</div>'
        f"{sub}</div>"
    )


def section(title: str, subtitle: str | None = None) -> Any:
    """A clean section header (replaces the ``## §1`` style)."""
    sub = f'<div style="color:#777;font-size:13px;">{subtitle}</div>' if subtitle else ""
    return _html(
        '<div style="margin:22px 0 8px 0;font-family:-apple-system,Segoe UI,Roboto,sans-serif;">'
        '<div style="font-size:18px;font-weight:600;border-bottom:2px solid #e5e5e5;'
        f'padding-bottom:4px;">{title}</div>{sub}</div>'
    )


def stat_table(series: pd.Series, title: str | None = None) -> Any:
    """Render a metrics ``Series`` as a styled single-column table."""
    df = series.to_frame("Value")
    df["Value"] = df["Value"].map(_fmt)
    styler = df.style.set_properties(**{"text-align": "right"}).set_table_styles(
        [
            {"selector": "th.col_heading", "props": [("display", "none")]},
            {
                "selector": "th.row_heading",
                "props": [("text-align", "left"), ("font-weight", "600")],
            },
            {"selector": "td", "props": [("padding", "3px 14px")]},
        ]
    )
    if title:
        styler = styler.set_caption(title)
        styler = styler.set_table_styles(
            [
                {
                    "selector": "caption",
                    "props": [
                        ("text-align", "left"),
                        ("font-weight", "600"),
                        ("font-size", "14px"),
                        ("padding-bottom", "6px"),
                    ],
                }
            ],
            overwrite=False,
        )
    return styler


def metric_row(metrics: dict[str, Any], team: str | None = None) -> Any:
    """A horizontal strip of key-stat cards. ``metrics`` maps label -> value."""
    accent = team_color(team, "primary") if team else NEUTRAL_PRIMARY
    cards = "".join(
        f'<div style="background:#f7f7f8;border-left:4px solid {accent};border-radius:4px;'
        f'padding:8px 14px;min-width:78px;">'
        f'<div style="font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:#777;">{label}</div>'
        f'<div style="font-size:18px;font-weight:600;color:#222;">{_fmt(value)}</div></div>'
        for label, value in metrics.items()
    )
    return _html(
        '<div style="display:flex;flex-wrap:wrap;gap:8px;margin:10px 0;'
        f'font-family:-apple-system,Segoe UI,Roboto,sans-serif;">{cards}</div>'
    )
