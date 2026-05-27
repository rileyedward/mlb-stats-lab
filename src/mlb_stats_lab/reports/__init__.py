"""PDF report engine — Jinja2 templates → WeasyPrint output."""

from __future__ import annotations

from mlb_stats_lab.reports.assets import fig_to_data_uri, figs_to_context
from mlb_stats_lab.reports.context import (
    BatterProfileContext,
    PitcherProfileContext,
    SeriesMatchupContext,
    TeamSnapshotContext,
    build_batter_profile_context,
    build_pitcher_profile_context,
    build_series_matchup_context,
    build_team_snapshot_context,
)
from mlb_stats_lab.reports.engine import list_pdf_templates, render_html, render_report

__all__ = [
    "BatterProfileContext",
    "PitcherProfileContext",
    "SeriesMatchupContext",
    "TeamSnapshotContext",
    "build_batter_profile_context",
    "build_pitcher_profile_context",
    "build_series_matchup_context",
    "build_team_snapshot_context",
    "fig_to_data_uri",
    "figs_to_context",
    "list_pdf_templates",
    "render_html",
    "render_report",
]
