"""Result-based filters (in play, swings, hits, walks, etc.)."""

from __future__ import annotations

import pandas as pd

SWING_DESCRIPTIONS = (
    "swinging_strike",
    "swinging_strike_blocked",
    "foul",
    "foul_tip",
    "foul_bunt",
    "hit_into_play",
    "hit_into_play_score",
    "hit_into_play_no_out",
    "missed_bunt",
)

CALLED_DESCRIPTIONS = (
    "ball",
    "called_strike",
    "blocked_ball",
    "pitchout",
    "intent_ball",
    "automatic_ball",
    "automatic_strike",
)

HIT_EVENTS = ("single", "double", "triple", "home_run")
STRIKEOUT_EVENTS = ("strikeout", "strikeout_double_play")


def only_in_play(df: pd.DataFrame) -> pd.DataFrame:
    """``type == 'X'`` (ball put in play, regardless of outcome)."""
    if df.empty:
        return df
    return df[df["type"] == "X"]


def only_swings(df: pd.DataFrame) -> pd.DataFrame:
    """Pitches the batter swung at."""
    if df.empty:
        return df
    return df[df["description"].isin(SWING_DESCRIPTIONS)]


def only_called_pitches(df: pd.DataFrame) -> pd.DataFrame:
    """Pitches the batter did NOT swing at."""
    if df.empty:
        return df
    return df[df["description"].isin(CALLED_DESCRIPTIONS)]


def only_hits(df: pd.DataFrame) -> pd.DataFrame:
    """events ∈ single/double/triple/home_run."""
    if df.empty:
        return df
    return df[df["events"].isin(HIT_EVENTS)]


def only_walks(df: pd.DataFrame) -> pd.DataFrame:
    """events == 'walk'."""
    if df.empty:
        return df
    return df[df["events"] == "walk"]


def only_strikeouts(df: pd.DataFrame) -> pd.DataFrame:
    """events ∈ strikeout/strikeout_double_play."""
    if df.empty:
        return df
    return df[df["events"].isin(STRIKEOUT_EVENTS)]


def only_completed_pa(df: pd.DataFrame) -> pd.DataFrame:
    """Last pitch of each PA (``events`` notnull)."""
    if df.empty:
        return df
    return df[df["events"].notna()]
