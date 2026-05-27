# 10 — Roadmap

## Purpose

Phased build order for a downstream coding agent. Each phase is small, demoable, and ends with a clearly testable artifact. Dependencies are explicit so phases can be sequenced safely.

The phases below assume all decisions from `01`–`09` are locked. If the agent hits an open question, the answer is in that document's "Open Items" section or in the meta-plan at `/Users/rileygrotenhuis/.claude/plans/i-m-working-on-a-splendid-rocket.md`.

---

## Phase 1 — Repo Bootstrap

**Goal**: Empty but runnable project with `uv`, the package skeleton, and quality tooling wired up.

**Tasks**:
1. Create `~/rileyedward/mlb-stats-lab/` (or final dir name).
2. `uv init` and replace generated `pyproject.toml` with the spec from `02_tech_stack.md`.
3. Create `.python-version` (3.12), `.gitignore` (standard Python + `.venv/`, `reports/output/`, `reports/*.ipynb`, `.pybaseball/`).
4. Create `src/mlb_stats_lab/__init__.py` (empty package).
5. Add empty subpackage dirs per `01`: `data/`, `filters/`, `batting/`, `pitching/`, `viz/`, `reports/`, `cli/`, plus `__init__.py` in each.
6. Add `tests/` mirror with `__init__.py` stubs.
7. Add `statslab.toml` template at repo root (from `01_architecture.md`).
8. `uv sync` and verify the venv works.
9. Wire up ruff, mypy, pytest, import-linter configs (already in `pyproject.toml`).
10. Add `pre-commit` config (`02_tech_stack.md`) and run `uv run pre-commit install`.
11. Add a minimal `README.md` pointing to the planning docs.

**Done when**:
- `uv run ruff check src/` exits 0.
- `uv run mypy src/` exits 0.
- `uv run pytest` exits 0 (no tests yet — empty test run).
- `uv run lint-imports` exits 0 (empty packages still satisfy the contract).
- `uv run statslab --help` exits non-zero with helpful "no commands" message (expected pre-CLI).

---

## Phase 2 — Data Layer

**Goal**: `mlb_stats_lab.data` fully functional. Every helper downstream consumes its output.

**Tasks**:
1. `data/cache.py` — `enable_default`, `disable`, `flush`.
2. `data/dates.py` — `current_season`, `current_season_range`, `season_range`, `last_n_days`, `opening_day` (with a hardcoded 2025/2026 opening days table, fallback heuristic).
3. `data/teams.py` — `TEAMS` registry (all 30 teams w/ MLBAM ID), `normalize_team`, `team_schedule`.
4. `data/players.py` — `resolve_player_id` (with in-process cache + `AmbiguousPlayerError`), `player_name`, `team_roster`.
5. `data/exceptions.py` — `AmbiguousPlayerError`, `UnknownPlayerError`, `UnknownTeamError`.
6. `data/statcast.py` — `get_statcast`, `get_statcast_batter`, `get_statcast_pitcher`, `get_statcast_for_team`, `get_statcast_for_game`.
7. `data/season.py` — `get_team_batting`, `get_team_pitching`, `get_standings`.
8. `data/__init__.py` — re-export per the public surface in `03`. Call `cache.enable_default()`.
9. Tests:
   - Unit tests for `dates.py` (no network).
   - Unit tests for `teams.normalize_team` (no network).
   - Integration test for `resolve_player_id` against a small fixture or a network call (gated by env flag).
   - Smoke test for `get_statcast` (small date range, marked `@pytest.mark.network`).

**Done when**:
- All public functions in `03` have working implementations.
- Test suite runs in <60s offline (network-gated tests skipped without env flag).
- A bare notebook can `from mlb_stats_lab.data import *` and pull a real Statcast slice.

---

## Phase 3 — Filters

**Goal**: All filter helpers from `04` implemented and tested.

**Tasks**:
1. One module per filter family (`date.py`, `team.py`, `player.py`, `pitch.py`, `count.py`, `situation.py`, `result.py`).
2. `filters/__init__.py` re-exports the full public surface listed in `04`.
3. Each function: `(df, ...) -> df`, no mutation, pure.
4. Per-family tests using small DataFrame fixtures built in `tests/fixtures/`.

**Done when**:
- All filter helpers in `04` exist and are tested.
- `from mlb_stats_lab.filters import ...` works for every name in the catalog.
- `lint-imports` confirms `filters/` imports only `pandas` (no internal deps).

---

## Phase 4 — Batting + Pitching Helpers

**Goal**: All aggregators from `04` (excluding viz) implemented.

**Tasks**:
1. `batting/line.py` — `batting_line` (returns `pd.Series` with the full key set from `04`).
2. `batting/plate_discipline.py` — `plate_discipline`.
3. `batting/contact.py` — `contact_quality`.
4. `batting/splits.py` — `splits(df, axis=...)`.
5. `batting/by_pitch.py` — `performance_by_pitch_type`.
6. `batting/rolling.py` — `rolling_batting_line`.
7. `batting/__init__.py` re-exports.
8. `pitching/line.py` — `pitching_line`.
9. `pitching/arsenal.py` — `arsenal_summary`.
10. `pitching/movement.py` — `pitch_movement`.
11. `pitching/location.py` — `location_summary`.
12. `pitching/by_pitch.py` — `results_by_pitch`.
13. `pitching/command.py` — `command_metrics`.
14. `pitching/splits.py` — `splits(df, axis=...)`.
15. `pitching/rolling.py` — `rolling_pitching_line`.
16. `pitching/__init__.py` re-exports.
17. Per-function tests against a fixture DataFrame holding one batter's season + one pitcher's season (committed under `tests/fixtures/`).

**Done when**:
- Every function in `04` (excluding viz) exists.
- Test fixtures verify reasonable outputs (e.g. a known batter's AVG matches a known reference within rounding).
- `lint-imports` clean: batting/pitching import only pandas, numpy, and filters.

---

## Phase 5 — Visualization

**Goal**: All charts from `05` implemented.

**Tasks**:
1. `viz/theme.py` — `TEAM_COLORS`, `PITCH_COLORS`, `OUTCOME_COLORS`, `apply()`.
2. `viz/field.py` — `_draw_field_overlay(ax)`.
3. `viz/zone.py` — `_draw_zone_overlay(ax)`.
4. `viz/spray.py` — `spray_chart`.
5. `viz/heatmap.py` — `zone_heatmap`, `zone_grid`.
6. `viz/scatter.py` — `pitch_location_scatter`, `ev_la_scatter`.
7. `viz/arsenal.py` — `pitch_movement_chart`, `velocity_distribution`.
8. `viz/usage.py` — `pitch_usage_bar`, `pitch_usage_pie`.
9. `viz/rolling.py` — `rolling_metric_line`.
10. `viz/splits.py` — `splits_bar_chart`.
11. `viz/distributions.py` — `ev_distribution`, `la_distribution`, `velocity_box`.
12. `viz/save.py` — `fig_to_png`, `fig_to_svg`, `fig_to_bytes`.
13. `viz/__init__.py` re-exports + `theme.apply()`.
14. Smoke tests: each chart fn called against the fixture DataFrame, asserts that a `Figure` is returned with the expected number of axes. Visual diff testing optional/deferred.

**Done when**:
- Every chart in `05` exists, callable against fixtures.
- Manual eyeball check on a sample batter Profile: spray, zone heatmap, EV/LA scatter look right.
- `viz/` imports only pandas/numpy/matplotlib/seaborn (no batting/pitching).

---

## Phase 6 — Report Module + First End-to-End Template (Batter Profile)

**Goal**: One full path from CLI invocation → notebook → PDF working. Batter Profile is the canary.

**Tasks**:
1. `reports/engine.py` — Jinja env, `render_report`, `render_html`.
2. `reports/pdf.py` — `html_to_pdf` WeasyPrint wrapper.
3. `reports/assets.py` — `fig_to_data_uri`, `figs_to_context`.
4. `reports/filters.py` — `avg`, `pct`, `int`, `mph`, `team_color` Jinja filters.
5. `reports/context.py` — `BatterProfileContext` dataclass + `build_batter_profile_context(args) -> BatterProfileContext` builder.
6. `reports/summary.py` — initial bullet-builder helpers (small; expand as needed).
7. `reports/templates/pdf/_base.html.j2`, `_macros.html.j2`, `_styles.css`.
8. `reports/templates/pdf/batter-profile.html.j2` (per `07` example).
9. `reports/templates/notebooks/batter-profile.ipynb` (papermill-tagged parameters cell, full section flow from `06`).
10. `cli/registry.py` — `TemplateSpec` and `TEMPLATES` dict with the batter-profile entry.
11. `cli/new_notebook.py` — `new-notebook batter-profile --player <name>` working.
12. `cli/new_report.py` — `new-report batter-profile --player <name>` working.
13. `cli/list_templates.py` — `list-templates`.
14. `cli/flush_cache.py` — `flush-cache`.
15. `cli/__init__.py` — wire `app = typer.Typer()`, register subcommands.
16. `cli/_output.py` — rich-based pretty printing.
17. End-to-end smoke: `uv run statslab new-report batter-profile --player "Aaron Judge"` produces a PDF.
18. End-to-end smoke: `uv run statslab new-notebook batter-profile --player "Aaron Judge"`, then `nbclient` executes it to confirm runnability.

**Done when**:
- A valid PDF appears in `reports/output/` for a real player.
- The generated notebook opens in JupyterLab, runs cleanly, produces all charts.
- `statslab list-templates` lists batter-profile.

---

## Phase 7 — Remaining Three Templates

**Goal**: Pitcher Profile, Series Matchup, Team Season Snapshot at parity with Batter Profile.

**Tasks** (per template):
1. Notebook template `.ipynb` under `reports/templates/notebooks/`.
2. PDF template `.html.j2` under `reports/templates/pdf/`.
3. Context dataclass + builder in `reports/context.py`.
4. `TemplateSpec` registry entry.
5. CLI subcommand wiring.
6. End-to-end smoke (CLI new-notebook + execute, CLI new-report).

Order matters less here than completeness; recommended order:
- **Pitcher Profile** (close cousin to Batter Profile — reuses most viz)
- **Team Season Snapshot** (introduces team-level builders)
- **Series Matchup** (most complex — composes batter + pitcher + team logic)

**Done when**:
- `statslab list-templates` shows all four.
- All four PDFs render without error.
- All four notebooks execute via nbclient without error.

---

## Phase 8 — Notebook Smoke-Test CI

**Goal**: Catch template breakage automatically when helpers change.

**Tasks**:
1. Add `tests/templates/test_notebook_execution.py` — uses `nbclient` to execute each notebook template with default parameters against fixture data (or `@pytest.mark.network` for live data).
2. Add `tests/templates/test_pdf_render.py` — calls each builder against fixtures, runs `render_report`, asserts the PDF exists and is > some byte threshold.
3. Mark slow tests so the default `pytest` invocation stays fast.

**Done when**:
- A change that breaks any template's helper API fails a test before a PDF/notebook user sees it.

---

## Phase 9 — Documentation & Polish

**Goal**: Project is self-explanatory enough for daily use.

**Tasks**:
1. `README.md` — quick start, link to `docs/` copies of the planning docs.
2. Copy `00`–`10` planning docs into `docs/` in the repo (so they travel with the code).
3. `reports/templates/README.md` — describes each template, intended audience, args.
4. Ensure every public helper has a complete docblock matching the spec in `04`.
5. Add Typer shell completion install instructions to README.

**Done when**:
- A new contributor can clone, follow README, and produce their first PDF in under 10 minutes.

---

## Phase 10 — Backlog / v1.1 Candidates

Captured for later. Not part of v1.

| Item                                    | Source doc        |
| --------------------------------------- | ----------------- |
| Game Recap template                     | `06`              |
| Historical multi-season analysis        | `00_meta_plan`    |
| `fielding/` module                      | `04`              |
| Team logo PNG embedding in PDFs         | `07`              |
| Auto-execute flag on `new-notebook`     | `06`              |
| `statslab serve` local dashboard        | `08`              |
| GitHub Actions CI                       | `09`              |
| Dockerfile                              | `09`              |
| Per-pitch sequence chart (Game Recap)   | `05`              |
| `splits` axis `times_through_order`     | `04` (may be v1) |

---

## Phase 1 — First Task For The Downstream Agent

If the agent has just been handed all 10 docs and asks "where do I start?" — the answer:

> **Create the repo skeleton per Phase 1. Specifically:**
>
> 1. `cd ~/rileyedward`
> 2. Decide the repo dir name (suggest `mlb-stats-lab`).
> 3. `mkdir mlb-stats-lab && cd mlb-stats-lab`
> 4. `uv init`
> 5. Replace the generated `pyproject.toml` with the spec from `02_tech_stack.md`.
> 6. Create the `src/mlb_stats_lab/` layout from `01_architecture.md` with empty `__init__.py` files in every subpackage.
> 7. Add `.python-version`, `.gitignore`, `statslab.toml` template, `README.md` stub.
> 8. `uv sync`
> 9. Verify `uv run ruff check src/` and `uv run mypy src/` both exit 0 (against empty packages).
> 10. Commit: "chore: bootstrap repo skeleton per 01/02".
>
> Once those pass, move to Phase 2 (Data Layer).

---

## Cross-Phase Rules

- **Never skip phases.** Each builds on the prior. Skipping risks rework.
- **Tests land in the same phase as the code.** Don't defer testing to a "testing phase."
- **One PR per phase** (or per major step in a long phase). Keeps diffs reviewable.
- **`lint-imports` clean after every phase.** Prevents architectural drift.
- **If a phase reveals a missing spec**, update the relevant `01`–`09` doc *before* implementing the fix in code. Docs lead, code follows.

---

## Verification Checklist (Project-Wide)

Final acceptance for v1:

- [ ] `uv sync` from scratch produces a clean venv.
- [ ] `uv run pytest` passes (offline; network tests skipped).
- [ ] `uv run mypy src/` passes strict.
- [ ] `uv run ruff check src/ tests/` passes.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run statslab list-templates` shows all four.
- [ ] `uv run statslab new-notebook batter-profile --player "Aaron Judge"` generates a notebook.
- [ ] Generated notebook runs cleanly to completion in JupyterLab.
- [ ] `uv run statslab new-report batter-profile --player "Aaron Judge"` writes a valid PDF.
- [ ] Same three checks pass for pitcher-profile, series-matchup, team-season-snapshot.

When every box is ticked, v1 is shipped.
