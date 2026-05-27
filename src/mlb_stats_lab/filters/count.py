"""Count-state filters."""

from __future__ import annotations

from typing import Literal

import pandas as pd

Perspective = Literal["batter", "pitcher"]


def by_count(df: pd.DataFrame, balls: int, strikes: int) -> pd.DataFrame:
    """Specific count, e.g. ``(3, 2)``."""
    if df.empty:
        return df
    return df[(df["balls"] == balls) & (df["strikes"] == strikes)]


def ahead_in_count(df: pd.DataFrame, perspective: Perspective) -> pd.DataFrame:
    """Batter ahead: balls > strikes. Pitcher ahead: strikes > balls."""
    if df.empty:
        return df
    if perspective == "batter":
        return df[df["balls"] > df["strikes"]]
    return df[df["strikes"] > df["balls"]]


def behind_in_count(df: pd.DataFrame, perspective: Perspective) -> pd.DataFrame:
    """Inverse of :func:`ahead_in_count`."""
    if df.empty:
        return df
    if perspective == "batter":
        return df[df["balls"] < df["strikes"]]
    return df[df["strikes"] < df["balls"]]


def even_count(df: pd.DataFrame) -> pd.DataFrame:
    """0-0, 1-1, 2-2."""
    if df.empty:
        return df
    return df[df["balls"] == df["strikes"]]


def two_strike_counts(df: pd.DataFrame) -> pd.DataFrame:
    """``strikes == 2``."""
    if df.empty:
        return df
    return df[df["strikes"] == 2]


def three_ball_counts(df: pd.DataFrame) -> pd.DataFrame:
    """``balls == 3``."""
    if df.empty:
        return df
    return df[df["balls"] == 3]


def first_pitch(df: pd.DataFrame) -> pd.DataFrame:
    """``balls == 0 and strikes == 0``."""
    if df.empty:
        return df
    return df[(df["balls"] == 0) & (df["strikes"] == 0)]


def full_count(df: pd.DataFrame) -> pd.DataFrame:
    """3-2."""
    return by_count(df, 3, 2)
