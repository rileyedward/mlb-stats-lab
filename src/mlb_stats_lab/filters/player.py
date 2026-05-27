"""Player-based filters."""

from __future__ import annotations

from typing import Literal

import pandas as pd

from mlb_stats_lab.data.players import resolve_player_id


def _to_id(player: str | int) -> int:
    return int(player) if isinstance(player, int) else resolve_player_id(player)


def by_batter(df: pd.DataFrame, player: str | int) -> pd.DataFrame:
    """Rows where ``player`` batted."""
    if df.empty:
        return df
    return df[df["batter"] == _to_id(player)]


def by_pitcher(df: pd.DataFrame, player: str | int) -> pd.DataFrame:
    """Rows where ``player`` pitched."""
    if df.empty:
        return df
    return df[df["pitcher"] == _to_id(player)]


def by_batter_handedness(df: pd.DataFrame, stand: Literal["L", "R"]) -> pd.DataFrame:
    """Filter on batter handedness."""
    if df.empty:
        return df
    return df[df["stand"] == stand]


def by_pitcher_handedness(df: pd.DataFrame, throws: Literal["L", "R"]) -> pd.DataFrame:
    """Filter on pitcher handedness."""
    if df.empty:
        return df
    return df[df["p_throws"] == throws]


def vs_handedness(df: pd.DataFrame, throws: Literal["L", "R"]) -> pd.DataFrame:
    """Alias of ``by_pitcher_handedness`` — natural at call site for batter views."""
    return by_pitcher_handedness(df, throws)
