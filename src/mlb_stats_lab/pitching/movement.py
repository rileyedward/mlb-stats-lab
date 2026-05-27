"""Pitch movement summary (mean + stdev per pitch type)."""

from __future__ import annotations

import pandas as pd


def pitch_movement(df: pd.DataFrame) -> pd.DataFrame:
    """Per pitch_type, mean and stdev of horizontal/vertical break.

    Columns: ``H-Mov-Mean``, ``H-Mov-Std``, ``V-Mov-Mean``, ``V-Mov-Std``.
    Movement values are in feet (Statcast's native unit).
    """
    if df is None or df.empty or "pitch_type" not in df.columns:
        return pd.DataFrame()

    grouped = df.groupby("pitch_type")
    out = pd.DataFrame(
        {
            "H-Mov-Mean": grouped["pfx_x"].mean(),
            "H-Mov-Std": grouped["pfx_x"].std(),
            "V-Mov-Mean": grouped["pfx_z"].mean(),
            "V-Mov-Std": grouped["pfx_z"].std(),
        }
    ).fillna(0.0)
    return out
