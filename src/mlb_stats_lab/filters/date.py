"""Date-based filters."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd


def _ensure_dates(df: pd.DataFrame) -> pd.Series:
    s = pd.to_datetime(df["game_date"], errors="coerce").dt.date
    return s


def by_date_range(df: pd.DataFrame, start: date | str, end: date | str) -> pd.DataFrame:
    """Inclusive ``[start, end]`` filter on ``game_date``."""
    if df.empty:
        return df
    s = date.fromisoformat(start) if isinstance(start, str) else start
    e = date.fromisoformat(end) if isinstance(end, str) else end
    dates = _ensure_dates(df)
    return df[(dates >= s) & (dates <= e)]


def since_date(df: pd.DataFrame, date_: date | str) -> pd.DataFrame:
    """Rows on or after ``date_``."""
    if df.empty:
        return df
    d = date.fromisoformat(date_) if isinstance(date_, str) else date_
    return df[_ensure_dates(df) >= d]


def last_n_days(df: pd.DataFrame, n: int, anchor: date | None = None) -> pd.DataFrame:
    """Last ``n`` days of data, ending at ``anchor`` (default: max game_date in df)."""
    if df.empty:
        return df
    dates = _ensure_dates(df)
    a = anchor or max(d for d in dates if d is not None)
    start = a - timedelta(days=max(n - 1, 0))
    return df[(dates >= start) & (dates <= a)]


def by_month(df: pd.DataFrame, month: int, year: int | None = None) -> pd.DataFrame:
    """Single-month slice."""
    if df.empty:
        return df
    parsed = pd.to_datetime(df["game_date"], errors="coerce")
    mask = parsed.dt.month == month
    if year is not None:
        mask &= parsed.dt.year == year
    return df[mask]
