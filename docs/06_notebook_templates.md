# 06 — Notebook Templates

> **Update (presentation overhaul).** The design below is the original v1 plan.
> What changed in the overhaul:
> - Templates are now **jupytext percent-format `.py`** files in
>   `reports/templates/notebooks/` (source of truth), paired to `.ipynb` via
>   `[tool.jupytext]`. The `scripts/generate_notebook_templates.py` generator is gone.
> - Generated notebooks are written to **`notebooks/generated/`**, not `reports/`.
> - **Auto-execution shipped**: `statslab new-notebook … --run` executes the notebook
>   via `nbclient` after parameter substitution (default stays scaffold-only).
> - Templates render with shared presentation helpers from
>   `mlb_stats_lab.viz.display` — `report_header()`, `section()`, `stat_table()`,
>   `metric_row()` — instead of raw `display(series.to_frame("value"))` dumps.
> Cell tags (`parameters`, `setup`, `load`, `section`, `summary`, `hidden`) are
> unchanged and preserved through the `.py` ⇄ `.ipynb` round-trip.

## Purpose

Each template is a scaffold `.ipynb` that — given a few parameters — produces a structured analysis notebook combining helpers from `04` and charts from `05`. Templates are the workflow backbone: most user reporting will start from one of them, not from a blank notebook.

**v1 templates** (locked in `00_meta_plan`):
1. Series Matchup
2. Batter Profile
3. Pitcher Profile
4. Team Season Snapshot

Game Recap deferred to v1.1.

---

## Template Mechanics

### File Format
- Each template is a real, valid `.ipynb` file in `reports/templates/notebooks/`.
- Filenames are kebab-case: `series-matchup.ipynb`, `batter-profile.ipynb`, `pitcher-profile.ipynb`, `team-season-snapshot.ipynb`.
- Templates are runnable as-is with default parameters (the "parameters" cell holds sensible defaults).

### Parameterization — Papermill-Style

One cell near the top of every template is tagged `"parameters"` (via `metadata.tags`). The CLI rewrites this cell with caller-provided values before saving the new notebook.

Example parameters cell in `series-matchup.ipynb`:

```python
# parameters
team_a = "SEA"
team_b = "LAD"
season = None              # None → current season (auto-detect)
start_date = None          # None → opening day of season
end_date = None            # None → today
```

CLI flow (full spec in `08_cli.md`):

```
statslab new-notebook series-matchup --team-a SEA --team-b LAD
```

→ reads `reports/templates/notebooks/series-matchup.ipynb`
→ uses `nbformat` to find the cell tagged `parameters`
→ replaces its source with `team_a = "SEA"\nteam_b = "LAD"\n...`
→ writes new notebook to `reports/series_matchup__SEA_vs_LAD__2026-05-20.ipynb` (per naming rule in `01`)
→ does **not** execute (user opens in JupyterLab and runs)

### Templates Reference No CLI State
Once generated, a notebook is self-contained. It imports from `mlb_stats_lab` and reads its own parameters. No CLI artifacts leak into the saved file.

### Auto-Execution
**Not** in v1. CLI generates → user reviews + runs. Rationale: live pybaseball fetches can be slow on a cold cache; user wants to see code before paying for execution time.

> Door-open: a future `--execute` flag could call `nbclient.NotebookClient.execute()` after substitution.

---

## Standard Template Structure

Every template follows the same skeleton. Cells listed by index/role:

| #   | Cell type | Tags         | Purpose                                                                                                                           |
| --- | --------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| 1   | markdown  | —            | **Title + subtitle**. Dynamic via Python display below or auto-injected by CLI (see "Title Cell" note).                           |
| 2   | code      | `parameters` | Parameters with defaults. Rewritten by CLI.                                                                                       |
| 3   | code      | `setup`      | Imports + `season` resolution + date range derivation.                                                                            |
| 4   | code      | `load`       | Data fetch via `mlb_stats_lab.data`. Slowest cell.                                                                                |
| 5+  | mixed     | `section`    | One or more cells per analytical section: markdown intro, code that calls helpers and renders charts, optional markdown takeaway. |
| N   | markdown  | `summary`    | Closing summary. Often contains a code cell above it that prints auto-derived takeaway bullets.                                   |

### Title Cell Pattern

Markdown title is static template wording, but a code cell injects dynamic context using `IPython.display`:

```python
from IPython.display import Markdown
Markdown(f"# Series Matchup — {team_a} vs {team_b}\n*{start_date} → {end_date}*")
```

This keeps the markdown title generic and lets parameters drive the rendered heading.

### Standard Setup Cell

Every template's `setup` cell:

```python
from mlb_stats_lab.data import current_season, current_season_range, season_range
from mlb_stats_lab.viz.save import fig_to_png  # for occasional inline saves

season = season or current_season()
if start_date is None or end_date is None:
    s, e = season_range(season)
    start_date = start_date or s
    end_date = end_date or e
```

### Standard Load Cell
Each template fetches the minimum slice it needs (per-batter, per-pitcher, per-team) so the cell is fast on warm cache.

### Markdown Conventions
- Section intros: 2–4 sentences explaining what the next code block does and why.
- Takeaways: at the end of a non-trivial section, a code cell prints auto-derived bullets ("→ Hits LHP at .312 / .388 / .567 — significantly above his .288/.355/.510 overall").
- Bullets pulled from helper outputs, not hand-written commentary.

---

## Template 1 — Series Matchup

**Filename**: `reports/templates/notebooks/series-matchup.ipynb`

**Purpose**: In-depth comparison of two teams' recent form and head-to-head outlook ahead of a series.

### CLI

```
statslab new-notebook series-matchup --team-a SEA --team-b LAD
statslab new-notebook series-matchup --team-a SEA --team-b LAD --season 2026 --start 2026-05-15 --end 2026-05-20
```

### Parameters

```python
team_a = "SEA"
team_b = "LAD"
season = None
start_date = None
end_date = None
recent_form_games = 10   # last-N games for form analysis
```

### Sections

#### §1 — Series Overview
**Narrative intro**: Records, division standings, head-to-head this season (if any).

**Helpers used**:
- `data.get_standings(season)`
- `data.team_schedule(team_a, season)`, `data.team_schedule(team_b, season)` — filter to head-to-head and to last-N
- `data.normalize_team` to render names

**Output**: One markdown summary printed via `IPython.display.Markdown`. No chart.

#### §2 — Recent Form (Last 10)
**Narrative intro**: Run differential, wins/losses, key offensive/pitching trends in the last 10 games for each team.

**Code**:
```python
from mlb_stats_lab.data import get_statcast_for_team
from mlb_stats_lab.batting import batting_line
from mlb_stats_lab.pitching import pitching_line
from mlb_stats_lab.viz import rolling_metric_line

df_a = get_statcast_for_team(team_a, start=start_date, end=end_date)
df_b = get_statcast_for_team(team_b, start=start_date, end=end_date)

# Team batting line, last N games each
# ... compute and render
```

**Helpers used**: `get_statcast_for_team` (side="batting" for offense, "pitching" for staff), `batting_line`, `pitching_line`, filters by date.

**Charts**:
- `rolling_metric_line` — run differential over season for each team (twin lines).

#### §3 — Offense Compare
**Narrative intro**: Side-by-side offensive profile.

**Helpers used**: `batting_line` on each team's batting data; `performance_by_pitch_type` to compare how each handles fastballs vs breaking balls.

**Charts**:
- `splits_bar_chart` — AVG vs LHP / RHP for each team.
- `ev_la_scatter` — team batted-ball profile (one panel per team or overlay).

#### §4 — Pitching Compare
**Narrative intro**: Staff arsenals overall.

**Helpers used**: `arsenal_summary`, `pitch_movement` per team's staff.

**Charts**:
- `pitch_usage_bar` (vs_hand) — staff pitch mix per team.
- `velocity_distribution` — staff velocity by pitch type.

#### §5 — Key Matchups
**Narrative intro**: Top hitter from each team's expected lineup, top starter from each team's rotation.

**Helpers used**:
- `data.team_roster` or top-PA hitters from the team Statcast slice
- `batting_line`, `splits(axis="vs_hand")`, `contact_quality`
- `pitching_line`, `arsenal_summary`, `results_by_pitch`

**Charts**:
- `spray_chart` for each featured hitter.
- `pitch_movement_chart` for each featured starter.

#### §6 — Closing Summary
Auto-generated bullets:
- "→ SEA hitters are .258 wOBA over the last 10; LAD staff held opponents to .295 wOBA."
- "→ Both starters lean fastball-heavy (>55%) — expect a velocity-driven series."

Pulled from variables computed above. Rendered as Markdown.

---

## Template 2 — Batter Profile

**Filename**: `reports/templates/notebooks/batter-profile.ipynb`

**Purpose**: Deep-dive on a single hitter for the current season.

### CLI

```
statslab new-notebook batter-profile --player "Aaron Judge"
statslab new-notebook batter-profile --player "Julio Rodriguez" --season 2026
```

### Parameters

```python
player = "Aaron Judge"
season = None
start_date = None
end_date = None
recent_form_pas = 50    # last-N PAs for rolling charts
```

### Sections

#### §1 — Player Header
**Narrative intro**: Name, team, position, handedness, season-to-date PAs.

**Helpers used**:
- `data.resolve_player_id(player)`
- Pull header info from a small slice of Statcast (team via `home_team`/`away_team` derived from at-bats).

**Output**: Display block with name, team, current slash line teaser.

#### §2 — Season Line
**Narrative intro**: Full slash + power + plate discipline + contact quality.

**Code**:
```python
from mlb_stats_lab.data import get_statcast_batter
from mlb_stats_lab.batting import batting_line, plate_discipline, contact_quality

df = get_statcast_batter(player, start=start_date, end=end_date)
line = batting_line(df)
disc = plate_discipline(df)
contact = contact_quality(df)
```

**Output**:
- `batting_line` printed as a styled DataFrame (use `df.to_frame().T`).
- `plate_discipline` and `contact_quality` displayed side-by-side.

**Charts**: none in this section (numbers only).

#### §3 — Spray Chart
**Narrative intro**: Where they put the ball in play. Colored by outcome.

**Charts**:
- `spray_chart(df, team_color=<their team abbrev>)`

#### §4 — Plate Discipline / Zone Profile
**Narrative intro**: What they swing at, what they take, where pitchers come at them.

**Charts**:
- `zone_heatmap(df, metric="density")` — pitches they see.
- `zone_heatmap(df, metric="swing_rate")` — where they swing.
- `zone_grid(df, metric="xwoba")` — production by zone.

#### §5 — Contact Profile
**Narrative intro**: Launch angle / exit velocity profile, barrel rate.

**Charts**:
- `ev_la_scatter(df, color_by="outcome", overlay_barrel_zone=True)`
- `ev_distribution(df, by="bb_type")` (optional small panel)

#### §6 — Splits
**Narrative intro**: vs LHP/RHP, home/away, by month, leverage.

**Helpers used**: `splits(df, axis=...)` four times.

**Charts**:
- `splits_bar_chart(splits_hand, metric="wOBA")`
- `splits_bar_chart(splits_home_away, metric="wOBA")`
- `splits_bar_chart(splits_month, metric="wOBA")`
- `splits_bar_chart(splits_leverage, metric="wOBA")`

#### §7 — Performance by Pitch Type
**Narrative intro**: What they hit and what gets them.

**Helpers used**: `performance_by_pitch_type(df)`.

**Output**: Table sorted by pitches seen. No chart in v1 — optional `splits_bar_chart` over the pitch-type axis is a follow-up.

#### §8 — Recent Form
**Narrative intro**: Rolling wOBA / AVG over last N PAs.

**Helpers used**: `rolling_batting_line(df, window=recent_form_pas, over="PA")`.

**Charts**:
- `rolling_metric_line(rolling_df, metric="wOBA", league_average=0.320)`

#### §9 — Summary
Auto-generated takeaway bullets pulled from `line`, `disc`, `contact`, splits:
- "→ wOBA .378 — top decile vs RHP, average vs LHP."
- "→ Whiff% on breaking balls 32% — above MLB average (28%)."

---

## Template 3 — Pitcher Profile

**Filename**: `reports/templates/notebooks/pitcher-profile.ipynb`

**Purpose**: Deep-dive on a single pitcher for the current season.

### CLI

```
statslab new-notebook pitcher-profile --player "Logan Gilbert"
statslab new-notebook pitcher-profile --player "Tarik Skubal" --season 2026
```

### Parameters

```python
player = "Logan Gilbert"
season = None
start_date = None
end_date = None
recent_form_starts = 5
```

### Sections

#### §1 — Player Header
**Helpers used**: `data.resolve_player_id`, header info from a Statcast slice.

#### §2 — Season Line
**Code**:
```python
from mlb_stats_lab.data import get_statcast_pitcher
from mlb_stats_lab.pitching import pitching_line, command_metrics

df = get_statcast_pitcher(player, start=start_date, end=end_date)
line = pitching_line(df)
command = command_metrics(df)
```

**Output**: `pitching_line` + `command_metrics` tables.

#### §3 — Arsenal Overview
**Narrative intro**: Pitch mix, velocity, movement.

**Helpers used**: `arsenal_summary(df)`, `pitch_movement(df)`.

**Charts**:
- `pitch_movement_chart(df)` — the arsenal in break space.
- `velocity_distribution(df, kind="violin")`.
- `pitch_usage_pie(df)` — quick mix overview.

#### §4 — Pitch Usage by Context
**Narrative intro**: How usage shifts by handedness and count state.

**Charts**:
- `pitch_usage_bar(df, by="vs_hand")`
- `pitch_usage_bar(df, by="count_state")`

#### §5 — Location & Command
**Narrative intro**: Where each pitch goes, zone %, edge %.

**Charts**:
- `zone_heatmap(df, perspective="pitcher", metric="density")`
- `zone_grid(df, perspective="pitcher", metric="count")`
- `zone_heatmap(df_filter_to_FF, metric="density")` — repeated per primary pitch (loop over top 3 pitches).

#### §6 — Results by Pitch
**Narrative intro**: What each pitch does — whiff%, BAA, xwOBA.

**Helpers used**: `results_by_pitch(df)`.

**Output**: Table sorted by usage.

#### §7 — Splits
**Helpers used**: `pitching.splits(df, axis=...)` for vs_hand, home_away, times_through_order, leverage.

**Charts**: `splits_bar_chart` over each axis on K-BB%.

#### §8 — Recent Form
**Helpers used**: `rolling_pitching_line(df, window=recent_form_starts, over="starts")`.

**Charts**: `rolling_metric_line(rolling_df, metric="K%", league_average=0.225)`.

#### §9 — Summary
Auto bullets from `line`, `arsenal`, `command_metrics`:
- "→ K-BB% 19.4% (top quartile). FB sits 94.7, vert mov +18 in."
- "→ Whiff% on SL .402; that's the swing-and-miss pitch."

---

## Template 4 — Team Season Snapshot

**Filename**: `reports/templates/notebooks/team-season-snapshot.ipynb`

**Purpose**: Single team's season-to-date state of the union.

### CLI

```
statslab new-notebook team-season-snapshot --team SEA
statslab new-notebook team-season-snapshot --team LAD --season 2026
```

### Parameters

```python
team = "SEA"
season = None
start_date = None
end_date = None
recent_window_games = 15
```

### Sections

#### §1 — Standings + Record
**Helpers used**: `data.get_standings(season)`, `data.team_schedule(team, season)`.

**Output**: Record, division position, GB, last-10, streak.

#### §2 — Run Differential Trend
**Narrative intro**: Are they trending up or down?

**Helpers used**: derive per-game run diff from `team_schedule` (R-RA columns).

**Charts**: `rolling_metric_line` of run differential over the season.

#### §3 — Offense Summary
**Helpers used**:
- `data.get_team_batting(season)` → row for this team (Fangraphs season-level)
- `get_statcast_for_team(team, side="batting")` for Statcast-derived metrics
- `batting_line` on team-aggregate; `contact_quality`; `plate_discipline`

**Output**: Team slash + plate disc + contact quality.

**Charts**:
- `splits_bar_chart` for team vs LHP/RHP wOBA.
- `ev_la_scatter` for team batted-ball profile (sample-down for legibility).

#### §4 — Pitching Summary
**Helpers used**:
- `data.get_team_pitching(season)` for season-level
- `get_statcast_for_team(team, side="pitching")`
- `pitching_line` on staff aggregate
- `arsenal_summary` for staff pitch mix

**Charts**:
- `pitch_usage_bar(staff_df, by="overall")`
- `velocity_distribution(staff_df, kind="box")`.

#### §5 — Top Contributors
**Narrative intro**: Top 3 hitters by wOBA, top 3 pitchers by K-BB%.

**Helpers used**: Group `get_statcast_for_team` by batter / pitcher ID, run `batting_line` / `pitching_line` per player, sort.

**Output**: Tables of top-3 each side.

**Charts**: Optional mini-spray for #1 hitter, optional mini-arsenal for #1 starter.

#### §6 — Hot / Cold Recent
**Narrative intro**: Last-N games — who's hot, who's cold.

**Helpers used**: Filter to last-N games, recompute batting_line per hitter, sort by deltas vs season line.

**Output**: Markdown bullet list, no chart in v1.

#### §7 — Summary
Auto bullets from §3, §4, §6:
- "→ Offense ranks 8th in wOBA, 22nd vs LHP — a clear platoon weakness."
- "→ Staff K% top-5; HR/9 bottom-10 — strikeout-heavy but vulnerable to power."

---

## Cross-Template Patterns

### Auto-Bullet Helper

Templates frequently end with a `summary` cell that prints data-derived bullets. The pattern:

```python
from IPython.display import Markdown

bullets = []
if line["wOBA"] >= 0.350:
    bullets.append(f"→ wOBA {line['wOBA']:.3f} — top tier this season.")
if disc["Chase%"] >= 0.32:
    bullets.append(f"→ Chase% {disc['Chase%']:.1%} — aggressive; vulnerable to breakers off the plate.")
# ...
Markdown("\n".join(bullets) or "_No standout traits detected._")
```

A small utility may end up in `mlb_stats_lab.reports.summary` for shared bullet logic. Open item — flagged for later.

### Markdown Headings Convention

All section headers use `## §<N> <Section name>` so the table of contents extension in JupyterLab can render them.

### Cell Tags Convention

Templates use cell tags to make programmatic manipulation easy:

| Tag           | Meaning                                                    |
| ------------- | ---------------------------------------------------------- |
| `parameters`  | The single cell rewritten by CLI                           |
| `setup`       | Imports + season/date resolution                           |
| `load`        | Data fetch — biggest cost                                  |
| `section`     | Any analytical block                                       |
| `summary`     | The final auto-bullet cell                                 |
| `hidden`      | Cell that should be collapsed by default in JupyterLab UI  |

Tags can be inspected via `nbformat`: `nb.cells[i].metadata.get("tags", [])`.

---

## Authoring New Templates

Workflow for adding a template later:

1. Create `reports/templates/notebooks/<kebab-name>.ipynb` in JupyterLab.
2. Tag the parameters cell with `parameters` (Property Inspector → Common Tools → Add Tag).
3. Follow the standard cell structure above.
4. Register the template name in `mlb_stats_lab.cli` (decorator or registry — see `08_cli.md`).
5. Add a row to `reports/templates/README.md` describing usage.
6. Smoke-test via `nbclient` in CI to catch breakage when helper signatures change.

---

## Decision Log

| Decision                                              | Rationale                                                |
| ----------------------------------------------------- | -------------------------------------------------------- |
| Papermill-style `parameters` tag                      | Standard, nbformat-compatible, templates stay runnable   |
| No auto-execute in v1                                 | Slow first runs; user controls                           |
| Rich narrative + auto-bullets                         | Reports read better; matches PDF output story            |
| Stick with 4 templates in v1                          | Per scope lock-in                                        |
| Common skeleton (title/params/setup/load/sections/summary) | Consistency reduces cognitive overhead per template |
| Cell tags (`setup`, `load`, `section`, `summary`)     | Enables programmatic manipulation later (PDF export, etc.) |
| Dynamic title via IPython.display Markdown            | Avoids needing CLI to rewrite markdown cells too         |
| Templates run on minimum slice of data                | Fast on warm cache, clear ownership of fetch             |

---

## Open Items For Later Docs

- `mlb_stats_lab.reports.summary` shared bullet helpers — design defer to impl phase or `04_helper_catalog` revision
- PDF export: each template's notebook → PDF rendering rules → `07_pdf_reports.md`
- CLI args mapping: full `statslab new-notebook` surface → `08_cli.md`
- Game Recap template design — captured in scratch notes for v1.1
- Whether to ship a `blank` template (just imports + parameters scaffold) for greenfield analysis — flag during impl
