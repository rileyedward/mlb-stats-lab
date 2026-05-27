"""Plate discipline metrics — pitch-level."""

from __future__ import annotations

import pandas as pd

from mlb_stats_lab.filters.result import (
    CALLED_DESCRIPTIONS,
    SWING_DESCRIPTIONS,
)

WHIFF_DESCRIPTIONS = ("swinging_strike", "swinging_strike_blocked", "missed_bunt")
CONTACT_DESCRIPTIONS = (
    "foul",
    "foul_tip",
    "foul_bunt",
    "hit_into_play",
    "hit_into_play_score",
    "hit_into_play_no_out",
)
CALLED_STRIKE_DESCRIPTIONS = ("called_strike", "automatic_strike")


def _safe(num: float, den: float) -> float:
    return float(num) / float(den) if den else 0.0


def plate_discipline(df: pd.DataFrame) -> pd.Series:
    """Plate-discipline metrics keyed by stat name."""
    if df is None or df.empty:
        return pd.Series(dtype="float64", name="plate_discipline")

    desc = df["description"].astype(str)
    n = len(df)

    swings = desc.isin(SWING_DESCRIPTIONS)
    contact = desc.isin(CONTACT_DESCRIPTIONS)
    whiffs = desc.isin(WHIFF_DESCRIPTIONS)
    called = desc.isin(CALLED_DESCRIPTIONS)
    called_strikes = desc.isin(CALLED_STRIKE_DESCRIPTIONS)

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

    swing_pct = _safe(swings.sum(), n)
    z_swing = _safe((swings & in_zone).sum(), in_zone.sum())
    o_swing = _safe((swings & out_zone).sum(), out_zone.sum())

    contact_pct = _safe(contact.sum(), swings.sum())
    z_contact = _safe((contact & in_zone).sum(), (swings & in_zone).sum())
    o_contact = _safe((contact & out_zone).sum(), (swings & out_zone).sum())

    whiff_pct = _safe(whiffs.sum(), swings.sum())
    swstr_pct = _safe(whiffs.sum(), n)
    csw_pct = _safe(called_strikes.sum() + whiffs.sum(), n)
    z_pct = _safe(in_zone.sum(), n)

    first = (
        df[(df["balls"] == 0) & (df["strikes"] == 0)]
        if "balls" in df and "strikes" in df
        else df.iloc[0:0]
    )
    fps = pd.Series(False, index=first.index)
    if not first.empty:
        fps = first["description"].isin(CALLED_STRIKE_DESCRIPTIONS) | first["type"].isin(["S", "X"])
    fp_strike_pct = _safe(fps.sum(), len(first))

    data = {
        "Pitches": n,
        "Swing%": swing_pct,
        "Z-Swing%": z_swing,
        "O-Swing%": o_swing,
        "Chase%": o_swing,
        "Contact%": contact_pct,
        "Z-Contact%": z_contact,
        "O-Contact%": o_contact,
        "Whiff%": whiff_pct,
        "SwStr%": swstr_pct,
        "CSW%": csw_pct,
        "Z%": z_pct,
        "First-Pitch Strike%": fp_strike_pct,
    }
    return pd.Series(data, name="plate_discipline")
