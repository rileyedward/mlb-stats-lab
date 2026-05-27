"""Statcast pitch-level data fetchers (wrappers around pybaseball)."""

from __future__ import annotations

from datetime import date
from typing import Literal

import pandas as pd

from mlb_stats_lab.data.dates import current_season_range, parse_date
from mlb_stats_lab.data.players import resolve_player_id
from mlb_stats_lab.data.teams import normalize_team

Side = Literal["batting", "pitching", "both"]


def _range(start: date | str | None, end: date | str | None) -> tuple[date, date]:
    s = parse_date(start)
    e = parse_date(end)
    if s is None or e is None:
        cs, ce = current_season_range()
        s = s or cs
        e = e or ce
    return s, e


def get_statcast(start: date | str | None = None, end: date | str | None = None) -> pd.DataFrame:
    """All Statcast pitch-level data in ``[start, end]`` (inclusive).

    Defaults to the current season opening day → today.
    """
    s, e = _range(start, end)
    try:
        from pybaseball import statcast  # type: ignore[import-untyped]

        df = statcast(start_dt=s.isoformat(), end_dt=e.isoformat(), verbose=False)
        if df is None:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


def get_statcast_batter(
    player: str,
    start: date | str | None = None,
    end: date | str | None = None,
) -> pd.DataFrame:
    """Pitches faced by ``player`` in ``[start, end]``."""
    pid = resolve_player_id(player)
    s, e = _range(start, end)
    try:
        from pybaseball import statcast_batter  # type: ignore[import-untyped]

        df = statcast_batter(s.isoformat(), e.isoformat(), pid)
        if df is None:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


def get_statcast_pitcher(
    player: str,
    start: date | str | None = None,
    end: date | str | None = None,
) -> pd.DataFrame:
    """Pitches thrown by ``player`` in ``[start, end]``."""
    pid = resolve_player_id(player)
    s, e = _range(start, end)
    try:
        from pybaseball import statcast_pitcher  # type: ignore[import-untyped]

        df = statcast_pitcher(s.isoformat(), e.isoformat(), pid)
        if df is None:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


def get_statcast_for_team(
    team: str,
    start: date | str | None = None,
    end: date | str | None = None,
    side: Side = "both",
) -> pd.DataFrame:
    """All pitches in games where ``team`` was batting, pitching, or either.

    Adds two helper columns:
        - ``_team_batting``: 3-letter abbreviation of the batting team for the row.
        - ``_team_pitching``: 3-letter abbreviation of the pitching team for the row.
    Filters down to rows where ``team`` matches the chosen ``side``.
    """
    abbrev = normalize_team(team)
    df = get_statcast(start, end)
    if df.empty:
        return df

    is_top = df["inning_topbot"].astype(str).str.lower().str.startswith("top")
    batting = pd.Series(df["home_team"].where(~is_top, df["away_team"]).values, index=df.index)
    pitching = pd.Series(df["home_team"].where(is_top, df["away_team"]).values, index=df.index)
    df = df.copy()
    df["_team_batting"] = batting
    df["_team_pitching"] = pitching

    if side == "batting":
        return df[df["_team_batting"] == abbrev]
    if side == "pitching":
        return df[df["_team_pitching"] == abbrev]
    return df[(df["_team_batting"] == abbrev) | (df["_team_pitching"] == abbrev)]


def get_statcast_for_game(game_pk: int) -> pd.DataFrame:
    """All pitches from a single Statcast game."""
    try:
        from pybaseball import statcast_single_game  # type: ignore[import-untyped]

        df = statcast_single_game(int(game_pk))
        if df is None:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()
