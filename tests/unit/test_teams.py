"""Tests for ``mlb_stats_lab.data.teams.normalize_team``."""

from __future__ import annotations

import pytest

from mlb_stats_lab.data.exceptions import UnknownTeamError
from mlb_stats_lab.data.teams import TEAMS, normalize_team


def test_all_30_teams_registered() -> None:
    assert len(TEAMS) == 30


def test_normalize_abbreviation_case_insensitive() -> None:
    assert normalize_team("SEA") == "SEA"
    assert normalize_team("sea") == "SEA"


def test_normalize_nickname() -> None:
    assert normalize_team("Mariners") == "SEA"
    assert normalize_team("Dodgers") == "LAD"
    assert normalize_team("blue jays") == "TOR"


def test_normalize_full_name() -> None:
    assert normalize_team("Seattle Mariners") == "SEA"
    assert normalize_team("New York Yankees") == "NYY"


def test_normalize_alias_athletics() -> None:
    assert normalize_team("OAK") == "ATH"
    assert normalize_team("Athletics") == "ATH"


def test_normalize_alias_nationals() -> None:
    assert normalize_team("WSH") == "WSN"
    assert normalize_team("Nationals") == "WSN"


def test_unknown_team_raises() -> None:
    with pytest.raises(UnknownTeamError):
        normalize_team("Springfield Isotopes")
