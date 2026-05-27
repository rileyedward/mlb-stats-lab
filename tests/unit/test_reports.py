"""Tests for the report engine (template loading + Jinja filters)."""

from __future__ import annotations

from mlb_stats_lab.reports.engine import list_pdf_templates
from mlb_stats_lab.reports.filters import fmt_avg, fmt_int, fmt_pct


def test_pdf_templates_discoverable() -> None:
    names = list_pdf_templates()
    assert {"batter-profile", "pitcher-profile", "series-matchup", "team-season-snapshot"} <= set(
        names
    )


def test_filter_fmt_avg() -> None:
    assert fmt_avg(0.288) == ".288"
    assert fmt_avg(None) == "—"


def test_filter_fmt_pct() -> None:
    assert fmt_pct(0.224) == "22.4%"
    assert fmt_pct(0.5) == "50.0%"


def test_filter_fmt_int() -> None:
    assert fmt_int(231) == "231"
    assert fmt_int(231.4) == "231"
