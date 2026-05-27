"""Team-based filters."""

from __future__ import annotations

from typing import Literal

import pandas as pd

from mlb_stats_lab.data.teams import normalize_team

Side = Literal["batting", "pitching", "both"]


def _batting_pitching_series(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Return (batting_team, pitching_team) Series for each row."""
    if "_team_batting" in df.columns and "_team_pitching" in df.columns:
        return df["_team_batting"], df["_team_pitching"]
    is_top = df["inning_topbot"].astype(str).str.lower().str.startswith("top")
    batting = df["home_team"].where(~is_top, df["away_team"])
    pitching = df["home_team"].where(is_top, df["away_team"])
    return batting, pitching


def by_team(df: pd.DataFrame, team: str, side: Side = "both") -> pd.DataFrame:
    """Rows where ``team`` was batting, pitching, or either."""
    if df.empty:
        return df
    abbrev = normalize_team(team)
    batting, pitching = _batting_pitching_series(df)
    if side == "batting":
        return df[batting == abbrev]
    if side == "pitching":
        return df[pitching == abbrev]
    return df[(batting == abbrev) | (pitching == abbrev)]


def vs_team(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """Rows where the opponent (home or away) is ``team``. Assumes df is
    already scoped to a single subject team."""
    if df.empty:
        return df
    abbrev = normalize_team(team)
    return df[(df["home_team"] == abbrev) | (df["away_team"] == abbrev)]


def home_games_for(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """Rows where ``team`` is the home team."""
    if df.empty:
        return df
    return df[df["home_team"] == normalize_team(team)]


def away_games_for(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """Rows where ``team`` is the away team."""
    if df.empty:
        return df
    return df[df["away_team"] == normalize_team(team)]
