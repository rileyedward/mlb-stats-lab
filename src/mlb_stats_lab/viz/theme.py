"""Visualization theme — palettes and ``apply()`` for matplotlib defaults."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import matplotlib as mpl
import seaborn as sns

TEAM_COLORS: dict[str, dict[str, str]] = {
    "ARI": {"primary": "#A71930", "secondary": "#E3D4AD", "text_on_primary": "#FFFFFF"},
    "ATL": {"primary": "#CE1141", "secondary": "#13274F", "text_on_primary": "#FFFFFF"},
    "BAL": {"primary": "#DF4601", "secondary": "#000000", "text_on_primary": "#FFFFFF"},
    "BOS": {"primary": "#BD3039", "secondary": "#0C2340", "text_on_primary": "#FFFFFF"},
    "CHC": {"primary": "#0E3386", "secondary": "#CC3433", "text_on_primary": "#FFFFFF"},
    "CWS": {"primary": "#27251F", "secondary": "#C4CED4", "text_on_primary": "#FFFFFF"},
    "CIN": {"primary": "#C6011F", "secondary": "#000000", "text_on_primary": "#FFFFFF"},
    "CLE": {"primary": "#00385D", "secondary": "#E50022", "text_on_primary": "#FFFFFF"},
    "COL": {"primary": "#333366", "secondary": "#C4CED4", "text_on_primary": "#FFFFFF"},
    "DET": {"primary": "#0C2340", "secondary": "#FA4616", "text_on_primary": "#FFFFFF"},
    "HOU": {"primary": "#002D62", "secondary": "#EB6E1F", "text_on_primary": "#FFFFFF"},
    "KC": {"primary": "#004687", "secondary": "#BD9B60", "text_on_primary": "#FFFFFF"},
    "LAA": {"primary": "#BA0021", "secondary": "#003263", "text_on_primary": "#FFFFFF"},
    "LAD": {"primary": "#005A9C", "secondary": "#EF3E42", "text_on_primary": "#FFFFFF"},
    "MIA": {"primary": "#00A3E0", "secondary": "#EF3340", "text_on_primary": "#FFFFFF"},
    "MIL": {"primary": "#0A2351", "secondary": "#B6922E", "text_on_primary": "#FFFFFF"},
    "MIN": {"primary": "#002B5C", "secondary": "#D31145", "text_on_primary": "#FFFFFF"},
    "NYM": {"primary": "#002D72", "secondary": "#FF5910", "text_on_primary": "#FFFFFF"},
    "NYY": {"primary": "#003087", "secondary": "#E4002C", "text_on_primary": "#FFFFFF"},
    "ATH": {"primary": "#003831", "secondary": "#EFB21E", "text_on_primary": "#FFFFFF"},
    "PHI": {"primary": "#E81828", "secondary": "#002D72", "text_on_primary": "#FFFFFF"},
    "PIT": {"primary": "#FDB827", "secondary": "#27251F", "text_on_primary": "#000000"},
    "SD": {"primary": "#2F241D", "secondary": "#FFC425", "text_on_primary": "#FFFFFF"},
    "SF": {"primary": "#FD5A1E", "secondary": "#27251F", "text_on_primary": "#FFFFFF"},
    "SEA": {"primary": "#0C2C56", "secondary": "#005C5C", "text_on_primary": "#FFFFFF"},
    "STL": {"primary": "#C41E3A", "secondary": "#0C2340", "text_on_primary": "#FFFFFF"},
    "TB": {"primary": "#092C5C", "secondary": "#8FBCE6", "text_on_primary": "#FFFFFF"},
    "TEX": {"primary": "#003278", "secondary": "#C0111F", "text_on_primary": "#FFFFFF"},
    "TOR": {"primary": "#134A8E", "secondary": "#E8291C", "text_on_primary": "#FFFFFF"},
    "WSN": {"primary": "#AB0003", "secondary": "#14225A", "text_on_primary": "#FFFFFF"},
}

PITCH_COLORS: dict[str, str] = {
    "FF": "#d62728",
    "SI": "#ff7f0e",
    "FC": "#8c564b",
    "SL": "#f7c948",
    "ST": "#bcbd22",
    "SV": "#aed6f1",
    "CU": "#1f77b4",
    "KC": "#5e2ca5",
    "CH": "#2ca02c",
    "FS": "#17becf",
    "FO": "#7f7f7f",
    "KN": "#e377c2",
}

OUTCOME_COLORS: dict[str, str] = {
    "home_run": "#d62728",
    "triple": "#ff7f0e",
    "double": "#bcbd22",
    "single": "#2ca02c",
    "walk": "#1f77b4",
    "hit_by_pitch": "#9467bd",
    "strikeout": "#7f7f7f",
    "field_out": "#cccccc",
    "force_out": "#cccccc",
    "grounded_into_double_play": "#999999",
    "sac_fly": "#bcbd99",
    "sac_bunt": "#bcbd99",
    "fielders_choice": "#aaaaaa",
}

NEUTRAL_PRIMARY = "#103e6e"
NEUTRAL_ACCENT = "#888888"

_applied = False


def apply() -> None:
    """Apply project-wide matplotlib/seaborn defaults (idempotent)."""
    global _applied
    if _applied:
        return
    sns.set_theme(style="white", context="notebook")
    mpl.rcParams.update(
        {
            "figure.dpi": 100,
            "savefig.dpi": 200,
            "font.family": "sans-serif",
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "axes.grid": True,
            "grid.alpha": 0.2,
            "legend.frameon": False,
        }
    )
    _applied = True


def team_color(abbrev: str | None, slot: str = "primary") -> str:
    if not abbrev:
        return NEUTRAL_PRIMARY
    info = TEAM_COLORS.get(abbrev.upper())
    return (info or {}).get(slot, NEUTRAL_PRIMARY)


def _tint(hex_color: str, amount: float) -> str:
    """Lighten ``hex_color`` toward white by ``amount`` in [0, 1]."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def report_theme(team: str | None) -> dict[str, str]:
    """Design tokens for a report, derived from a team (neutral if none).

    Shared by the PDF CSS (via injected custom properties) and the matplotlib
    chart tinting so a report's color story is defined in exactly one place.
    """
    primary = team_color(team, "primary") if team else NEUTRAL_PRIMARY
    secondary = team_color(team, "secondary") if team else NEUTRAL_ACCENT
    text = team_color(team, "text_on_primary") if team else "#FFFFFF"
    return {
        "primary": primary,
        "secondary": secondary,
        "text_on_primary": text,
        "accent_soft": _tint(primary, 0.88),
        "accent_mid": _tint(primary, 0.55),
    }


@contextmanager
def report_chart_context(accent: str | None) -> Iterator[None]:
    """Temporarily tint chart titles/spines with ``accent`` (report figures).

    Leaves data series colors untouched — only the framing picks up the team
    color, so interactive/notebook charts keep the neutral defaults.
    """
    if not accent:
        yield
        return
    with mpl.rc_context(
        {
            "axes.titlecolor": accent,
            "axes.edgecolor": accent,
            "axes.labelcolor": "#333333",
        }
    ):
        yield


def pitch_color(code: str | None) -> str:
    if not code:
        return "#cccccc"
    return PITCH_COLORS.get(str(code), "#cccccc")


def outcome_color(event: str | None) -> str:
    if not event:
        return "#cccccc"
    return OUTCOME_COLORS.get(str(event), "#cccccc")
