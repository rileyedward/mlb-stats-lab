"""Season-level Fangraphs-backed team aggregates."""

from __future__ import annotations

import pandas as pd

from mlb_stats_lab.data.dates import current_season


def get_team_batting(year: int | None = None) -> pd.DataFrame:
    """Fangraphs season-level team batting. Year defaults to current."""
    yr = year or current_season()
    try:
        from pybaseball import team_batting  # type: ignore[import-untyped]

        df = team_batting(yr)
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def get_team_pitching(year: int | None = None) -> pd.DataFrame:
    """Fangraphs season-level team pitching."""
    yr = year or current_season()
    try:
        from pybaseball import team_pitching  # type: ignore[import-untyped]

        df = team_pitching(yr)
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def get_standings(year: int | None = None) -> pd.DataFrame:
    """Division standings as a single concatenated DataFrame."""
    yr = year or current_season()
    try:
        from pybaseball import standings  # type: ignore[import-untyped]

        result = standings(yr)
        if result is None:
            return pd.DataFrame()
        if isinstance(result, list):
            frames = []
            for i, frame in enumerate(result):
                if frame is None or getattr(frame, "empty", False):
                    continue
                f = frame.copy()
                f["division_index"] = i
                frames.append(f)
            return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        return result
    except Exception:
        return pd.DataFrame()
