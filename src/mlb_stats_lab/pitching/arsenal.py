"""Pitcher arsenal summary — usage / velo / movement per pitch type."""

from __future__ import annotations

import pandas as pd


def arsenal_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per pitch_type: ``Count``, ``Usage%``, velo, spin, movement, extension, release."""
    if df is None or df.empty or "pitch_type" not in df.columns:
        return pd.DataFrame()
    total = len(df)

    rows: list[dict[str, object]] = []
    for pt, sub in df.groupby("pitch_type"):
        rows.append(
            {
                "pitch_type": pt,
                "Count": len(sub),
                "Usage%": float(len(sub)) / float(total) if total else 0.0,
                "Avg Velo": float(sub["release_speed"].dropna().mean())
                if "release_speed" in sub
                else 0.0,
                "Max Velo": float(sub["release_speed"].dropna().max())
                if "release_speed" in sub
                else 0.0,
                "Avg Spin": float(sub["release_spin_rate"].dropna().mean())
                if "release_spin_rate" in sub
                else 0.0,
                "Avg pfx_x": float(sub["pfx_x"].dropna().mean()) if "pfx_x" in sub else 0.0,
                "Avg pfx_z": float(sub["pfx_z"].dropna().mean()) if "pfx_z" in sub else 0.0,
                "Avg Extension": float(sub["release_extension"].dropna().mean())
                if "release_extension" in sub
                else 0.0,
                "Avg Release Height": float(sub["release_pos_z"].dropna().mean())
                if "release_pos_z" in sub
                else 0.0,
            }
        )
    out = pd.DataFrame(rows).set_index("pitch_type").sort_values("Usage%", ascending=False)
    return out
