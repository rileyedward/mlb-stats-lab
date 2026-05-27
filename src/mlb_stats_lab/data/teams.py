"""Team metadata, normalization, and schedule lookup."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from mlb_stats_lab.data.exceptions import UnknownTeamError

League = Literal["AL", "NL"]
Division = Literal["E", "C", "W"]


@dataclass(frozen=True)
class TeamInfo:
    abbrev: str
    name: str
    location: str
    nickname: str
    league: League
    division: Division
    mlbam_team_id: int


def _t(
    abbrev: str,
    name: str,
    location: str,
    nickname: str,
    league: League,
    division: Division,
    mlbam_team_id: int,
) -> tuple[str, TeamInfo]:
    return abbrev, TeamInfo(abbrev, name, location, nickname, league, division, mlbam_team_id)


TEAMS: dict[str, TeamInfo] = dict(
    [
        _t("ARI", "Arizona Diamondbacks", "Arizona", "Diamondbacks", "NL", "W", 109),
        _t("ATL", "Atlanta Braves", "Atlanta", "Braves", "NL", "E", 144),
        _t("BAL", "Baltimore Orioles", "Baltimore", "Orioles", "AL", "E", 110),
        _t("BOS", "Boston Red Sox", "Boston", "Red Sox", "AL", "E", 111),
        _t("CHC", "Chicago Cubs", "Chicago", "Cubs", "NL", "C", 112),
        _t("CWS", "Chicago White Sox", "Chicago", "White Sox", "AL", "C", 145),
        _t("CIN", "Cincinnati Reds", "Cincinnati", "Reds", "NL", "C", 113),
        _t("CLE", "Cleveland Guardians", "Cleveland", "Guardians", "AL", "C", 114),
        _t("COL", "Colorado Rockies", "Colorado", "Rockies", "NL", "W", 115),
        _t("DET", "Detroit Tigers", "Detroit", "Tigers", "AL", "C", 116),
        _t("HOU", "Houston Astros", "Houston", "Astros", "AL", "W", 117),
        _t("KC", "Kansas City Royals", "Kansas City", "Royals", "AL", "C", 118),
        _t("LAA", "Los Angeles Angels", "Los Angeles", "Angels", "AL", "W", 108),
        _t("LAD", "Los Angeles Dodgers", "Los Angeles", "Dodgers", "NL", "W", 119),
        _t("MIA", "Miami Marlins", "Miami", "Marlins", "NL", "E", 146),
        _t("MIL", "Milwaukee Brewers", "Milwaukee", "Brewers", "NL", "C", 158),
        _t("MIN", "Minnesota Twins", "Minnesota", "Twins", "AL", "C", 142),
        _t("NYM", "New York Mets", "New York", "Mets", "NL", "E", 121),
        _t("NYY", "New York Yankees", "New York", "Yankees", "AL", "E", 147),
        _t("ATH", "Athletics", "Sacramento", "Athletics", "AL", "W", 133),
        _t("PHI", "Philadelphia Phillies", "Philadelphia", "Phillies", "NL", "E", 143),
        _t("PIT", "Pittsburgh Pirates", "Pittsburgh", "Pirates", "NL", "C", 134),
        _t("SD", "San Diego Padres", "San Diego", "Padres", "NL", "W", 135),
        _t("SF", "San Francisco Giants", "San Francisco", "Giants", "NL", "W", 137),
        _t("SEA", "Seattle Mariners", "Seattle", "Mariners", "AL", "W", 136),
        _t("STL", "St. Louis Cardinals", "St. Louis", "Cardinals", "NL", "C", 138),
        _t("TB", "Tampa Bay Rays", "Tampa Bay", "Rays", "AL", "E", 139),
        _t("TEX", "Texas Rangers", "Texas", "Rangers", "AL", "W", 140),
        _t("TOR", "Toronto Blue Jays", "Toronto", "Blue Jays", "AL", "E", 141),
        _t("WSN", "Washington Nationals", "Washington", "Nationals", "NL", "E", 120),
    ]
)

# Common alternative spellings → canonical abbrev.
_ALIASES: dict[str, str] = {
    # variant abbreviations
    "CHW": "CWS",
    "WSH": "WSN",
    "WAS": "WSN",
    "KCR": "KC",
    "SDP": "SD",
    "SFG": "SF",
    "TBR": "TB",
    "OAK": "ATH",
    "ANA": "LAA",
    # nicknames
    "diamondbacks": "ARI",
    "dbacks": "ARI",
    "braves": "ATL",
    "orioles": "BAL",
    "red sox": "BOS",
    "redsox": "BOS",
    "cubs": "CHC",
    "white sox": "CWS",
    "whitesox": "CWS",
    "reds": "CIN",
    "guardians": "CLE",
    "indians": "CLE",
    "rockies": "COL",
    "tigers": "DET",
    "astros": "HOU",
    "royals": "KC",
    "angels": "LAA",
    "dodgers": "LAD",
    "marlins": "MIA",
    "brewers": "MIL",
    "twins": "MIN",
    "mets": "NYM",
    "yankees": "NYY",
    "athletics": "ATH",
    "a's": "ATH",
    "as": "ATH",
    "phillies": "PHI",
    "pirates": "PIT",
    "padres": "SD",
    "giants": "SF",
    "mariners": "SEA",
    "cardinals": "STL",
    "cards": "STL",
    "rays": "TB",
    "rangers": "TEX",
    "blue jays": "TOR",
    "bluejays": "TOR",
    "jays": "TOR",
    "nationals": "WSN",
    "nats": "WSN",
}


def normalize_team(value: str) -> str:
    """Accept abbreviation, nickname, location, or full name → canonical abbrev.

    Args:
        value: Any team identifier. Case-insensitive.

    Returns:
        Canonical 3-letter abbreviation.

    Raises:
        UnknownTeamError: when ``value`` does not match any team.
    """
    if value is None:
        raise UnknownTeamError(str(value))
    raw = str(value).strip()
    if not raw:
        raise UnknownTeamError(value)

    upper = raw.upper()
    if upper in TEAMS:
        return upper

    if upper in {k.upper() for k in _ALIASES}:
        return _ALIASES[next(k for k in _ALIASES if k.upper() == upper)]

    low = raw.lower()
    if low in _ALIASES:
        return _ALIASES[low]

    # Full name / location match
    for abbrev, info in TEAMS.items():
        if low in {info.name.lower(), info.location.lower(), info.nickname.lower()}:
            return abbrev

    raise UnknownTeamError(raw)


def team_schedule(team: str, year: int | None = None) -> pd.DataFrame:
    """Wraps ``pybaseball.schedule_and_record``. Year defaults to current season.

    Returns a DataFrame of the team's games with R / RA / W-L columns.
    """
    from mlb_stats_lab.data.dates import current_season

    abbrev = normalize_team(team)
    yr = year or current_season()
    try:
        from pybaseball import schedule_and_record  # type: ignore[import-untyped]

        df = schedule_and_record(yr, abbrev)
        if df is None:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()
