"""Situational filters (inning, baserunners, leverage)."""

from __future__ import annotations

import pandas as pd


def by_inning(df: pd.DataFrame, *innings: int) -> pd.DataFrame:
    """One or more inning numbers."""
    if df.empty or not innings:
        return df
    return df[df["inning"].isin(innings)]


def early_innings(df: pd.DataFrame) -> pd.DataFrame:
    """Innings 1–3."""
    if df.empty:
        return df
    return df[df["inning"].between(1, 3, inclusive="both")]


def middle_innings(df: pd.DataFrame) -> pd.DataFrame:
    """Innings 4–6."""
    if df.empty:
        return df
    return df[df["inning"].between(4, 6, inclusive="both")]


def late_innings(df: pd.DataFrame) -> pd.DataFrame:
    """Innings 7+."""
    if df.empty:
        return df
    return df[df["inning"] >= 7]


def _runner_cols(df: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    return (
        df["on_1b"].notna() if "on_1b" in df else pd.Series(False, index=df.index),
        df["on_2b"].notna() if "on_2b" in df else pd.Series(False, index=df.index),
        df["on_3b"].notna() if "on_3b" in df else pd.Series(False, index=df.index),
    )


def with_runners_on(df: pd.DataFrame) -> pd.DataFrame:
    """Any of ``on_1b``, ``on_2b``, ``on_3b`` populated."""
    if df.empty:
        return df
    a, b, c = _runner_cols(df)
    return df[a | b | c]


def bases_empty(df: pd.DataFrame) -> pd.DataFrame:
    """All bases empty."""
    if df.empty:
        return df
    a, b, c = _runner_cols(df)
    return df[~(a | b | c)]


def risp(df: pd.DataFrame) -> pd.DataFrame:
    """Runners in scoring position (2nd or 3rd)."""
    if df.empty:
        return df
    _, b, c = _runner_cols(df)
    return df[b | c]


def close_game(df: pd.DataFrame, run_diff: int = 3) -> pd.DataFrame:
    """``abs(bat_score - fld_score) <= run_diff``."""
    if df.empty:
        return df
    diff = (df["bat_score"] - df["fld_score"]).abs()
    return df[diff <= run_diff]


def high_leverage(df: pd.DataFrame) -> pd.DataFrame:
    """Late innings AND close game."""
    return close_game(late_innings(df))
