"""Custom Jinja filters for the PDF report engine."""

from __future__ import annotations

import math
from typing import Any

from mlb_stats_lab.viz.theme import team_color as _team_color


def _is_nan(x: Any) -> bool:
    try:
        return isinstance(x, float) and math.isnan(x)
    except Exception:
        return False


def fmt_avg(value: Any) -> str:
    """``.288`` style — three decimals, no leading zero."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    if _is_nan(v):
        return "—"
    s = f"{v:.3f}"
    return s.lstrip("0") if abs(v) < 1 and v >= 0 else s


def fmt_pct(value: Any) -> str:
    """``22.4%`` style — one decimal."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    if _is_nan(v):
        return "—"
    if abs(v) <= 1:
        v *= 100
    return f"{v:.1f}%"


def fmt_signed_pct(value: Any) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    if _is_nan(v):
        return "—"
    if abs(v) <= 1:
        v *= 100
    return f"{v:+.1f}%"


def fmt_int(value: Any) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    if _is_nan(v):
        return "—"
    return f"{round(v)}"


def fmt_mph(value: Any) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    if _is_nan(v):
        return "—"
    return f"{v:.1f} mph"


def fmt_team_color(team: Any, slot: str = "primary") -> str:
    return _team_color(str(team) if team else None, slot)


FILTERS: dict[str, Any] = {
    "avg": fmt_avg,
    "pct": fmt_pct,
    "signed_pct": fmt_signed_pct,
    "int": fmt_int,
    "mph": fmt_mph,
    "team_color": fmt_team_color,
}
