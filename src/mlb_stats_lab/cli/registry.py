"""Template registry — bridges CLI names to notebook + PDF + builders."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mlb_stats_lab.config import get_config
from mlb_stats_lab.reports.context import (
    build_batter_profile_context,
    build_pitcher_profile_context,
    build_series_matchup_context,
    build_team_snapshot_context,
)


@dataclass(frozen=True)
class TemplateSpec:
    name: str
    description: str
    parameter_keys: list[str]
    builder: Callable[[dict[str, Any]], Any]

    @property
    def notebook_path(self) -> Path:
        return get_config().paths.notebook_templates_dir / f"{self.name}.ipynb"


TEMPLATES: dict[str, TemplateSpec] = {
    "batter-profile": TemplateSpec(
        name="batter-profile",
        description="Single-hitter deep dive",
        parameter_keys=["player", "season", "start_date", "end_date", "recent_form_pas"],
        builder=build_batter_profile_context,
    ),
    "pitcher-profile": TemplateSpec(
        name="pitcher-profile",
        description="Single-pitcher deep dive",
        parameter_keys=["player", "season", "start_date", "end_date", "recent_form_starts"],
        builder=build_pitcher_profile_context,
    ),
    "team-season-snapshot": TemplateSpec(
        name="team-season-snapshot",
        description="Team state-of-the-union",
        parameter_keys=["team", "season", "start_date", "end_date", "recent_window_games"],
        builder=build_team_snapshot_context,
    ),
    "series-matchup": TemplateSpec(
        name="series-matchup",
        description="Two-team series matchup",
        parameter_keys=[
            "team_a",
            "team_b",
            "season",
            "start_date",
            "end_date",
            "recent_form_games",
        ],
        builder=build_series_matchup_context,
    ),
}


def get(name: str) -> TemplateSpec:
    if name not in TEMPLATES:
        raise KeyError(name)
    return TEMPLATES[name]


def names() -> list[str]:
    return sorted(TEMPLATES.keys())
