"""Smoke tests for viz helpers — assert ``Figure`` returns."""

from __future__ import annotations

from matplotlib.figure import Figure

from mlb_stats_lab.batting.rolling import rolling_batting_line
from mlb_stats_lab.batting.splits import splits as batting_splits
from mlb_stats_lab.viz import (
    ev_distribution,
    ev_la_scatter,
    la_distribution,
    pitch_location_scatter,
    pitch_movement_chart,
    pitch_usage_bar,
    pitch_usage_pie,
    rolling_metric_line,
    splits_bar_chart,
    spray_chart,
    velocity_box,
    velocity_distribution,
    zone_grid,
    zone_heatmap,
)
from tests.fixtures.synthetic import make_batter_df


def test_charts_return_figure() -> None:
    df = make_batter_df()
    assert isinstance(spray_chart(df), Figure)
    assert isinstance(zone_heatmap(df, metric="density"), Figure)
    assert isinstance(zone_heatmap(df, metric="whiff_rate"), Figure)
    assert isinstance(zone_grid(df, metric="xwoba"), Figure)
    assert isinstance(pitch_location_scatter(df), Figure)
    assert isinstance(ev_la_scatter(df), Figure)
    assert isinstance(pitch_movement_chart(df), Figure)
    assert isinstance(velocity_distribution(df), Figure)
    assert isinstance(pitch_usage_bar(df), Figure)
    assert isinstance(pitch_usage_pie(df), Figure)
    assert isinstance(ev_distribution(df), Figure)
    assert isinstance(la_distribution(df), Figure)
    assert isinstance(velocity_box(df), Figure)


def test_rolling_and_splits_charts() -> None:
    df = make_batter_df()
    r = rolling_batting_line(df, window=10)
    if not r.empty:
        assert isinstance(rolling_metric_line(r, metric="wOBA"), Figure)
    s = batting_splits(df, axis="vs_hand")
    if not s.empty:
        assert isinstance(splits_bar_chart(s, metric="wOBA"), Figure)
