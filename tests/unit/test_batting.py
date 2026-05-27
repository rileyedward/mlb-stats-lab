"""Smoke tests for the batting aggregators on a synthetic DataFrame."""

from __future__ import annotations

from mlb_stats_lab.batting import (
    batting_line,
    contact_quality,
    performance_by_pitch_type,
    plate_discipline,
)
from mlb_stats_lab.batting.splits import splits as batting_splits
from tests.fixtures.synthetic import make_batter_df


def test_batting_line_returns_expected_keys() -> None:
    df = make_batter_df()
    line = batting_line(df)
    for key in ["PA", "AB", "H", "HR", "BB", "SO", "AVG", "OBP", "SLG", "OPS", "wOBA"]:
        assert key in line.index
    assert line["PA"] > 0
    assert 0 <= line["AVG"] <= 1


def test_plate_discipline_keys() -> None:
    df = make_batter_df()
    disc = plate_discipline(df)
    for key in ["Swing%", "Chase%", "Whiff%", "Contact%", "CSW%", "Z%"]:
        assert key in disc.index


def test_contact_quality_returns_nonnull() -> None:
    df = make_batter_df()
    c = contact_quality(df)
    assert c["BBE"] > 0
    assert c["Avg EV (mph)"] > 0


def test_performance_by_pitch_type_sorted() -> None:
    df = make_batter_df()
    out = performance_by_pitch_type(df)
    assert not out.empty
    assert list(out["Pitches"]) == sorted(out["Pitches"], reverse=True)


def test_splits_runs_for_every_axis() -> None:
    df = make_batter_df()
    for axis in [
        "vs_hand",
        "home_away",
        "month",
        "count_state",
        "two_strike",
        "leverage",
        "innings",
    ]:
        s = batting_splits(df, axis=axis)  # type: ignore[arg-type]
        # Either empty or has batting_line columns.
        if not s.empty:
            assert "wOBA" in s.columns
