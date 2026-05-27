"""Player name ↔ MLBAM ID resolution, roster lookup."""

from __future__ import annotations

from functools import lru_cache

import pandas as pd

from mlb_stats_lab.data.exceptions import (
    AmbiguousPlayerError,
    Candidate,
    UnknownPlayerError,
)


def _split_name(name: str) -> tuple[str, str]:
    """Split a display name into ``(first, last)``.

    Handles ``"First Last"``, ``"First Middle Last"``, ``"First Last Jr."``.
    """
    raw = name.strip()
    parts = raw.split()
    if len(parts) == 1:
        return "", parts[0]
    suffixes = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv"}
    if parts[-1].lower() in suffixes and len(parts) >= 3:
        return parts[0], " ".join(parts[1:-1])
    return parts[0], " ".join(parts[1:])


def _lookup(first: str, last: str) -> pd.DataFrame:
    try:
        from pybaseball import playerid_lookup  # type: ignore[import-untyped]

        df = playerid_lookup(last, first, fuzzy=False)
        if df is None or df.empty:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


@lru_cache(maxsize=512)
def resolve_player_id(name: str) -> int:
    """Display name → MLBAM ID.

    Multiple matches → if exactly one is currently active, use it; otherwise
    raise :class:`AmbiguousPlayerError`. No matches → :class:`UnknownPlayerError`.
    """
    first, last = _split_name(name)
    df = _lookup(first, last)
    if df.empty:
        # Try a fuzzy fallback by passing the whole name as a last-name only.
        df = _lookup("", name)
    if df.empty:
        raise UnknownPlayerError(name)

    df = df.dropna(subset=["key_mlbam"])
    df = df[df["key_mlbam"] != 0]
    if df.empty:
        raise UnknownPlayerError(name)

    if len(df) == 1:
        return int(df.iloc[0]["key_mlbam"])

    from datetime import date

    current_year = date.today().year
    active = df[df["mlb_played_last"].fillna(0) >= current_year - 1]
    if len(active) == 1:
        return int(active.iloc[0]["key_mlbam"])

    candidates = [
        Candidate(
            id=int(row["key_mlbam"]),
            first=str(row.get("name_first", "")),
            last=str(row.get("name_last", "")),
            debut_year=int(row["mlb_played_first"])
            if pd.notna(row.get("mlb_played_first"))
            else None,
            last_year=int(row["mlb_played_last"]) if pd.notna(row.get("mlb_played_last")) else None,
        )
        for _, row in df.iterrows()
    ]
    raise AmbiguousPlayerError(name, candidates)


@lru_cache(maxsize=512)
def player_name(player_id: int) -> str:
    """MLBAM ID → display name."""
    try:
        from pybaseball import playerid_reverse_lookup  # type: ignore[import-untyped]

        df = playerid_reverse_lookup([int(player_id)], key_type="mlbam")
        if df is None or df.empty:
            return str(player_id)
        row = df.iloc[0]
        first = str(row.get("name_first", "")).title()
        last = str(row.get("name_last", "")).title()
        return f"{first} {last}".strip() or str(player_id)
    except Exception:
        return str(player_id)


def team_roster(team: str, year: int | None = None) -> pd.DataFrame:
    """Roster for ``team`` in ``year``. Columns: player_id, name, position, status.

    Implementation uses Statcast batting + pitching data to derive an in-season
    "active roster" (any player who appeared for the team that year).
    """
    from mlb_stats_lab.data.dates import current_season, season_range
    from mlb_stats_lab.data.statcast import get_statcast_for_team
    from mlb_stats_lab.data.teams import normalize_team

    abbrev = normalize_team(team)
    yr = year or current_season()
    start, end = season_range(yr)
    df = get_statcast_for_team(abbrev, start=start, end=end, side="both")
    if df.empty:
        return pd.DataFrame(columns=["player_id", "name", "position", "status"])

    rows: list[dict[str, object]] = []
    # Pitchers: rows where team was pitching → pitcher MLBAM ID
    pitchers = (
        df.loc[df["_team_pitching"] == abbrev, "pitcher"].dropna().unique()
        if "_team_pitching" in df
        else []
    )
    batters = (
        df.loc[df["_team_batting"] == abbrev, "batter"].dropna().unique()
        if "_team_batting" in df
        else []
    )
    seen: set[int] = set()
    for pid in batters:
        pid_i = int(pid)
        if pid_i in seen:
            continue
        seen.add(pid_i)
        rows.append(
            {"player_id": pid_i, "name": player_name(pid_i), "position": "B", "status": "active"}
        )
    for pid in pitchers:
        pid_i = int(pid)
        if pid_i in seen:
            continue
        seen.add(pid_i)
        rows.append(
            {"player_id": pid_i, "name": player_name(pid_i), "position": "P", "status": "active"}
        )
    return pd.DataFrame(rows)
