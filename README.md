# MLB Stats Lab

Personal MLB Statcast analytics playground. Pull pitch-level data via
[pybaseball](https://github.com/jldbc/pybaseball), explore it in JupyterLab, render
polished team-themed PDF reports.

## Quick Start

```sh
# 1. System deps (one time). On Apple Silicon use the arm64 Homebrew:
arch -arm64 brew install pango cairo gdk-pixbuf libffi

# 2. Python deps
uv sync --all-extras

# 3. Register the Jupyter kernel (matches the kernel templates target)
uv run python -m ipykernel install --user --name mlb-stats-lab --display-name "MLB Stats Lab"

# 4. (optional) install the git hooks
uv run pre-commit install

# 5. Start working
uv run statslab new                 # guided: pick report type, subject, format
uv run jupyter lab                  # interactive exploration
```

> **PDF rendering** uses WeasyPrint, which loads native pango/cairo/glib libraries.
> On Apple Silicon they must be the **arm64** builds (`/opt/homebrew`). If you see a
> `dlopen … incompatible architecture` error, your libs are the Intel (`/usr/local`)
> build — reinstall with `arch -arm64 brew install …`.

## Common Workflows

```sh
# Guided, interactive (recommended entry point)
uv run statslab new

# Scaffold a notebook (writes to notebooks/generated/, does not run it)
uv run statslab new-notebook batter-profile --player "Aaron Judge"

# Scaffold AND execute, so the notebook is fully populated when it opens
uv run statslab new-notebook batter-profile --player "Aaron Judge" --run

# Render a PDF directly (no notebook)
uv run statslab new-report batter-profile --player "Aaron Judge"
```

## Layout

```
src/mlb_stats_lab/          importable package (data, filters, batting, pitching, viz, reports, cli)
notebooks/                  your hand-authored notebooks (gitignored)
notebooks/generated/        CLI-generated notebooks (gitignored)
reports/templates/notebooks/ jupytext .py templates — SOURCE OF TRUTH (committed)
reports/templates/pdf/      Jinja2 HTML/CSS PDF templates (committed)
reports/output/             rendered PDFs (gitignored)
docs/                       design docs (architecture, data layer, viz, templates, CLI, roadmap)
tests/                      pytest suite
```

Notebook templates are authored as **percent-format `.py`** files paired to `.ipynb`
via [jupytext](https://jupytext.readthedocs.io) (`[tool.jupytext]` in `pyproject.toml`).
Edit the `.py` (in any editor or in Jupyter); the `.ipynb` is regenerated on demand —
no separate generator script.

## Commands

| Command | Purpose |
| --- | --- |
| `uv run statslab new` | guided notebook/PDF builder (recommended) |
| `uv run statslab list-templates` | available templates |
| `uv run statslab new-notebook <name> ... [--run]` | scaffold (and optionally execute) a notebook |
| `uv run statslab new-report <name> ...` | render a PDF directly |
| `uv run statslab flush-cache [--older-than-days N]` | clear pybaseball cache |
| `uv run jupyter lab` | start JupyterLab |
| `uv run jupytext --sync reports/templates/notebooks/<name>.py` | pair `.py` ⇄ `.ipynb` |
| `uv run pytest -m "not network"` | tests (offline) |
| `uv run ruff check src/ tests/` / `ruff format src/ tests/` | lint / format |
| `uv run mypy src/` | type check |
| `uv run lint-imports` | enforce module dependency direction |
| `uv run pre-commit run --all-files` | run all hooks |

See `docs/` for full architecture / data-layer / helper / viz / template / PDF /
CLI / dev-setup / roadmap specs.
