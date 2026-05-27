"""Data layer — only place that talks to pybaseball directly.

Enables the pybaseball Parquet cache at import time so notebooks "just work".
"""

from __future__ import annotations

from mlb_stats_lab.data.cache import disable, enable_default, flush
from mlb_stats_lab.data.dates import (
    current_season,
    current_season_range,
    last_n_days,
    opening_day,
    parse_date,
    regular_season_end,
    season_range,
)
from mlb_stats_lab.data.exceptions import (
    AmbiguousPlayerError,
    Candidate,
    UnknownPlayerError,
    UnknownTeamError,
)
from mlb_stats_lab.data.players import player_name, resolve_player_id, team_roster
from mlb_stats_lab.data.season import (
    get_standings,
    get_team_batting,
    get_team_pitching,
)
from mlb_stats_lab.data.statcast import (
    get_statcast,
    get_statcast_batter,
    get_statcast_for_game,
    get_statcast_for_team,
    get_statcast_pitcher,
)
from mlb_stats_lab.data.teams import TEAMS, TeamInfo, normalize_team, team_schedule

# Enable pybaseball cache once, on import.
enable_default()

__all__ = [
    "TEAMS",
    "AmbiguousPlayerError",
    "Candidate",
    "TeamInfo",
    "UnknownPlayerError",
    "UnknownTeamError",
    "current_season",
    "current_season_range",
    "disable",
    "enable_default",
    "flush",
    "get_standings",
    "get_statcast",
    "get_statcast_batter",
    "get_statcast_for_game",
    "get_statcast_for_team",
    "get_statcast_pitcher",
    "get_team_batting",
    "get_team_pitching",
    "last_n_days",
    "normalize_team",
    "opening_day",
    "parse_date",
    "player_name",
    "regular_season_end",
    "resolve_player_id",
    "season_range",
    "team_roster",
    "team_schedule",
]
