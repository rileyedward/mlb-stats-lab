"""Results per pitch type from the pitcher's perspective."""

from __future__ import annotations

import pandas as pd

from mlb_stats_lab.pitching.line import pitching_line


def results_by_pitch(df: pd.DataFrame) -> pd.DataFrame:
    """Per pitch_type: ``Whiff%``, ``CSW%``, ``BAA``, ``xwOBA-against``, ``K%``, ``BB%``, ``HR``."""
    if df is None or df.empty or "pitch_type" not in df.columns:
        return pd.DataFrame()
    total = len(df)

    rows: list[dict[str, object]] = []
    for pt, sub in df.groupby("pitch_type"):
        line = pitching_line(sub)
        desc = sub["description"].astype(str)
        swings = desc.isin(
            (
                "swinging_strike",
                "swinging_strike_blocked",
                "foul",
                "foul_tip",
                "hit_into_play",
                "missed_bunt",
            )
        )
        whiffs = desc.isin(("swinging_strike", "swinging_strike_blocked", "missed_bunt"))
        called = desc.isin(("called_strike", "automatic_strike"))
        n = len(sub)
        rows.append(
            {
                "pitch_type": pt,
                "Pitches": int(n),
                "Usage%": float(n) / float(total) if total else 0.0,
                "Whiff%": float(whiffs.sum()) / float(swings.sum()) if swings.sum() else 0.0,
                "CSW%": float(called.sum() + whiffs.sum()) / float(n) if n else 0.0,
                "BAA": float(line.get("BAA", 0.0)),
                "xwOBA-against": float(line.get("xwOBA-against", 0.0)),
                "K%": float(line.get("K%", 0.0)),
                "BB%": float(line.get("BB%", 0.0)),
                "HR": int(line.get("HR", 0)),
            }
        )
    out = pd.DataFrame(rows).set_index("pitch_type").sort_values("Usage%", ascending=False)
    return out
