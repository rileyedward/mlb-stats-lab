# 03 — Data Layer

## Purpose

Defines the `src/mlb_stats_lab/data/` module — the *only* place in the codebase that talks to pybaseball directly. Every other module receives plain `pandas.DataFrame` objects from here.

Goals:
- One canonical wrapper around each pybaseball function we actually use.
- Player and team identification ergonomic for notebook use (strings, not numeric IDs).
- "Current season" auto-detection so notebooks read naturally without season args.
- Pybaseball cache enabled on import — no per-call ceremony.

---

## Module Surface

```
src/mlb_stats_lab/data/
├── __init__.py       # re-exports public API; calls cache.enable_default() on import
├── cache.py          # cache enable/disable/flush
├── dates.py          # season detection, ranges, opening day map
├── players.py        # name → MLBAM ID resolution, roster lookup
├── teams.py          # team metadata, schedule, abbreviation registry
├── statcast.py       # pitch-level fetchers
└── season.py         # Fangraphs-backed season-level team aggregates
```

### Public re-exports (`mlb_stats_lab.data.__init__`)

```python
from mlb_stats_lab.data.cache import (
    enable_default,
    disable,
    flush,
)
from mlb_stats_lab.data.dates import (
    current_season,
    current_season_range,
    season_range,
    last_n_days,
    opening_day,
)
from mlb_stats_lab.data.players import (
    resolve_player_id,
    player_name,
    team_roster,
)
from mlb_stats_lab.data.teams import (
    TEAMS,
    normalize_team,
    team_schedule,
)
from mlb_stats_lab.data.statcast import (
    get_statcast,
    get_statcast_batter,
    get_statcast_pitcher,
    get_statcast_for_team,
    get_statcast_for_game,
)
from mlb_stats_lab.data.season import (
    get_team_batting,
    get_team_pitching,
    get_standings,
)
```

---

## Pybaseball Entry Points We Wrap

| Pybaseball function               | Our wrapper                       | Returns                         |
| --------------------------------- | --------------------------------- | ------------------------------- |
| `statcast(start_dt, end_dt)`      | `get_statcast(start, end)`        | All MLB pitches in range        |
| `statcast_batter(...)`            | `get_statcast_batter(player, …)`  | Pitches faced by batter         |
| `statcast_pitcher(...)`           | `get_statcast_pitcher(player, …)` | Pitches thrown by pitcher       |
| `playerid_lookup(last, first)`    | `resolve_player_id(name)`         | MLBAM ID (int)                  |
| `playerid_reverse_lookup(ids)`    | `player_name(player_id)`          | Display name (str)              |
| `schedule_and_record(year, team)` | `team_schedule(team, year=None)`  | Team schedule + game outcomes   |
| `team_batting(year)`              | `get_team_batting(year=None)`     | Fangraphs-style season batting  |
| `team_pitching(year)`             | `get_team_pitching(year=None)`    | Fangraphs-style season pitching |
| `standings(year)`                 | `get_standings(year=None)`        | Division standings              |

Every wrapper applies the same defaults: season auto-detect, normalized team abbreviations, plain DataFrame return.

---

## Public API — Function Signatures

### `data/statcast.py`

```python
def get_statcast(
    start: date | str | None = None,
    end: date | str | None = None,
) -> pd.DataFrame:
    """All Statcast pitch-level data in [start, end] (inclusive).

    Defaults to current season's opening day → today.
    Dates accept ISO strings ("2026-04-01") or datetime.date.
    """

def get_statcast_batter(
    player: str,
    start: date | str | None = None,
    end: date | str | None = None,
) -> pd.DataFrame:
    """Pitches faced by the given batter in [start, end]. Player by name."""

def get_statcast_pitcher(
    player: str,
    start: date | str | None = None,
    end: date | str | None = None,
) -> pd.DataFrame:
    """Pitches thrown by the given pitcher in [start, end]. Player by name."""

def get_statcast_for_team(
    team: str,
    start: date | str | None = None,
    end: date | str | None = None,
    side: Literal["batting", "pitching", "both"] = "both",
) -> pd.DataFrame:
    """All pitches in games where `team` was batting, pitching, or either.

    Implementation: fetch get_statcast(start, end), filter by team via
    home_team/away_team and the `side` arg. Team by 3-letter abbreviation.
    """

def get_statcast_for_game(game_pk: int) -> pd.DataFrame:
    """All pitches from a single game by Statcast game_pk."""
```

### `data/players.py`

```python
def resolve_player_id(name: str) -> int:
    """Convert display name → MLBAM ID via pybaseball.playerid_lookup.

    - Normalizes "First Last" → ("First", "Last") split.
    - On multiple matches: raises AmbiguousPlayerError with the candidate
      list and current-team hints so the caller can refine.
    - Cached in-process for the session.
    """

def player_name(player_id: int) -> str:
    """Inverse: MLBAM ID → 'First Last' display name."""

def team_roster(team: str, year: int | None = None) -> pd.DataFrame:
    """Roster for a team in a season. Source: pybaseball roster helper.
    Returns: columns [player_id, name, position, status]."""
```

### `data/teams.py`

```python
# Static registry — embedded constant, not fetched from network.
TEAMS: dict[str, TeamInfo]  # keyed by 3-letter abbreviation

@dataclass(frozen=True)
class TeamInfo:
    abbrev: str          # "SEA"
    name: str            # "Seattle Mariners"
    location: str        # "Seattle"
    nickname: str        # "Mariners"
    league: Literal["AL", "NL"]
    division: Literal["E", "C", "W"]
    mlbam_team_id: int   # MLBAM internal team ID (for fielding queries)

def normalize_team(value: str) -> str:
    """Accept 'SEA', 'sea', 'Mariners', 'Seattle Mariners', etc.
    → return canonical 'SEA'. Raises UnknownTeamError on miss."""

def team_schedule(team: str, year: int | None = None) -> pd.DataFrame:
    """Wraps pybaseball.schedule_and_record. Year defaults to current."""
```

### `data/dates.py`

```python
def current_season() -> int:
    """Year of the current MLB season.

    Rule: if today >= opening_day(today.year) → today.year, else today.year - 1.
    Allows override via STATSLAB_SEASON env or [season] default_year in
    statslab.toml.
    """

def current_season_range() -> tuple[date, date]:
    """(opening_day(current_season), today). Used as default in statcast fns."""

def season_range(year: int) -> tuple[date, date]:
    """(opening_day(year), regular_season_end(year)). v1: returns
    (opening_day, today) if year == current and season in progress."""

def last_n_days(n: int, anchor: date | None = None) -> tuple[date, date]:
    """(anchor - n + 1, anchor). anchor defaults to today."""

def opening_day(year: int) -> date:
    """Looks up regular-season opening day. v1: hardcoded table indexed
    by year, fallback to last-Thursday-of-March heuristic."""
```

### `data/cache.py`

```python
def enable_default() -> None:
    """Calls pybaseball.cache.enable(). Idempotent. Called at import time
    of mlb_stats_lab.data."""

def disable() -> None:
    """pybaseball.cache.disable() — for tests / forced fresh fetches."""

def flush(older_than_days: int | None = None) -> int:
    """Delete cache entries. Returns count of files removed.
    Targets ~/.pybaseball/cache/ (or pybaseball's configured dir)."""
```

### `data/season.py`

```python
def get_team_batting(year: int | None = None) -> pd.DataFrame:
    """Fangraphs season-level team batting (wraps pybaseball.team_batting).
    Year defaults to current season."""

def get_team_pitching(year: int | None = None) -> pd.DataFrame:
    """Fangraphs season-level team pitching."""

def get_standings(year: int | None = None) -> pd.DataFrame:
    """Division standings. Year defaults to current."""
```

---

## Statcast Column Reference

What `get_statcast(...)` actually returns. Pybaseball returns ~90 columns; the ones our helpers consume are listed here. Full list available at https://baseballsavant.mlb.com/csv-docs.

### Identifiers
| Column           | Type   | Notes                                       |
| ---------------- | ------ | ------------------------------------------- |
| `game_pk`        | int    | Unique game ID                              |
| `game_date`      | str    | ISO date string                             |
| `at_bat_number`  | int    | Per-game AB sequence                        |
| `pitch_number`   | int    | Per-AB pitch sequence                       |

### Players
| Column          | Type | Notes                                      |
| --------------- | ---- | ------------------------------------------ |
| `batter`        | int  | MLBAM batter ID                            |
| `pitcher`       | int  | MLBAM pitcher ID                           |
| `player_name`   | str  | Pitcher's name (despite the misleading name) |
| `stand`         | str  | Batter handedness: "L" or "R"              |
| `p_throws`      | str  | Pitcher handedness: "L" or "R"             |

### Pitch Physics
| Column            | Type  | Notes                                                |
| ----------------- | ----- | ---------------------------------------------------- |
| `pitch_type`      | str   | "FF", "SL", "CU", "CH", "SI", "FC", "FS", "KC", etc. |
| `pitch_name`      | str   | Human-readable: "4-Seam Fastball" etc.               |
| `release_speed`   | float | mph                                                  |
| `release_spin_rate` | float | rpm                                                |
| `pfx_x`, `pfx_z`  | float | Horiz/vert pitch movement (ft)                       |
| `plate_x`, `plate_z` | float | Horiz/vert plate crossing position (ft)            |
| `release_extension` | float | ft                                                |

### Plate / Zone
| Column          | Type | Notes                                                  |
| --------------- | ---- | ------------------------------------------------------ |
| `zone`          | int  | 1-9 strike zone, 11-14 outside                         |
| `sz_top`, `sz_bot` | float | Batter's strike zone top/bottom (ft)               |

### Result
| Column        | Type | Notes                                                                   |
| ------------- | ---- | ----------------------------------------------------------------------- |
| `description` | str  | Per-pitch: "called_strike", "ball", "swinging_strike", "hit_into_play", etc. |
| `events`      | str  | AB outcome (last pitch of AB): "single", "home_run", "strikeout", NaN otherwise |
| `type`        | str  | "S" strike, "B" ball, "X" in play                                       |

### Batted Ball
| Column         | Type  | Notes                                                  |
| -------------- | ----- | ------------------------------------------------------ |
| `launch_speed` | float | mph                                                    |
| `launch_angle` | float | degrees                                                |
| `hc_x`, `hc_y` | float | Hit coordinates (raw Hit-Chart space, used for spray)  |
| `bb_type`      | str   | "ground_ball", "fly_ball", "line_drive", "popup"       |
| `hit_distance_sc` | float | feet                                                |
| `estimated_ba_using_speedangle` | float | xBA per pitch                            |
| `estimated_woba_using_speedangle` | float | xwOBA per pitch                        |

### Context
| Column          | Type | Notes                            |
| --------------- | ---- | -------------------------------- |
| `balls`         | int  | Count                            |
| `strikes`       | int  | Count                            |
| `outs_when_up`  | int  | Outs at start of AB              |
| `inning`        | int  |                                  |
| `inning_topbot` | str  | "Top" / "Bot"                    |
| `on_1b`, `on_2b`, `on_3b` | float | MLBAM ID or NaN        |
| `home_team`, `away_team` | str | 3-letter abbreviations    |

### Win Probability / Run Expectancy
| Column            | Type  | Notes                                    |
| ----------------- | ----- | ---------------------------------------- |
| `delta_run_exp`   | float | Per-pitch run expectancy change          |
| `delta_home_win_exp` | float | Per-pitch home WPA change             |
| `bat_score`, `fld_score` | int | Score for batting/fielding team    |

This reference will be cross-linked from `04_helper_catalog.md` so helper docs can refer back rather than re-listing.

---

## Player Identification Convention

- **Public API takes names** (e.g. `get_statcast_batter("Aaron Judge", ...)`).
- Internally, `resolve_player_id(name)` calls `pybaseball.playerid_lookup`.
- On multiple matches:
  - If exactly one is currently active in MLB → use it, warn via logging.
  - Otherwise raise `AmbiguousPlayerError(name, candidates: list[Candidate])` with `Candidate(id, first, last, debut_year, last_year)`.
  - User passes a refined name (`"Tatis Jr."`, `"Vladimir Guerrero Jr."`) or the MLBAM ID directly via a separate `get_statcast_batter_by_id(id, ...)` escape hatch.
- Name → ID cache lives in-process (`functools.lru_cache`). Pybaseball already caches the underlying lookup table.

---

## Team Identification Convention

- **Canonical = 3-letter MLBAM abbreviation** (`SEA`, `LAD`, `NYY`, `ATH`, `WSN`, …).
- `normalize_team(value: str) -> str` accepts:
  - abbreviation (case-insensitive): `"sea"` → `"SEA"`
  - nickname: `"Mariners"` → `"SEA"`
  - full name: `"Seattle Mariners"` → `"SEA"`
  - location: `"Seattle"` → `"SEA"`
- All helpers internally call `normalize_team(team)` first.
- `TEAMS` dict embedded as a constant in `teams.py`. Updated manually if MLB rebrands (e.g. Oakland → Athletics → Sacramento → Las Vegas saga).

---

## "Current Season" Resolution

Resolution order (first non-None wins):

1. `STATSLAB_SEASON` env var (integer year)
2. `statslab.toml` → `[season] default_year`
3. Auto-detect:
   - If `today >= opening_day(today.year)` → `today.year`
   - Else → `today.year - 1`

The auto-detect rule means in January–March (offseason) we look at last year's season. From opening day forward, we look at the current year.

Stored under `mlb_stats_lab.config.current_season()` and shadowed by `data.dates.current_season()` for convenience.

---

## Cache Configuration

- `pybaseball.cache.enable()` invoked once at `mlb_stats_lab.data.__init__` import time.
- Cache backend: pybaseball's default Parquet cache at `~/.pybaseball/cache/`.
- We do not override the directory in v1.
- Cache can be flushed via `data.flush(older_than_days=…)` (mostly for the user; never called automatically).
- For tests: `data.cache.disable()` ensures live fetches in integration tests.

---

## Error Handling & Empty Results

- Wrappers return **empty DataFrames** (not `None`) when no rows match.
- Network or API errors propagate as `pybaseball`'s native exceptions — we do not wrap.
- One custom exception type per concern:
  - `AmbiguousPlayerError(name, candidates)` — multiple player matches
  - `UnknownPlayerError(name)` — no matches
  - `UnknownTeamError(value)` — `normalize_team` could not resolve
- All defined in `mlb_stats_lab.data.exceptions`.

---

## Performance Notes

- `get_statcast(start, end)` for a full season can take 60–120s on first call (uncached). Subsequent calls hit Parquet cache → < 1s.
- Recommend running `get_statcast(*current_season_range())` once at the top of any notebook, then filtering in-memory with `mlb_stats_lab.filters`.
- `get_statcast_batter` / `get_statcast_pitcher` are also cached. Pre-cache by calling these for a couple star players the first time you run a Player Profile notebook.

---

## Decision Log

| Decision                                 | Rationale                                                |
| ---------------------------------------- | -------------------------------------------------------- |
| Plain `pd.DataFrame` returns             | Per `01` — no wrapper types in v1                        |
| Names as input, IDs internal             | Notebook ergonomics                                      |
| `AmbiguousPlayerError` w/ candidates     | Forces resolution without silent wrong-player picks      |
| 3-letter MLBAM abbreviation as canonical | Matches Statcast `home_team` / `away_team` columns       |
| Static `TEAMS` registry, manual updates  | Rare changes; avoids per-import network call             |
| Auto-detect current season               | Removes boilerplate in nearly every notebook             |
| `cache.enable()` on import               | "It just works" in notebooks                             |
| Wrap Fangraphs season-level helpers      | Pre-aggregated team stats useful for Team Snapshot       |
| Empty DataFrame, not None, on no results | Avoids `if df is not None` clutter in helpers downstream |

---

## Open Items For Later Docs

- Exact filter signatures (`by_batter` resolves a name internally? Or takes a pre-resolved ID?) → `04_helper_catalog.md`
- Notebook-level "load data" pattern (helper that emits both the season DataFrame and a few common filtered subsets) → `06_notebook_templates.md`
- How `team_roster` is sourced — pybaseball has a roster helper but its reliability varies; may need a different source → confirm during data-layer implementation phase in `10_roadmap.md`
