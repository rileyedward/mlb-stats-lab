"""Contact quality metrics on batted balls."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _safe(num: float, den: float) -> float:
    return float(num) / float(den) if den else 0.0


def contact_quality(df: pd.DataFrame) -> pd.Series:
    """Aggregated batted-ball quality (EV, LA, Barrel%, HardHit%, ...)."""
    if df is None or df.empty:
        return pd.Series(dtype="float64", name="contact_quality")
    in_play = df[df["type"] == "X"] if "type" in df else df
    bbe = len(in_play)
    if bbe == 0:
        return pd.Series(dtype="float64", name="contact_quality")

    ev = in_play["launch_speed"]
    la = in_play["launch_angle"]
    avg_ev = float(ev.dropna().mean()) if not ev.dropna().empty else 0.0
    max_ev = float(ev.dropna().max()) if not ev.dropna().empty else 0.0
    avg_la = float(la.dropna().mean()) if not la.dropna().empty else 0.0

    if "launch_speed_angle" in in_play.columns:
        barrels = int((in_play["launch_speed_angle"] == 6).sum())
    else:
        # Approximate barrel: EV >= 98 and LA in 26-30 (loose definition).
        barrels = int(((ev >= 98) & la.between(26, 30, inclusive="both")).sum())
    hardhit = int((ev >= 95).sum())
    sweet_spot = int(la.between(8, 32, inclusive="both").sum())

    xba = (
        float(in_play["estimated_ba_using_speedangle"].dropna().mean())
        if "estimated_ba_using_speedangle" in in_play
        else 0.0
    )
    xslg = (
        float(in_play["estimated_slg_using_speedangle"].dropna().mean())
        if "estimated_slg_using_speedangle" in in_play
        else 0.0
    )
    xwoba = (
        float(in_play["estimated_woba_using_speedangle"].dropna().mean())
        if "estimated_woba_using_speedangle" in in_play
        else 0.0
    )
    avg_dist = (
        float(in_play["hit_distance_sc"].dropna().mean()) if "hit_distance_sc" in in_play else 0.0
    )

    def _z(value: float) -> float:
        return (
            0.0 if value is None or (isinstance(value, float) and np.isnan(value)) else float(value)
        )

    return pd.Series(
        {
            "BBE": int(bbe),
            "Avg EV (mph)": _z(avg_ev),
            "Max EV (mph)": _z(max_ev),
            "Avg LA (°)": _z(avg_la),
            "Barrel%": _safe(barrels, bbe),
            "HardHit%": _safe(hardhit, bbe),
            "Sweet-Spot%": _safe(sweet_spot, bbe),
            "xBA": _z(xba),
            "xSLG": _z(xslg),
            "xwOBA (in-play)": _z(xwoba),
            "Avg Distance": _z(avg_dist),
        },
        name="contact_quality",
    )
