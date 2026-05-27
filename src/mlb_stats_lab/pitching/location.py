"""Pitcher overall location tendencies."""

from __future__ import annotations

import pandas as pd

from mlb_stats_lab.filters.pitch import (
    HEART_X,
    SZ_BOT_DEFAULT,
    SZ_TOP_DEFAULT,
    ZONE_X,
)


def _safe(num: float, den: float) -> float:
    return float(num) / float(den) if den else 0.0


def location_summary(df: pd.DataFrame) -> pd.Series:
    """``Zone%``, ``Edge%``, ``Heart%``, ``Chase-Inducing%``."""
    if df is None or df.empty:
        return pd.Series(dtype="float64", name="location_summary")
    n = len(df)

    in_zone = (
        df["zone"].between(1, 9, inclusive="both")
        if "zone" in df
        else pd.Series(False, index=df.index)
    )
    out_zone = (
        df["zone"].between(11, 14, inclusive="both")
        if "zone" in df
        else pd.Series(False, index=df.index)
    )
    abs_x = df["plate_x"].abs() if "plate_x" in df else pd.Series(0.0, index=df.index)
    top = (
        df["sz_top"].fillna(SZ_TOP_DEFAULT)
        if "sz_top" in df
        else pd.Series(SZ_TOP_DEFAULT, index=df.index)
    )
    bot = (
        df["sz_bot"].fillna(SZ_BOT_DEFAULT)
        if "sz_bot" in df
        else pd.Series(SZ_BOT_DEFAULT, index=df.index)
    )
    mid = (top + bot) / 2
    half_h = (top - bot) / 6
    heart_x = abs_x <= HEART_X
    heart_z = (
        df["plate_z"].between(mid - half_h, mid + half_h)
        if "plate_z" in df
        else pd.Series(False, index=df.index)
    )
    heart = heart_x & heart_z
    edge = (abs_x > HEART_X) & (abs_x <= ZONE_X)

    swings = (
        df["description"].isin(
            (
                "swinging_strike",
                "swinging_strike_blocked",
                "foul",
                "foul_tip",
                "hit_into_play",
                "missed_bunt",
            )
        )
        if "description" in df
        else pd.Series(False, index=df.index)
    )

    chase_swings = swings & out_zone
    chase_rate = _safe(chase_swings.sum(), out_zone.sum())

    return pd.Series(
        {
            "Zone%": _safe(in_zone.sum(), n),
            "Edge%": _safe(edge.sum(), n),
            "Heart%": _safe(heart.sum(), n),
            "Chase-Inducing%": chase_rate,
        },
        name="location_summary",
    )
