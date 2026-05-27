"""Pitcher command-tendency metrics."""

from __future__ import annotations

import pandas as pd

from mlb_stats_lab.pitching.location import location_summary


def _safe(num: float, den: float) -> float:
    return float(num) / float(den) if den else 0.0


def command_metrics(df: pd.DataFrame) -> pd.Series:
    """First-Pitch Strike%, called-strike-in-heart%, edge%, in-zone%, ball%."""
    if df is None or df.empty:
        return pd.Series(dtype="float64", name="command_metrics")
    loc = location_summary(df)

    first = df[(df["balls"] == 0) & (df["strikes"] == 0)] if "balls" in df else df.iloc[0:0]
    fps_mask = first["description"].isin(("called_strike", "automatic_strike")) | (
        first["type"].isin(("S", "X")) if "type" in first else False
    )
    fps = _safe(fps_mask.sum(), len(first))

    type_b = float((df["type"] == "B").sum()) if "type" in df else 0.0
    ball_pct = _safe(type_b, len(df))

    return pd.Series(
        {
            "First-Pitch Strike%": fps,
            "Heart%": loc.get("Heart%", 0.0),
            "Edge%": loc.get("Edge%", 0.0),
            "Zone%": loc.get("Zone%", 0.0),
            "Ball%": ball_pct,
        },
        name="command_metrics",
    )
