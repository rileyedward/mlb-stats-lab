"""Smoke tests for the pitching aggregators."""

from __future__ import annotations

from mlb_stats_lab.pitching import (
    arsenal_summary,
    command_metrics,
    location_summary,
    pitch_movement,
    pitching_line,
    results_by_pitch,
)
from mlb_stats_lab.pitching.splits import splits as pitching_splits
from tests.fixtures.synthetic import make_pitcher_df


def test_pitching_line_keys() -> None:
    df = make_pitcher_df()
    line = pitching_line(df)
    for key in ["BF", "IP", "K", "BB", "K%", "BB%", "K-BB%", "WHIP"]:
        assert key in line.index
    assert line["BF"] > 0


def test_arsenal_summary_sorted_by_usage() -> None:
    df = make_pitcher_df()
    out = arsenal_summary(df)
    assert not out.empty
    assert list(out["Usage%"]) == sorted(out["Usage%"], reverse=True)


def test_pitch_movement_columns() -> None:
    df = make_pitcher_df()
    m = pitch_movement(df)
    assert {"H-Mov-Mean", "H-Mov-Std", "V-Mov-Mean", "V-Mov-Std"} <= set(m.columns)


def test_location_summary_keys() -> None:
    df = make_pitcher_df()
    loc = location_summary(df)
    assert {"Zone%", "Edge%", "Heart%", "Chase-Inducing%"} <= set(loc.index)


def test_results_by_pitch_basic() -> None:
    df = make_pitcher_df()
    r = results_by_pitch(df)
    assert not r.empty
    assert "Whiff%" in r.columns
    assert "BAA" in r.columns


def test_command_metrics() -> None:
    df = make_pitcher_df()
    c = command_metrics(df)
    for key in ["First-Pitch Strike%", "Zone%", "Edge%", "Heart%", "Ball%"]:
        assert key in c.index


def test_splits_axes_all_run() -> None:
    df = make_pitcher_df()
    for axis in ["vs_hand", "home_away", "month", "times_through_order", "innings", "leverage"]:
        s = pitching_splits(df, axis=axis)  # type: ignore[arg-type]
        if not s.empty:
            assert "K%" in s.columns
