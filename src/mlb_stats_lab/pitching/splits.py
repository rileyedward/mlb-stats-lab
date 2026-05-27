"""Pitcher splits — group by an axis, run ``pitching_line`` per bucket."""

from __future__ import annotations

from typing import Literal

import pandas as pd

from mlb_stats_lab.pitching.line import pitching_line

Axis = Literal[
    "vs_hand",
    "home_away",
    "month",
    "times_through_order",
    "innings",
    "leverage",
]


def _times_through_order(df: pd.DataFrame) -> pd.Series:
    """Approximate Times-Through-Order per pitch.

    For each (game_pk, pitcher), order completed PAs by at_bat_number and assign
    TTO = 1 for the first 9 unique batters faced, 2 for the next 9, 3 for the rest.
    """
    if df.empty:
        return pd.Series(dtype="int64", index=df.index)

    tto = pd.Series(0, index=df.index, dtype="int64")
    for (_game, _pitcher), sub in df.groupby(["game_pk", "pitcher"], sort=False):
        order_pairs = (
            sub[sub["events"].notna()]
            .sort_values("at_bat_number")
            .loc[:, ["at_bat_number", "batter"]]
            .drop_duplicates(subset="at_bat_number")
        )
        seen: list[int] = []
        ab_to_tto: dict[int, int] = {}
        for _, row in order_pairs.iterrows():
            b = int(row["batter"])
            if b not in seen:
                seen.append(b)
            count = sum(1 for x in seen if x == b)
            ab_to_tto[int(row["at_bat_number"])] = min(count, 3)
        tto.loc[sub.index] = sub["at_bat_number"].map(ab_to_tto).fillna(1).astype("int64")
    return tto


def _bucketize(df: pd.DataFrame, axis: Axis) -> dict[str, pd.DataFrame]:
    buckets: dict[str, pd.DataFrame] = {}
    if axis == "vs_hand":
        for hand, label in (("L", "vs LHB"), ("R", "vs RHB")):
            buckets[label] = df[df["stand"] == hand]
    elif axis == "home_away":
        is_top = df["inning_topbot"].astype(str).str.lower().str.startswith("top")
        # pitcher home = top-of-inning rows
        buckets["Home"] = df[is_top]
        buckets["Away"] = df[~is_top]
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
    elif axis == "times_through_order":
        tto = _times_through_order(df)
        for n in (1, 2, 3):
            buckets[f"TTO {n}"] = df[tto == n]
    elif axis == "innings":
        buckets["Early (1-3)"] = df[df["inning"].between(1, 3, inclusive="both")]
        buckets["Middle (4-6)"] = df[df["inning"].between(4, 6, inclusive="both")]
        buckets["Late (7+)"] = df[df["inning"] >= 7]
    elif axis == "leverage":
        late = df["inning"] >= 7
        close = (df["bat_score"] - df["fld_score"]).abs() <= 3
        buckets["High"] = df[late & close]
        buckets["Other"] = df[~(late & close)]
    return buckets


def splits(df: pd.DataFrame, axis: Axis) -> pd.DataFrame:
    """Run ``pitching_line`` per bucket of the chosen ``axis``."""
    if df is None or df.empty:
        return pd.DataFrame()
    rows: list[pd.Series] = []
    labels: list[str] = []
    for label, sub in _bucketize(df, axis).items():
        labels.append(label)
        rows.append(pitching_line(sub))
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows, index=labels)
    out.index.name = axis
    return out
