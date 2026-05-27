# 04 — Helper Catalog

## Purpose

Exhaustive list of reusable Python helpers organized by domain module. This is the "library catalog" the PRD calls for. Every helper here is designed to be called from notebooks, templates, the CLI, and other helpers.

**Scope of this doc**: `filters/`, `batting/`, `pitching/`.

- **No `fielding/`** in v1 (deferred — pybaseball coverage spotty).
- **No `viz/`** here — visualization helpers have their own catalog in `05_visualizations.md`.

---

## Conventions

### Function Shape
Every helper follows one of two shapes:

1. **Filter**: `DataFrame → DataFrame` (subset of rows, same columns)
2. **Aggregator**: `DataFrame → Series` or `DataFrame → DataFrame` (summary stats)

No helper performs I/O. No helper mutates input. No helper depends on `pybaseball` directly (use `data/` module wrappers).

### Filter Composability
Filters use the pandas `pipe` idiom:

```python
from mlb_stats_lab.filters import by_team, by_pitch_type, two_strike_counts

result = (
    df
    .pipe(by_team, "SEA", side="batting")
    .pipe(by_pitch_type, "FF")
    .pipe(two_strike_counts)
)
```

Each filter is a top-level function: `def by_team(df: pd.DataFrame, team: str, ...) -> pd.DataFrame`.

### Docblock Format
Every public helper carries a docblock following this template:

```python
def batting_line(df: pd.DataFrame) -> pd.Series:
    """One-line summary of what this returns.

    Longer description: what assumptions about the input DataFrame, what
    Statcast columns it reads, what stats it computes.

    Args:
        df: Statcast pitch-level DataFrame already filtered to the
            batter and date range of interest. Must contain columns:
            events, description, type, launch_speed, launch_angle, ...

    Returns:
        pd.Series indexed by stat name, e.g.
            PA              231
            AB              208
            AVG           0.288
            ...

    Example:
        >>> df = get_statcast_batter("Aaron Judge")
        >>> batting_line(df)
        PA       231
        AVG    0.288
        ...
    """
```

This docblock spec is enforced by linting where possible (ruff D rules later).

### Column References
All helpers operate on Statcast columns. Reference table lives in `03_data_layer.md`. Helper docblocks reference column names verbatim.

### Naming
- Filters: `by_<noun>` (`by_team`, `by_pitch_type`), or predicate verbs (`with_runners_on`, `in_zone`)
- Aggregators: noun phrases (`batting_line`, `arsenal_summary`)
- Plurals for multi-row returns (`splits`, not `split`)

---

## `filters/` — Subset Operations

All take a Statcast DataFrame and return a filtered DataFrame.

### Date Filters

```python
def by_date_range(df, start: date | str, end: date | str) -> pd.DataFrame:
    """Inclusive [start, end] filter on game_date."""

def since_date(df, date_: date | str) -> pd.DataFrame:
    """Rows on or after date_."""

def last_n_days(df, n: int, anchor: date | None = None) -> pd.DataFrame:
    """Last n days of data, ending at anchor (default: max(game_date) in df)."""

def by_month(df, month: int, year: int | None = None) -> pd.DataFrame:
    """Single month slice."""
```

### Team Filters

```python
def by_team(df, team: str, side: Literal["batting", "pitching", "both"] = "both") -> pd.DataFrame:
    """Rows where `team` was batting, pitching, or either.

    Reads: home_team, away_team, inning_topbot.
    side="batting" → rows where team is at bat.
    side="pitching" → rows where team is in the field.
    """

def vs_team(df, team: str) -> pd.DataFrame:
    """Rows where the opponent is `team`. Requires df to already have a
    single 'subject' team established (e.g. via by_team)."""

def home_games_for(df, team: str) -> pd.DataFrame:
    """home_team == team."""

def away_games_for(df, team: str) -> pd.DataFrame:
    """away_team == team."""
```

### Player Filters

```python
def by_batter(df, player: str | int) -> pd.DataFrame:
    """Rows where this player batted. Accepts name (resolved via
    data.resolve_player_id) or MLBAM ID."""

def by_pitcher(df, player: str | int) -> pd.DataFrame:
    """Rows where this player pitched."""

def by_batter_handedness(df, stand: Literal["L", "R"]) -> pd.DataFrame:
    """Filter on batter handedness."""

def by_pitcher_handedness(df, throws: Literal["L", "R"]) -> pd.DataFrame:
    """Filter on pitcher handedness."""

def vs_handedness(df, throws: Literal["L", "R"]) -> pd.DataFrame:
    """Alias of by_pitcher_handedness — natural language at call site
    when slicing a batter's data: df.pipe(vs_handedness, "L")."""
```

### Pitch Filters

```python
def by_pitch_type(df, *pitch_types: str) -> pd.DataFrame:
    """One or more pitch_type codes: FF, SI, FC, SL, CU, KC, CH, FS, ...

    Multiple args → union (df.pipe(by_pitch_type, "FF", "SI") = all fastballs).
    """

def fastballs(df) -> pd.DataFrame:
    """FF, SI, FC, FS."""

def breaking_balls(df) -> pd.DataFrame:
    """SL, CU, KC, SV."""

def offspeed(df) -> pd.DataFrame:
    """CH, FS, FO."""

def by_zone(df, *zones: int) -> pd.DataFrame:
    """Zones 1-9 (in-strike) or 11-14 (out). Multi-zone via varargs."""

def in_zone(df) -> pd.DataFrame:
    """Zones 1-9."""

def out_of_zone(df) -> pd.DataFrame:
    """Zones 11-14."""

def edge_pitches(df) -> pd.DataFrame:
    """Approximate edge of strike zone via plate_x/plate_z thresholds."""

def heart_pitches(df) -> pd.DataFrame:
    """Middle third of zone."""
```

### Count Filters

```python
def by_count(df, balls: int, strikes: int) -> pd.DataFrame:
    """Specific count, e.g. (3, 2)."""

def ahead_in_count(df, perspective: Literal["batter", "pitcher"]) -> pd.DataFrame:
    """Batter ahead: counts where balls > strikes (1-0, 2-0, 2-1, 3-0, 3-1).
    Pitcher ahead: where strikes > balls (0-1, 0-2, 1-2)."""

def behind_in_count(df, perspective: Literal["batter", "pitcher"]) -> pd.DataFrame:
    """Inverse of above."""

def even_count(df) -> pd.DataFrame:
    """0-0, 1-1, 2-2."""

def two_strike_counts(df) -> pd.DataFrame:
    """strikes == 2."""

def three_ball_counts(df) -> pd.DataFrame:
    """balls == 3."""

def first_pitch(df) -> pd.DataFrame:
    """balls == 0 and strikes == 0."""

def full_count(df) -> pd.DataFrame:
    """3-2."""
```

### Situation Filters

```python
def by_inning(df, *innings: int) -> pd.DataFrame:
    """One or more inning numbers."""

def early_innings(df) -> pd.DataFrame:
    """Innings 1-3."""

def middle_innings(df) -> pd.DataFrame:
    """Innings 4-6."""

def late_innings(df) -> pd.DataFrame:
    """Innings 7+."""

def with_runners_on(df) -> pd.DataFrame:
    """Any of on_1b, on_2b, on_3b populated."""

def bases_empty(df) -> pd.DataFrame:
    """All of on_1b, on_2b, on_3b NaN."""

def risp(df) -> pd.DataFrame:
    """Runners in scoring position: on_2b or on_3b populated."""

def close_game(df, run_diff: int = 3) -> pd.DataFrame:
    """abs(bat_score - fld_score) <= run_diff."""

def high_leverage(df) -> pd.DataFrame:
    """Late innings AND close game. Convenience composition."""
```

### Result Filters

```python
def only_in_play(df) -> pd.DataFrame:
    """type == 'X' (ball put in play, regardless of outcome)."""

def only_swings(df) -> pd.DataFrame:
    """description in {swinging_strike, foul, foul_tip, hit_into_play, ...}."""

def only_called_pitches(df) -> pd.DataFrame:
    """description in {ball, called_strike, blocked_ball, pitchout}."""

def only_hits(df) -> pd.DataFrame:
    """events in {single, double, triple, home_run}."""

def only_walks(df) -> pd.DataFrame:
    """events == 'walk'."""

def only_strikeouts(df) -> pd.DataFrame:
    """events in {strikeout, strikeout_double_play}."""

def only_completed_pa(df) -> pd.DataFrame:
    """events.notna() — last pitch of each plate appearance."""
```

---

## `batting/` — Hitter Domain

All take a Statcast DataFrame already filtered to a batter (or a population of batters) and return aggregated stats.

### `batting_line(df) -> pd.Series`

**Comprehensive single call.** Returns the full hitter card.

| Key       | Computation                                              |
| --------- | -------------------------------------------------------- |
| `PA`      | `only_completed_pa(df).shape[0]`                         |
| `AB`      | PA minus walks, HBP, SF, SH                              |
| `H`       | events ∈ {single, double, triple, home_run}              |
| `1B`      | events == "single"                                       |
| `2B`      | events == "double"                                       |
| `3B`      | events == "triple"                                       |
| `HR`      | events == "home_run"                                     |
| `BB`      | events == "walk"                                         |
| `IBB`     | events == "intent_walk" (if available)                   |
| `HBP`     | events == "hit_by_pitch"                                 |
| `SO`      | events ∈ {strikeout, strikeout_double_play}              |
| `SF`      | events == "sac_fly"                                      |
| `SH`      | events == "sac_bunt"                                     |
| `AVG`     | H / AB                                                   |
| `OBP`     | (H + BB + HBP) / (AB + BB + HBP + SF)                    |
| `SLG`     | TB / AB where TB = 1B + 2·2B + 3·3B + 4·HR               |
| `OPS`     | OBP + SLG                                                |
| `ISO`     | SLG − AVG                                                |
| `BB%`     | BB / PA                                                  |
| `K%`      | SO / PA                                                  |
| `BB/K`    | BB / SO                                                  |
| `wOBA`    | mean of `woba_value` weighted by `woba_denom` (Statcast cols) |
| `xwOBA`   | mean of `estimated_woba_using_speedangle` on in-play     |
| `xBA`     | mean of `estimated_ba_using_speedangle` on in-play       |

> Note: wOBA columns vary by Statcast version. If `woba_value`/`woba_denom` are absent, fall back to a fixed-weight formula using events counts. Implementation detail.

### `plate_discipline(df) -> pd.Series`

Standalone. Reads pitch-level (not PA-level) data.

| Key             | Computation                                                  |
| --------------- | ------------------------------------------------------------ |
| `Pitches`       | row count                                                    |
| `Swing%`        | swings / pitches                                             |
| `Z-Swing%`      | swings in zone / pitches in zone                             |
| `O-Swing%`      | swings out of zone / pitches out of zone (= Chase%)          |
| `Contact%`      | contact / swings                                             |
| `Z-Contact%`    | contact on in-zone swings / in-zone swings                   |
| `O-Contact%`    | contact on out-of-zone swings / out-of-zone swings           |
| `Whiff%`        | swinging-strikes / swings                                    |
| `SwStr%`        | swinging-strikes / pitches                                   |
| `Chase%`        | alias of O-Swing%                                            |
| `CSW%`          | (called strikes + swinging strikes) / pitches                |
| `Z%`            | pitches in zone / pitches                                    |
| `First-Pitch Strike%` | first-pitch strikes / first-pitch PAs                  |

### `contact_quality(df) -> pd.Series`

Standalone. Operates only on in-play events.

| Key              | Computation                                                  |
| ---------------- | ------------------------------------------------------------ |
| `BBE`            | batted ball events (rows in only_in_play)                    |
| `Avg EV (mph)`   | mean launch_speed                                            |
| `Max EV (mph)`   | max launch_speed                                             |
| `Avg LA (°)`     | mean launch_angle                                            |
| `Barrel%`        | barrels / BBE — barrel via Statcast's launch_speed_angle classification |
| `HardHit%`       | EV ≥ 95 mph / BBE                                            |
| `Sweet-Spot%`    | LA between 8°–32° / BBE                                      |
| `xBA`            | mean estimated_ba_using_speedangle                           |
| `xSLG`           | mean estimated_slg_using_speedangle                          |
| `xwOBA (in-play)`| mean estimated_woba_using_speedangle                         |
| `Avg Distance`   | mean hit_distance_sc                                         |

### `splits(df, axis) -> pd.DataFrame`

Single function, multiple axes. Returns a multi-row DataFrame indexed by split bucket with the full `batting_line` columns per bucket.

```python
def splits(
    df: pd.DataFrame,
    axis: Literal[
        "vs_hand",       # by p_throws (L vs R pitcher)
        "home_away",
        "month",
        "count_state",   # ahead / even / behind (batter perspective)
        "two_strike",    # two-strike vs not
        "leverage",      # close late vs not
        "innings",       # early / mid / late
    ],
) -> pd.DataFrame:
    """For each bucket on the chosen axis, run batting_line() on the subset.

    Returns a DataFrame indexed by bucket label, columns = batting_line keys.
    """
```

### `performance_by_pitch_type(df) -> pd.DataFrame`

```python
def performance_by_pitch_type(df: pd.DataFrame) -> pd.DataFrame:
    """Group by pitch_type, return per-pitch-type:
       Pitches, Whiff%, AVG, SLG, xwOBA, Avg EV, Avg LA.

    Index: pitch_type. Sort: most-seen first.
    """
```

### `rolling_batting_line(df, window) -> pd.DataFrame`

```python
def rolling_batting_line(
    df: pd.DataFrame,
    window: int = 25,
    over: Literal["PA", "games"] = "PA",
) -> pd.DataFrame:
    """Rolling-window slash line over recent PAs or games. Returns DataFrame
    indexed by anchor PA/game with the same columns as batting_line."""
```

---

## `pitching/` — Pitcher Domain

Mirror of batting. All take a Statcast DataFrame filtered to a pitcher.

### `pitching_line(df) -> pd.Series`

**Comprehensive single call.** Pitcher equivalent of `batting_line`.

| Key      | Computation                                              |
| -------- | -------------------------------------------------------- |
| `BF`     | Batters faced (= completed PAs against)                  |
| `IP`     | Innings pitched — sum of inning fractions per outs recorded |
| `H`      | Hits allowed                                             |
| `R`      | Runs (estimate from delta_run_exp or events; rough in v1)|
| `ER`     | Earned runs — v1: same as R (no error tracking)          |
| `BB`     | Walks allowed                                            |
| `K`      | Strikeouts                                               |
| `HR`     | Home runs allowed                                        |
| `K/9`    | 9·K / IP                                                 |
| `BB/9`   | 9·BB / IP                                                |
| `K-BB%`  | (K − BB) / BF                                            |
| `K%`     | K / BF                                                   |
| `BB%`    | BB / BF                                                  |
| `HR/9`   | 9·HR / IP                                                |
| `WHIP`   | (H + BB) / IP                                            |
| `BAA`    | H / AB-against                                           |
| `wOBA-against`  | mean woba_value weighted by woba_denom            |
| `xwOBA-against` | mean estimated_woba_using_speedangle              |

> Note: ER vs R requires play-by-play and fielding error data not in standard Statcast. v1 treats them as equal and flags this in the docblock.

### `arsenal_summary(df) -> pd.DataFrame`

```python
def arsenal_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per pitch_type:
       Count, Usage%, Avg Velo, Max Velo, Avg Spin, Avg pfx_x, Avg pfx_z,
       Avg Extension, Avg Release Height.

    Sorted by Usage% desc.
    """
```

### `pitch_movement(df) -> pd.DataFrame`

```python
def pitch_movement(df: pd.DataFrame) -> pd.DataFrame:
    """Per pitch_type: Avg/StDev of pfx_x and pfx_z. Used by viz spray-plot.
    Returns Index=pitch_type, columns=[H-Mov-Mean, H-Mov-Std, V-Mov-Mean, V-Mov-Std]."""
```

### `location_summary(df) -> pd.Series`

```python
def location_summary(df: pd.DataFrame) -> pd.Series:
    """Pitcher's overall location tendencies:
       Zone%, Edge%, Heart%, Chase-Inducing% (out-of-zone swings / out-of-zone pitches).
    Optionally callable per pitch_type via groupby pattern in notebook."""
```

### `results_by_pitch(df) -> pd.DataFrame`

```python
def results_by_pitch(df: pd.DataFrame) -> pd.DataFrame:
    """Per pitch_type: Whiff%, CSW%, BAA, xwOBA-against, K%, BB%, HR allowed.
    Sorted by Usage% desc (joined with arsenal_summary)."""
```

### `command_metrics(df) -> pd.Series`

```python
def command_metrics(df: pd.DataFrame) -> pd.Series:
    """Pitcher command indicators:
       First-Pitch Strike%, Called-Strike% in Heart, Edge%, In-Zone%, Ball%.
    """
```

### `splits(df, axis) -> pd.DataFrame`

Mirror of batting splits, axes adjusted for pitcher perspective:

```python
def splits(
    df: pd.DataFrame,
    axis: Literal[
        "vs_hand",        # by stand (L vs R batter)
        "home_away",
        "month",
        "times_through_order",
        "innings",
        "leverage",
    ],
) -> pd.DataFrame:
    """For each bucket, run pitching_line(). Returns DataFrame indexed by bucket."""
```

> Note: `times_through_order` requires deriving from at_bat_number ordering within game_pk + pitcher. v1 implementation detail.

### `rolling_pitching_line(df, window) -> pd.DataFrame`

```python
def rolling_pitching_line(
    df: pd.DataFrame,
    window: int = 5,
    over: Literal["starts", "BF"] = "starts",
) -> pd.DataFrame:
    """Rolling-window pitching line over recent starts/BFs."""
```

---

## Module Exports Summary

```python
# mlb_stats_lab/filters/__init__.py
from .date import by_date_range, since_date, last_n_days, by_month
from .team import by_team, vs_team, home_games_for, away_games_for
from .player import by_batter, by_pitcher, by_batter_handedness, by_pitcher_handedness, vs_handedness
from .pitch import (
    by_pitch_type, fastballs, breaking_balls, offspeed,
    by_zone, in_zone, out_of_zone, edge_pitches, heart_pitches,
)
from .count import (
    by_count, ahead_in_count, behind_in_count, even_count,
    two_strike_counts, three_ball_counts, first_pitch, full_count,
)
from .situation import (
    by_inning, early_innings, middle_innings, late_innings,
    with_runners_on, bases_empty, risp, close_game, high_leverage,
)
from .result import (
    only_in_play, only_swings, only_called_pitches,
    only_hits, only_walks, only_strikeouts, only_completed_pa,
)
```

```python
# mlb_stats_lab/batting/__init__.py
from .line import batting_line
from .plate_discipline import plate_discipline
from .contact import contact_quality
from .splits import splits
from .by_pitch import performance_by_pitch_type
from .rolling import rolling_batting_line
```

```python
# mlb_stats_lab/pitching/__init__.py
from .line import pitching_line
from .arsenal import arsenal_summary
from .movement import pitch_movement
from .location import location_summary
from .by_pitch import results_by_pitch
from .command import command_metrics
from .splits import splits
from .rolling import rolling_pitching_line
```

Note: `batting.splits` and `pitching.splits` share a name but live in separate subpackages — no collision.

---

## Worked Example (Notebook-Level)

What a typical helper composition looks like:

```python
from mlb_stats_lab.data import get_statcast_batter
from mlb_stats_lab.filters import vs_handedness, risp, two_strike_counts
from mlb_stats_lab.batting import batting_line, plate_discipline, contact_quality, splits

df = get_statcast_batter("Aaron Judge")

# Overall line
overall = batting_line(df)

# Discipline + contact (standalone)
disc = plate_discipline(df)
contact = contact_quality(df)

# vs LHP, RISP, two-strike
clutch = (
    df
    .pipe(vs_handedness, "L")
    .pipe(risp)
    .pipe(two_strike_counts)
    .pipe(batting_line)
)

# Splits panel
by_hand = splits(df, axis="vs_hand")
by_month = splits(df, axis="month")
```

This composition style is what the notebook templates will rely on. See `06_notebook_templates.md`.

---

## Decision Log

| Decision                                            | Rationale                                                     |
| --------------------------------------------------- | ------------------------------------------------------------- |
| `batting_line()` comprehensive, sub-fns standalone  | Single-call convenience + composability                       |
| `splits(df, axis=...)` single-fn API                | Discoverable via Literal type, one function to learn          |
| Pandas `.pipe()` for filter composition             | Idiomatic, no new abstractions to learn                       |
| Skip `fielding/` in v1                              | Pybaseball coverage spotty, defer until needed                |
| Viz helpers moved to `05_visualizations.md`         | Cleaner doc boundary                                          |
| Per-pitch-type aggregator inside batting + pitching | Both perspectives need it                                     |
| Rolling helpers split by domain                     | Default window differs (PAs for hitters, starts for pitchers) |
| ER == R in v1                                       | Standard Statcast lacks error data; flag in docblock          |

---

## Open Items For Later Docs

- Which of these helpers each notebook template invokes → `06_notebook_templates.md`
- Charts that consume each aggregator's output → `05_visualizations.md`
- Helpers that should be re-exported at the package root for super-common cases (e.g. `from mlb_stats_lab import batting_line`) → decide during implementation
- Whether `splits` `times_through_order` axis lands in v1 or v1.1 → flag during implementation
