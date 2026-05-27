"""``performance_by_pitch_type`` — slash + EV/LA per pitch type."""

from __future__ import annotations

import pandas as pd

from mlb_stats_lab.batting.line import batting_line


def performance_by_pitch_type(df: pd.DataFrame) -> pd.DataFrame:
    """Group by ``pitch_type`` → key offensive metrics per pitch.

    Columns: ``Pitches``, ``Whiff%``, ``AVG``, ``SLG``, ``xwOBA``, ``Avg EV``, ``Avg LA``.
    Sorted by most-seen first.
    """
    if df is None or df.empty or "pitch_type" not in df.columns:
        return pd.DataFrame()

    rows: list[dict[str, object]] = []
    for pt, sub in df.groupby("pitch_type"):
        line = batting_line(sub)
        in_play = sub[sub["type"] == "X"] if "type" in sub else sub
        ev = float(in_play["launch_speed"].dropna().mean()) if "launch_speed" in in_play else 0.0
        la = float(in_play["launch_angle"].dropna().mean()) if "launch_angle" in in_play else 0.0

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
        whiff_pct = float(whiffs.sum()) / float(swings.sum()) if swings.sum() else 0.0

        rows.append(
            {
                "pitch_type": pt,
                "Pitches": len(sub),
                "Whiff%": whiff_pct,
                "AVG": float(line.get("AVG", 0.0)),
                "SLG": float(line.get("SLG", 0.0)),
                "xwOBA": float(line.get("xwOBA", 0.0)),
                "Avg EV": ev,
                "Avg LA": la,
            }
        )

    out = pd.DataFrame(rows).set_index("pitch_type").sort_values("Pitches", ascending=False)
    return out
