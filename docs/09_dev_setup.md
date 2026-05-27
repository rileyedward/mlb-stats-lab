# 09 — Dev Setup

## Purpose

End-to-end instructions for setting up the project from a fresh clone on macOS. A downstream coding agent can follow these steps verbatim to bootstrap the repo.

Target platform: **macOS** (per environment). Linux works too with apt equivalents noted where relevant.

---

## Prerequisites

### 1. Homebrew Packages

WeasyPrint requires system libraries that `uv` cannot install:

```sh
brew install pango cairo gdk-pixbuf libffi
```

(One-time. Skip if already installed.)

### 2. uv

If not already installed:

```sh
brew install uv
```

Or per the official installer at https://docs.astral.sh/uv/getting-started/installation/.

Verify:
```sh
uv --version    # should print uv 0.x.x
```

### 3. Git

Standard `git` from Xcode CLT or Homebrew. Verify `git --version`.

---

## Repository Bootstrap

### Clone

Final project location: `~/rileyedward/mlb-stats-lab/` (exact dir name TBD).

```sh
cd ~/rileyedward
# (clone or create)
cd mlb-stats-lab
```

### Initial Install

```sh
uv sync
```

This:
- Reads `pyproject.toml` and `uv.lock`.
- Creates `.venv/` in the repo root.
- Installs all runtime + dev dependencies.

Output should end with something like: `Installed 47 packages in 8.2s`.

### Verify Install

```sh
uv run python -c "import pybaseball, pandas, weasyprint, typer; print('ok')"
```

Should print `ok` with no errors. If WeasyPrint complains about missing libs, revisit Homebrew prereqs.

### Register Jupyter Kernel

So JupyterLab can find the project venv:

```sh
uv run python -m ipykernel install --user --name mlb-stats-lab --display-name "MLB Stats Lab"
```

One-time. Removes via `jupyter kernelspec remove mlb-stats-lab` if needed.

### Pre-Commit Hooks (Optional)

If pre-commit was kept in dev deps:

```sh
uv run pre-commit install
```

Now `ruff` + `mypy` run on every `git commit`.

---

## Daily Workflow

### Start JupyterLab

```sh
uv run jupyter lab
```

Opens browser. Hand-authored notebooks live under `notebooks/`; CLI-generated ones under `reports/`.

When creating a new notebook in JupyterLab, select the **"MLB Stats Lab"** kernel.

### Generate a Templated Notebook

```sh
uv run statslab new-notebook batter-profile --player "Aaron Judge"
```

Then open the generated file in JupyterLab.

### Generate a PDF Report

```sh
uv run statslab new-report batter-profile --player "Aaron Judge"
```

PDF lands in `reports/output/`.

### Inspect Cache

```sh
ls -lh ~/.pybaseball/cache/
```

If a query is misbehaving:

```sh
uv run statslab flush-cache --older-than-days 0
```

---

## Quality Commands

| Command                                      | Purpose                                |
| -------------------------------------------- | -------------------------------------- |
| `uv run ruff check src/ tests/`              | Lint                                   |
| `uv run ruff format src/ tests/`             | Format in place                        |
| `uv run mypy src/`                           | Type check                             |
| `uv run pytest`                              | Run tests                              |
| `uv run pytest -k <pattern>`                 | Run tests matching pattern             |
| `uv run pytest --cov`                        | Run with coverage                      |
| `uv run lint-imports`                        | Verify module dependency direction     |
| `uv run pre-commit run --all-files`          | Run all hooks against the whole repo   |

### Combined CI Equivalent

For "is this branch healthy?":

```sh
uv run ruff check src/ tests/ && \
uv run mypy src/ && \
uv run lint-imports && \
uv run pytest
```

A make-style runner can be added later (see Open Items).

---

## Adding a Dependency

Runtime:
```sh
uv add <pkg>
```

Dev only:
```sh
uv add --dev <pkg>
```

Updates `pyproject.toml` + `uv.lock`. Commit both.

---

## Upgrading Dependencies

```sh
uv lock --upgrade           # upgrade all per version constraints
uv lock --upgrade-package pandas
uv sync                     # apply lockfile to .venv
```

---

## Common Gotchas

### "WeasyPrint cannot find libpango"
Re-run the Homebrew install. If you're on Apple Silicon, ensure Homebrew is at `/opt/homebrew/bin` and your shell `PATH` includes it.

```sh
echo $PATH | tr ':' '\n' | grep homebrew
```

### "Jupyter cannot find the kernel"
Re-register:

```sh
uv run python -m ipykernel install --user --name mlb-stats-lab --display-name "MLB Stats Lab"
```

### Pybaseball returns empty DataFrame
- Check date range — early-season dates before opening day return nothing.
- Try `statslab flush-cache --older-than-days 0` to force a fresh fetch.
- Verify network — pybaseball calls live MLB endpoints.

### "AmbiguousPlayerError"
Multiple players match the given name. Pass a fuller name (e.g. `"Vladimir Guerrero Jr."`) or use the MLBAM ID via the by-ID escape hatch in the data layer.

### Stale cache after season transition
Pybaseball may cache responses past their useful life. Flush with `--older-than-days 7` after major data updates (mid-March, post-season).

---

## Project Configuration

Project-level config lives in `statslab.toml` at the repo root (see `01_architecture.md`):

```toml
[paths]
notebooks_dir = "notebooks"
reports_dir = "reports"
templates_dir = "reports/templates"
output_dir = "reports/output"

[season]
# Override auto-detection if needed
# default_year = 2026

[pybaseball]
cache_enabled = true
```

User-level overrides via env vars:

| Env var                  | Effect                                    |
| ------------------------ | ----------------------------------------- |
| `STATSLAB_SEASON`        | Overrides current season detection        |
| `STATSLAB_OUTPUT_DIR`    | Overrides PDF output dir                  |
| `STATSLAB_NOTEBOOKS_DIR` | Overrides user-authored notebooks dir     |
| `STATSLAB_VERBOSE`       | If set, CLI runs in verbose mode          |

---

## Editor Setup

### VSCode

Recommended extensions:
- **Python** (Microsoft)
- **Jupyter** (Microsoft)
- **Ruff** (Astral) — formatting + linting
- **mypy** (or Pylance for type hints)

Workspace `settings.json` snippet:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": { "source.organizeImports.ruff": "explicit" }
  }
}
```

### JupyterLab Extensions (Optional)

- **jupyterlab-toc** — table of contents pane reads `## §N` headings
- **jupyterlab-code-formatter** — apply ruff/black to notebook cells

---

## CLI Shell Completion

Typer ships completion:

```sh
uv run statslab --install-completion zsh   # or bash, fish
```

Restart the shell. Tab completion works on subcommands and template names.

---

## Decision Log

| Decision                                            | Rationale                                       |
| --------------------------------------------------- | ----------------------------------------------- |
| macOS Homebrew prereqs documented as one-time       | WeasyPrint needs them, not pip-installable      |
| `uv run` prefix for all commands                    | Always uses project venv, no manual activation  |
| Jupyter kernel registered via ipykernel             | Lets user pick "MLB Stats Lab" in any notebook  |
| `statslab.toml` for project paths                   | Easy reorg without code edits                   |
| Env-var overrides for one-off CLI runs              | Doesn't require editing the config file         |
| Optional pre-commit                                 | User-preference; not required                   |

---

## Open Items

- A `Makefile` (or `justfile`) wrapping the common commands — defer; document the raw commands here for now
- CI config (GitHub Actions) — out of v1, can add later
- Docker image — out of v1
- Linux-specific apt commands for WeasyPrint prereqs — add if/when targeting Linux
