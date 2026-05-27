"""Smoke tests for filter helpers."""

from __future__ import annotations

from mlb_stats_lab.filters import (
    breaking_balls,
    by_pitch_type,
    by_team,
    fastballs,
    first_pitch,
    in_zone,
    only_completed_pa,
    only_in_play,
    out_of_zone,
    two_strike_counts,
)
from tests.fixtures.synthetic import make_batter_df


def test_by_pitch_type_subset() -> None:
    df = make_batter_df()
    sub = by_pitch_type(df, "FF")
    assert (sub["pitch_type"] == "FF").all()


def test_fastballs_breaking_balls() -> None:
    df = make_batter_df()
    fb = fastballs(df)
    bb = breaking_balls(df)
    assert set(fb["pitch_type"]).issubset({"FF", "SI", "FC", "FS"})
    assert set(bb["pitch_type"]).issubset({"SL", "ST", "SV", "CU", "KC"})


def test_zone_partition() -> None:
    df = make_batter_df()
    iz = in_zone(df)
    oz = out_of_zone(df)
    assert len(iz) + len(oz) <= len(df)


def test_only_in_play_only_completed() -> None:
    df = make_batter_df()
    ip = only_in_play(df)
    assert (ip["type"] == "X").all()
    cp = only_completed_pa(df)
    assert cp["events"].notna().all()


def test_count_filters() -> None:
    df = make_batter_df()
    fp = first_pitch(df)
    assert ((fp["balls"] == 0) & (fp["strikes"] == 0)).all()
    ts = two_strike_counts(df)
    assert (ts["strikes"] == 2).all()


def test_by_team_side_pitching() -> None:
    df = make_batter_df()
    # Force columns so by_team can compute.
    sub = by_team(df, "SEA", side="batting")
    assert not sub.empty


def test_pipe_composition() -> None:
    df = make_batter_df()
    out = df.pipe(fastballs).pipe(two_strike_counts)
    assert (out["pitch_type"].isin({"FF", "SI", "FC", "FS"})).all()
    assert (out["strikes"] == 2).all()
