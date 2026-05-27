# 01 — Architecture

## Purpose

Defines the repo layout, package structure, module boundaries, and naming conventions for **MLB Stats Lab**. This is the foundation every later doc references. A downstream coding agent should be able to scaffold the project from this document alone.

## Scope Confirmations

- **Local-only tool.** No authentication, no multi-user concerns, no remote deployment. Runs on the user's Mac, in Jupyter, with PDFs generated to disk.
- **v1 = current MLB season only.** Historical analysis deferred.
- **Python 3 + `uv`.**

---

## Top-Level Repo Layout

Repo will live at `~/rileyedward/mlb-stats-lab/` (final dir name TBD by user).

```
mlb-stats-lab/
├── pyproject.toml
├── uv.lock
├── README.md
├── .gitignore
├── .python-version
├── statslab.toml            # user-level config (output paths, defaults)
│
├── src/
│   └── mlb_stats_lab/       # importable package (src-layout)
│       ├── __init__.py
│       ├── config.py        # loads statslab.toml + env overrides
│       ├── data/            # pybaseball wrappers, cache config
│       ├── filters/         # date, team, player, pitch, situational filters
│       ├── batting/         # batting domain helpers
│       ├── pitching/        # pitching domain helpers
│       ├── fielding/        # fielding domain helpers
│       ├── viz/             # matplotlib/seaborn chart helpers
│       ├── reports/         # Jinja env, HTML→PDF rendering pipeline
│       └── cli/             # statslab CLI entry point + commands
│
├── notebooks/               # USER-AUTHORED .ipynb files (hand-written analysis)
│   └── .gitkeep
│
├── reports/                 # report-related artifacts
│   ├── templates/           # template SOURCES
│   │   ├── notebooks/       # .ipynb scaffolds (series_matchup.ipynb, etc.)
│   │   └── pdf/             # Jinja HTML/CSS templates for PDF reports
│   ├── output/              # GENERATED PDFs (gitignored)
│   └── *.ipynb              # GENERATED notebooks from CLI (gitignored)
│
├── tests/
│   ├── unit/
│   └── fixtures/            # cached pybaseball sample data for tests
│
└── docs/                    # (eventually) the planning docs from this obsidian set
```

### Notes on the `reports/` directory

`reports/` plays three roles, separated by subdir:

| Path                          | Role                            | Git-tracked? |
| ----------------------------- | ------------------------------- | ------------ |
| `reports/templates/notebooks/`| Source `.ipynb` scaffolds       | Yes          |
| `reports/templates/pdf/`      | Jinja HTML + CSS for PDFs       | Yes          |
| `reports/<name>.ipynb`        | CLI-generated notebooks         | No           |
| `reports/output/*.pdf`        | Rendered PDF reports            | No           |

These paths are **configurable** via `statslab.toml` (see Configuration below) — the defaults above are conventions, not hardcoded.

### Notes on `notebooks/` vs `reports/`

- **`notebooks/`** → your hand-authored exploratory work. Free-form. Whatever you create yourself.
- **`reports/`** → CLI-generated notebooks (filled from templates) and their PDF output.

This split makes it obvious which work is bespoke vs scaffolded.

---

## Package Module Boundaries

### `mlb_stats_lab.data`
- Wraps pybaseball entry points (`statcast`, `statcast_batter`, `statcast_pitcher`, etc.)
- Enables `pybaseball.cache.enable()` on import
- Provides season-aware date helpers (`current_season_range()`, `season_to_date_range(year)`)
- Returns plain `pandas.DataFrame` — no custom wrapper types
- **Imports**: pybaseball, pandas
- **Imported by**: filters, batting, pitching, fielding, cli

### `mlb_stats_lab.filters`
- Pure DataFrame → DataFrame transforms
- Functions take a Statcast DataFrame and filter args, return filtered DataFrame
- Examples: `by_date_range`, `by_team`, `by_batter`, `by_pitcher`, `by_pitch_type`, `by_count`, `by_inning`, `by_runners_on`
- **Imports**: pandas (only)
- **Imported by**: batting, pitching, fielding, viz, notebooks, CLI scaffolds

### `mlb_stats_lab.batting`, `mlb_stats_lab.pitching`, `mlb_stats_lab.fielding`
- Domain-specific aggregations and computed stats
- Each domain owns its own module(s) — e.g. `batting/batting_line.py`, `batting/splits.py`, `batting/plate_discipline.py`
- Functions take filtered DataFrames in, return DataFrames or Series with aggregated metrics
- **Imports**: pandas, numpy, filters (allowed but optional — most functions accept already-filtered data)
- **Imported by**: viz, notebooks, CLI scaffolds, reports

### `mlb_stats_lab.viz`
- matplotlib/seaborn chart factories
- Each function: takes a DataFrame (or aggregated result), returns a `matplotlib.figure.Figure`
- No `plt.show()` inside — caller decides display vs save
- Provides save-to-PNG/SVG helpers for embedding in PDFs
- **Imports**: matplotlib, seaborn, pandas, numpy
- **Imported by**: notebooks, reports, CLI scaffolds

### `mlb_stats_lab.reports`
- Jinja2 environment setup
- HTML template → PDF rendering via WeasyPrint
- Asset embedding (chart PNGs/SVGs into HTML)
- Entry function: `render_report(template_name, context, output_path)`
- **Imports**: jinja2, weasyprint, viz (for chart generation if needed)
- **Imported by**: cli

> Naming note: `src/mlb_stats_lab/reports/` (the Python module) and `reports/` (the repo top-level dir for templates+outputs) share a name but live in different filesystem trees, so there is no actual collision. The Python module operates on the top-level `reports/` dir as data.

### `mlb_stats_lab.cli`
- CLI entry point: `statslab` (registered in `pyproject.toml` under `[project.scripts]`)
- Subcommands: `new-notebook`, `new-report`, `list-templates`, others TBD in `08_cli.md`
- Uses click or typer (TBD in `02_tech_stack.md`)
- **Imports**: every other subpackage (top of the dependency graph)
- **Imported by**: nothing internal

### Import-Direction Rule

```
data  →  filters  →  {batting, pitching, fielding}  →  viz  →  reports  →  cli
```

Strict one-way arrows. No back-imports. Lint rule (e.g. import-linter contract) to be configured in `02_tech_stack.md`.

---

## Naming Conventions

### Functions
- `snake_case`
- Verbs for transforms (`filter_by_team`, `compute_batting_line`)
- Nouns for builders/queries (`spray_chart`, `pitch_arsenal`)
- Predicate helpers: `is_*`, `has_*`

### Files
- `snake_case.py`
- One conceptual unit per file when the file > ~150 lines
- Re-export public API via subpackage `__init__.py`: `from mlb_stats_lab.batting import batting_line, splits`

### Notebook Filenames (CLI-generated)
Format: `<template>__<key-args>__<YYYY-MM-DD>.ipynb`

Examples:
- `series_matchup__SEA_vs_LAD__2026-05-20.ipynb`
- `batter_profile__judge__2026-05-20.ipynb`

Underscores between segments, double-underscore as section separator.

### PDF Filenames (CLI-generated)
Same convention with `.pdf` extension, landing in `reports/output/`.

---

## Entry Points

### Python Import
```python
from mlb_stats_lab.data import get_season_statcast
from mlb_stats_lab.filters import by_team, by_pitch_type
from mlb_stats_lab.batting import batting_line
from mlb_stats_lab.viz import spray_chart
```

### CLI
```
statslab new-notebook series-matchup --team-a SEA --team-b LAD
statslab new-report batter-profile --player "Aaron Judge"
statslab list-templates
```

Full surface in `08_cli.md`.

### Jupyter
- Kernel name: `mlb-stats-lab` (registered via `python -m ipykernel install --user --name mlb-stats-lab`)
- Default first-cell imports defined by notebook templates

---

## Configuration

### `statslab.toml` (repo-root file, gitignored optional)

User-overridable config:

```toml
[paths]
notebooks_dir = "notebooks"
reports_dir = "reports"
templates_dir = "reports/templates"
output_dir = "reports/output"

[season]
default_year = 2026     # overrides "current year" detection if set

[pybaseball]
cache_enabled = true
```

Loaded by `mlb_stats_lab.config` with `[paths]` paths resolved relative to repo root. Env vars `STATSLAB_*` override.

### Pybaseball Cache Location
Default pybaseball cache (`~/.pybaseball/cache/`) is fine — no override needed unless user wants project-local cache.

---

## Test Layout

- `tests/unit/` mirrors `src/mlb_stats_lab/` structure
- `tests/fixtures/` holds small Parquet snapshots of Statcast data for offline tests
- Domain helpers tested against fixtures (no live pybaseball calls in CI)
- Notebook templates smoke-tested via `nbclient` execution

Details deferred to `02_tech_stack.md` (pytest config).

---

## What Lives Where — Quick Lookup

| You want to…                       | Look in…                              |
| ---------------------------------- | ------------------------------------- |
| Fetch Statcast data                | `src/mlb_stats_lab/data/`             |
| Filter a DataFrame                 | `src/mlb_stats_lab/filters/`          |
| Compute a batting/pitching stat    | `src/mlb_stats_lab/{batting,pitching}/` |
| Draw a chart                       | `src/mlb_stats_lab/viz/`              |
| Generate a PDF                     | `src/mlb_stats_lab/reports/`          |
| Add a CLI command                  | `src/mlb_stats_lab/cli/`              |
| Add a new notebook template        | `reports/templates/notebooks/`        |
| Add a new PDF template             | `reports/templates/pdf/`              |
| Author ad-hoc analysis             | `notebooks/`                          |

---

## Open Questions (Defer To Later Docs)

- Exact deps + versions → `02_tech_stack.md`
- Click vs Typer for CLI → `02_tech_stack.md`
- Specific pybaseball functions to wrap → `03_data_layer.md`
- Helper signatures → `04_helper_catalog.md`
- Repo dir name under `~/rileyedward/` (e.g. `mlb-stats-lab` vs `statslab`) → user decision when bootstrapping

## Decision Log

| Decision                              | Rationale                                            |
| ------------------------------------- | ---------------------------------------------------- |
| `src/` layout                         | Prevents accidental cwd imports, modern standard      |
| Package name `mlb_stats_lab`          | Explicit, matches project                            |
| CLI binary `statslab`                 | Short typing, no MLB acronym collision               |
| `notebooks/` vs `reports/` split      | User-authored vs generated                           |
| `reports/templates/{notebooks,pdf}/`  | Single template root, subdivided by output type      |
| Configurable paths via `statslab.toml`| Allows reorg without code changes                    |
| One-way module dependency graph       | Prevents circular imports, enforces clean layers     |
| No auth / no remote                   | Local-only personal tool                             |
