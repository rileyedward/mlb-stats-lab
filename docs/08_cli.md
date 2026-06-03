# 08 — CLI

> **Update (ergonomics overhaul).** Changes from the original plan below:
> - New **`statslab new`** guided command (questionary-backed) is the recommended
>   entry point: prompts for report type → subject → season → output format → run.
> - `list-templates` and `flush-cache` are now **flat `@app.command()`s**, not
>   sub-Typers.
> - `new-notebook <template>` gained **`--run/--no-run`** (execute via `nbclient`).
> - Notebook templates are loaded from jupytext `.py` (via `jupytext.read`), not
>   `.ipynb`; generated notebooks land in `notebooks/generated/`.
> - `_output.py` adds a `status()` spinner (shown during pybaseball fetch) and a
>   boxed `summary()` panel printed at the end of each command.

## Purpose

Defines the `statslab` CLI: command surface, argument shapes, registration mechanism, and how it bridges notebook templates (`06`) and PDF reports (`07`).

Stack: **Typer** (per `02_tech_stack.md`).

---

## Entry Point

Registered in `pyproject.toml`:

```toml
[project.scripts]
statslab = "mlb_stats_lab.cli:app"
```

`mlb_stats_lab.cli.app` is a `typer.Typer()` instance. Subcommands are imported from submodules and `app.add_typer(...)`-d.

Invocation pattern:

```
statslab <command> [args] [--options]
```

Run via `uv run statslab ...` during development.

---

## Module Surface

```
src/mlb_stats_lab/cli/
├── __init__.py         # app = typer.Typer(); attach subcommands
├── main.py             # callback: --version, --verbose, etc.
├── new_notebook.py     # `statslab new-notebook ...`
├── new_report.py       # `statslab new-report ...`
├── list_templates.py   # `statslab list-templates`
├── flush_cache.py      # `statslab flush-cache`
├── registry.py         # template registry: name → metadata + handler
└── _output.py          # rich-printing helpers
```

> Note: `rich` is bundled with `typer` for output formatting — no extra dep.

---

## Command Surface

### `statslab new-notebook <template> [options]`

Scaffold a parameterized `.ipynb` from a template under `reports/templates/notebooks/`.

**Subcommand handlers** (one per template, registered via registry):

```
statslab new-notebook series-matchup     --team-a SEA --team-b LAD [--season YEAR] [--start DATE] [--end DATE]
statslab new-notebook batter-profile     --player "Aaron Judge"   [--season YEAR] [--start DATE] [--end DATE]
statslab new-notebook pitcher-profile    --player "Logan Gilbert" [--season YEAR] [--start DATE] [--end DATE]
statslab new-notebook team-season-snapshot --team SEA              [--season YEAR] [--start DATE] [--end DATE]
```

**Behavior**:
1. Load template `.ipynb` via `nbformat`.
2. Find cell tagged `parameters`.
3. Rewrite its source with the new values.
4. Compute output filename per `01_architecture.md` naming rule.
5. Write to `reports/<filename>.ipynb` (path configurable).
6. Print the relative path of the generated file.

**Output**:
```
✓ Generated reports/batter_profile__aaron_judge__2026-05-20.ipynb
  Open with: uv run jupyter lab reports/batter_profile__aaron_judge__2026-05-20.ipynb
```

### `statslab new-report <template> [options]`

Render a PDF report directly (without going through a notebook).

```
statslab new-report batter-profile --player "Aaron Judge" [--season YEAR] [--out PATH]
statslab new-report pitcher-profile --player "Logan Gilbert" [--season YEAR] [--out PATH]
statslab new-report series-matchup --team-a SEA --team-b LAD [--season YEAR] [--out PATH]
statslab new-report team-season-snapshot --team SEA [--season YEAR] [--out PATH]
```

**Behavior**:
1. Resolve season/dates (auto-detect if not provided).
2. Call the template-specific "report builder" function (see Registry below) — fetches data, runs helpers, builds figures, assembles context.
3. Call `reports.render_report(template, context, output_path)`.
4. Print PDF path.

**Output**:
```
✓ Fetched data (cached) in 1.2s
✓ Rendered 9 charts
✓ Wrote reports/output/batter_profile__aaron_judge__2026-05-20.pdf
```

### `statslab list-templates`

List all available templates (notebook + PDF) with descriptions.

**Output**:
```
NOTEBOOK TEMPLATES
  series-matchup           Two-team series matchup analysis
  batter-profile           Single-hitter deep dive
  pitcher-profile          Single-pitcher deep dive
  team-season-snapshot     Team state-of-the-union

PDF TEMPLATES
  series-matchup           Series matchup → PDF
  batter-profile           Batter profile → PDF
  pitcher-profile          Pitcher profile → PDF
  team-season-snapshot     Team snapshot → PDF
```

### `statslab flush-cache [--older-than-days N]`

Convenience wrapper over `data.cache.flush(older_than_days=N)`.

```
statslab flush-cache
statslab flush-cache --older-than-days 30
```

**Output**: `✓ Removed 47 cached files.`

### Global Options (top-level callback)

```
statslab --version          Print version
statslab --verbose          Verbose logging (DEBUG level)
statslab --help             Help (per Typer convention; per-command also available)
```

---

## Template Registry

`cli/registry.py` is the bridge between CLI names and the implementation hooks. Single source of truth.

```python
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class TemplateSpec:
    name: str                                  # CLI name (kebab-case)
    description: str                           # for list-templates
    notebook_path: Path                        # reports/templates/notebooks/<name>.ipynb
    pdf_template: str                          # name passed to render_report
    parameter_keys: list[str]                  # which CLI args feed parameters
    builder: Callable[[dict], ReportContext]   # builds report context from args

TEMPLATES: dict[str, TemplateSpec] = {
    "series-matchup": TemplateSpec(
        name="series-matchup",
        description="Two-team series matchup analysis",
        notebook_path=Path("reports/templates/notebooks/series-matchup.ipynb"),
        pdf_template="series-matchup",
        parameter_keys=["team_a", "team_b", "season", "start_date", "end_date"],
        builder=build_series_matchup_context,
    ),
    "batter-profile": TemplateSpec(...),
    "pitcher-profile": TemplateSpec(...),
    "team-season-snapshot": TemplateSpec(...),
}
```

Builders live in `mlb_stats_lab.reports.context` (or a peer module) and are the shared core between `new-notebook` and `new-report`:

- `new-notebook` doesn't run the builder — it just rewrites the parameters cell. Builder gets invoked when the user runs the notebook.
- `new-report` runs the builder directly in-process, then calls `render_report`.

This split keeps the notebook experience independent of the headless-PDF experience while sharing the same "what does this template need" definition.

---

## Argument Conventions

### Naming
- CLI flag: kebab-case (`--team-a`, `--start`, `--end`).
- Typer auto-maps to snake_case Python args (`team_a`, `start`, `end`).

### Player names
- Quoted strings: `--player "Aaron Judge"`.
- Resolved via `data.resolve_player_id` at run time — `AmbiguousPlayerError` exits with non-zero and prints candidates.

### Team abbreviations
- Always 3-letter abbreviation (`--team SEA`). Case-insensitive — normalized via `data.normalize_team`.

### Dates
- ISO format only: `--start 2026-04-15`, `--end 2026-05-20`.
- Omitted → fall back to current season's range.

### Season
- `--season 2026`. Omitted → `data.current_season()`.

### Output paths
- `--out path/to/file.pdf` (only for `new-report`).
- Relative paths resolved under `[paths] output_dir` from `statslab.toml`.
- Omitted → default name per `01_architecture.md` convention.

---

## Error Handling & Exit Codes

| Condition                              | Exit code | Message                                                   |
| -------------------------------------- | --------- | --------------------------------------------------------- |
| Unknown template name                  | 2         | "Unknown template 'foo'. Run `statslab list-templates`."  |
| `AmbiguousPlayerError`                 | 2         | Lists candidates, suggests passing fuller name            |
| `UnknownPlayerError` / `UnknownTeamError` | 2     | Lists similar suggestions                                  |
| Missing required arg                   | 2         | Typer's default (auto-generated)                          |
| Pybaseball / network failure           | 1         | Wrapped message, suggests retry                           |
| Unexpected exception                   | 1         | Traceback only in `--verbose`, else short message         |

Typer's `typer.Exit(code=N)` used for explicit exits.

---

## Output Formatting

`_output.py` provides `rich`-backed helpers:

```python
def success(msg: str) -> None: ...     # ✓ green
def info(msg: str) -> None: ...        # • neutral
def warn(msg: str) -> None: ...        # ⚠ yellow
def fail(msg: str) -> None: ...        # ✗ red
def step(msg: str) -> None: ...        # prefixed with "→"
```

All CLI commands use these consistently.

---

## Example Sessions

### Generating a notebook

```sh
$ uv run statslab new-notebook batter-profile --player "Aaron Judge"
→ Loading template reports/templates/notebooks/batter-profile.ipynb
→ Rewriting parameters cell
✓ Generated reports/batter_profile__aaron_judge__2026-05-20.ipynb
  Open with: uv run jupyter lab reports/batter_profile__aaron_judge__2026-05-20.ipynb
```

### Generating a PDF directly

```sh
$ uv run statslab new-report pitcher-profile --player "Logan Gilbert" --out gilbert.pdf
→ Resolving player...
→ Fetching Statcast data...
✓ Loaded 1,847 pitches (cache hit)
→ Computing arsenal, location, results...
→ Rendering 7 charts...
→ Building PDF...
✓ Wrote reports/output/gilbert.pdf (412 KB)
```

### Listing templates

```sh
$ uv run statslab list-templates
NOTEBOOK TEMPLATES
  series-matchup           Two-team series matchup analysis
  batter-profile           Single-hitter deep dive
  pitcher-profile          Single-pitcher deep dive
  team-season-snapshot     Team state-of-the-union

PDF TEMPLATES
  series-matchup           Series matchup → PDF
  batter-profile           Batter profile → PDF
  pitcher-profile          Pitcher profile → PDF
  team-season-snapshot     Team snapshot → PDF
```

---

## Adding a New Template

When introducing a 5th template (say, `game-recap`):

1. Author the notebook template at `reports/templates/notebooks/game-recap.ipynb`.
2. Author the PDF template at `reports/templates/pdf/game-recap.html.j2`.
3. Add a `build_game_recap_context` builder in `reports/context.py`.
4. Add a `TemplateSpec(name="game-recap", ...)` entry to `TEMPLATES`.
5. Add a typed subcommand in `new_notebook.py` and `new_report.py` (or use a single dynamic dispatcher — see "Open Item" below).

That's it — `list-templates`, error messages, and registry-aware behavior pick it up automatically once `TEMPLATES` is updated.

---

## Decision Log

| Decision                                              | Rationale                                                |
| ----------------------------------------------------- | -------------------------------------------------------- |
| Typer for CLI                                         | Type-hint-driven, low boilerplate, built on Click        |
| Two commands: `new-notebook` + `new-report`           | Notebook and PDF flows have different cost profiles      |
| Shared `TemplateSpec` registry                        | Single source of truth for both flows                    |
| Builders live in `reports/context.py`                 | Reusable from notebook execution and from `new-report`   |
| Player resolution at run time, not in CLI parsing     | Allows the same `--player` arg shape everywhere          |
| ISO date format only                                  | Avoids locale/format ambiguity                           |
| Exit code 2 for usage / lookup errors                 | Distinguishes "user error" from "system failure"         |
| `rich` for output formatting                          | Bundled with Typer; consistent UX                        |

---

## Open Items For Later Docs / Impl

- Whether to use **per-template typed subcommands** (each its own Typer app with strict args) or **a single dynamic dispatcher** that consults the registry — leaning typed subcommands for discoverability + auto-help; revisit during implementation
- `statslab shell` REPL? Out of v1.
- `statslab serve` for local dashboard? Out of v1 (PRD didn't mention).
- Auto-completion (`statslab --install-completion`) — Typer handles this; document in `09_dev_setup.md`
