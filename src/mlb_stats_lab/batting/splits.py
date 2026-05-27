"""Batter splits — group by an axis, run ``batting_line`` per bucket."""

from __future__ import annotations

from typing import Literal

import pandas as pd

from mlb_stats_lab.batting.line import batting_line

Axis = Literal[
    "vs_hand",
    "home_away",
    "month",
    "count_state",
    "two_strike",
    "leverage",
    "innings",
]


def _bucketize(df: pd.DataFrame, axis: Axis) -> dict[str, pd.DataFrame]:
    buckets: dict[str, pd.DataFrame] = {}
    if axis == "vs_hand":
        for hand, label in (("L", "vs LHP"), ("R", "vs RHP")):
            buckets[label] = df[df["p_throws"] == hand]
    elif axis == "home_away":
        is_top = df["inning_topbot"].astype(str).str.lower().str.startswith("top")
        # batter home = bottom-of-inning rows (home team bats in bottom)
        buckets["Home"] = df[~is_top]
        buckets["Away"] = df[is_top]
    elif axis == "month":
        parsed = pd.to_datetime(df["game_date"], errors="coerce")
        for month in sorted(set(parsed.dt.month.dropna().astype(int))):
            name = [
                "",
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ][month]
            buckets[name] = df[parsed.dt.month == month]
    elif axis == "count_state":
        ahead = df["balls"] > df["strikes"]
        behind = df["balls"] < df["strikes"]
        buckets["Ahead"] = df[ahead]
        buckets["Even"] = df[~ahead & ~behind]
        buckets["Behind"] = df[behind]
    elif axis == "two_strike":
        buckets["Two-strike"] = df[df["strikes"] == 2]
        buckets["Other"] = df[df["strikes"] != 2]
    elif axis == "leverage":
        late = df["inning"] >= 7
        close = (df["bat_score"] - df["fld_score"]).abs() <= 3
        high = late & close
        buckets["High"] = df[high]
        buckets["Other"] = df[~high]
    elif axis == "innings":
        buckets["Early (1-3)"] = df[df["inning"].between(1, 3, inclusive="both")]
        buckets["Middle (4-6)"] = df[df["inning"].between(4, 6, inclusive="both")]
        buckets["Late (7+)"] = df[df["inning"] >= 7]
    return buckets


def splits(df: pd.DataFrame, axis: Axis) -> pd.DataFrame:
    """Run ``batting_line`` per bucket of the chosen ``axis``.

    Returns a DataFrame indexed by bucket label with ``batting_line`` columns.
    """
    if df is None or df.empty:
        return pd.DataFrame()
    rows = []
    labels = []
    for label, sub in _bucketize(df, axis).items():
        labels.append(label)
        rows.append(batting_line(sub))
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows, index=labels)
    out.index.name = axis
    return out
