# MLB Stats Lab

Personal MLB Statcast analytics playground. Pull pitch-level data via
[pybaseball](https://github.com/jldbc/pybaseball), explore it in JupyterLab, render
polished PDF reports.

## Quick Start

```sh
# 1. System deps (one time)
brew install pango cairo gdk-pixbuf libffi

# 2. Python deps
uv sync

# 3. Register Jupyter kernel
uv run python -m ipykernel install --user --name mlb-stats-lab --display-name "MLB Stats Lab"

# 4. Start working
uv run jupyter lab                                              # interactive
uv run statslab list-templates                                  # see what's available
uv run statslab new-notebook batter-profile --player "Aaron Judge"
uv run statslab new-report  batter-profile --player "Aaron Judge"
```

## Layout

```
src/mlb_stats_lab/   importable package (data, filters, batting, pitching, viz, reports, cli)
notebooks/           your hand-authored notebooks (gitignored)
reports/templates/   notebook + PDF templates (committed)
reports/             CLI-generated notebooks (gitignored)
reports/output/      rendered PDFs (gitignored)
docs/                design docs (architecture, data layer, viz, templates, CLI, roadmap)
tests/               pytest suite
```

See `docs/` for full architecture / data-layer / helper / viz / template / PDF /
CLI / dev-setup / roadmap specs.

## Common Commands

| Command | Purpose |
| --- | --- |
| `uv sync` | install deps |
| `uv run jupyter lab` | start JupyterLab |
| `uv run statslab list-templates` | available templates |
| `uv run statslab new-notebook <name> ...` | scaffold notebook |
| `uv run statslab new-report <name> ...` | render PDF directly |
| `uv run statslab flush-cache [--older-than-days N]` | clear pybaseball cache |
| `uv run pytest` | tests |
| `uv run ruff check src/ tests/` | lint |
| `uv run ruff format src/ tests/` | format |
| `uv run mypy src/` | type check |
| `uv run lint-imports` | enforce module dependency direction |
