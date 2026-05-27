"""Tests for ``mlb_stats_lab.data.dates``."""

from __future__ import annotations

from datetime import date

from mlb_stats_lab.data import dates


def test_opening_day_table_present() -> None:
    assert dates.opening_day(2024) == date(2024, 3, 28)
    assert dates.opening_day(2026) == date(2026, 3, 26)


def test_opening_day_heuristic_fallback() -> None:
    od = dates.opening_day(2099)
    assert od.month == 3
    assert od.weekday() == 3  # Thursday


def test_last_n_days() -> None:
    anchor = date(2024, 6, 10)
    start, end = dates.last_n_days(7, anchor=anchor)
    assert end == anchor
    assert (anchor - start).days == 6


def test_season_range_clamps_to_today() -> None:
    today = date.today()
    od, end = dates.season_range(today.year - 1)
    assert od <= end


def test_parse_date_handles_strings_and_none() -> None:
    assert dates.parse_date(None) is None
    assert dates.parse_date("2024-04-01") == date(2024, 4, 1)
    assert dates.parse_date(date(2024, 4, 1)) == date(2024, 4, 1)
