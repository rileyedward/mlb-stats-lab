"""Smoke tests for the notebook display helpers."""

from __future__ import annotations

import pandas as pd

from mlb_stats_lab.viz.display import metric_row, report_header, section, stat_table


def test_report_header_uses_team_color() -> None:
    html = report_header("Aaron Judge", "2024", team="NYY")._repr_html_()
    assert "#003087" in html  # NYY primary
    assert "Aaron Judge" in html


def test_section_renders_title() -> None:
    assert "Season Line" in section("Season Line")._repr_html_()


def test_metric_row_formats_values() -> None:
    html = metric_row({"AVG": 0.288, "HR": 42, "wOBA": None})._repr_html_()
    assert ".288" in html
    assert "42" in html
    assert "—" in html  # None → em dash


def test_stat_table_returns_styler() -> None:
    s = pd.Series({"PA": 100, "AVG": 0.288})
    out = stat_table(s, "Line").to_html()
    assert ".288" in out
    assert "Line" in out
