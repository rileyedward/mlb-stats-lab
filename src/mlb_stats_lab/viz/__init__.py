"""Visualization layer — matplotlib + seaborn chart factories.

Applies the project theme on import.
"""

from __future__ import annotations

from mlb_stats_lab.viz.arsenal import pitch_movement_chart, velocity_distribution
from mlb_stats_lab.viz.distributions import (
    ev_distribution,
    la_distribution,
    velocity_box,
)
from mlb_stats_lab.viz.heatmap import zone_grid, zone_heatmap
from mlb_stats_lab.viz.rolling import rolling_metric_line
from mlb_stats_lab.viz.save import fig_to_bytes, fig_to_png, fig_to_svg
from mlb_stats_lab.viz.scatter import ev_la_scatter, pitch_location_scatter
from mlb_stats_lab.viz.splits import splits_bar_chart
from mlb_stats_lab.viz.spray import spray_chart
from mlb_stats_lab.viz.theme import (
    OUTCOME_COLORS,
    PITCH_COLORS,
    TEAM_COLORS,
    apply,
    outcome_color,
    pitch_color,
    team_color,
)
from mlb_stats_lab.viz.usage import pitch_usage_bar, pitch_usage_pie

apply()

__all__ = [
    "OUTCOME_COLORS",
    "PITCH_COLORS",
    "TEAM_COLORS",
    "apply",
    "ev_distribution",
    "ev_la_scatter",
    "fig_to_bytes",
    "fig_to_png",
    "fig_to_svg",
    "la_distribution",
    "outcome_color",
    "pitch_color",
    "pitch_location_scatter",
    "pitch_movement_chart",
    "pitch_usage_bar",
    "pitch_usage_pie",
    "rolling_metric_line",
    "splits_bar_chart",
    "spray_chart",
    "team_color",
    "velocity_box",
    "velocity_distribution",
    "zone_grid",
    "zone_heatmap",
]
