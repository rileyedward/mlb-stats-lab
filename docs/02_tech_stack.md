# 02 — Tech Stack

## Purpose

Locks the full dependency list, dev tooling, and `pyproject.toml` shape. A downstream agent should be able to run `uv init` followed by `uv add` commands from this doc and reproduce the project's environment exactly.

---

## Python Version & Package Manager

- **Python**: `3.12` (pinned via `.python-version`)
- **Package manager**: `uv`
- `.python-version` file at repo root contains `3.12`
- `uv` will create and manage `.venv/` automatically

### uv Workflow

| Action                        | Command                                     |
| ----------------------------- | ------------------------------------------- |
| Initial setup                 | `uv sync`                                   |
| Add a runtime dep             | `uv add <pkg>`                              |
| Add a dev dep                 | `uv add --dev <pkg>`                        |
| Run a script in venv          | `uv run <cmd>`                              |
| Run pytest                    | `uv run pytest`                             |
| Run statslab CLI              | `uv run statslab <subcommand>`              |
| Update lockfile               | `uv lock`                                   |
| Upgrade all                   | `uv lock --upgrade`                         |

Lockfile `uv.lock` is committed. `.venv/` is gitignored.

---

## Runtime Dependencies

Version policy: **lower-bound only** for libraries (e.g. `pandas>=2.2`), **exact pin** for any lib with breaking-change risk we want to avoid. `uv.lock` provides the reproducible resolution.

### Data Layer
| Package      | Min Version | Why                                                       |
| ------------ | ----------- | --------------------------------------------------------- |
| `pybaseball` | `>=2.2.7`   | Statcast access, ships `cache.enable()`                   |
| `pandas`     | `>=2.2`     | Core DataFrame engine                                     |
| `numpy`      | `>=1.26`    | Pandas requirement + direct numerical work                |
| `pyarrow`    | `>=15.0`    | Parquet support (pybaseball cache uses it under the hood) |

### Notebooks
| Package      | Min Version | Why                                              |
| ------------ | ----------- | ------------------------------------------------ |
| `jupyterlab` | `>=4.1`     | Notebook IDE                                     |
| `ipykernel`  | `>=6.29`    | Registers the project venv as a Jupyter kernel   |

### Visualization
| Package      | Min Version | Why                              |
| ------------ | ----------- | -------------------------------- |
| `matplotlib` | `>=3.8`     | Underlying figure/axes API       |
| `seaborn`    | `>=0.13`    | Statistical chart shortcuts      |

### Reports (PDF)
| Package      | Min Version | Why                                                                 |
| ------------ | ----------- | ------------------------------------------------------------------- |
| `jinja2`     | `>=3.1`     | HTML template rendering                                             |
| `weasyprint` | `>=61.0`    | HTML/CSS → PDF (requires system libs — see WeasyPrint Notes below)  |

### CLI
| Package | Min Version | Why                                              |
| ------- | ----------- | ------------------------------------------------ |
| `typer` | `>=0.12`    | Type-hint-driven CLI, built on Click             |

### Config
Python 3.12 has stdlib `tomllib` (read-only) — used for parsing `statslab.toml`. No extra dep.

---

## Dev Dependencies

| Package         | Purpose                                                      |
| --------------- | ------------------------------------------------------------ |
| `pytest`        | Test runner                                                  |
| `nbclient`      | Execute notebook templates in CI (smoke test)                |
| `nbformat`      | Read/write `.ipynb` files programmatically (used by CLI too) |
| `ruff`          | Lint + format (replaces black/isort/flake8)                  |
| `mypy`          | Static type checking                                         |
| `import-linter` | Enforces the one-way module dependency rule from `01`        |
| `pre-commit`    | Git hook runner — runs ruff/mypy before commits              |

> **Note:** `nbformat` is also a runtime dep (the CLI generates notebooks from templates). It will appear under runtime, not dev. Listed here too because tests use it.

> **Open item:** User did not explicitly confirm pre-commit / pytest-cov in Q&A. Drop either if you don't want the ceremony — both are optional. Recommended to keep `import-linter` and `nbclient` regardless (they protect the architecture and the template scaffolds respectively).

---

## `pyproject.toml` Shape

```toml
[project]
name = "mlb-stats-lab"
version = "0.1.0"
description = "MLB Statcast analytics playground"
readme = "README.md"
requires-python = ">=3.12"
authors = [{ name = "Riley Grotenhuis" }]

dependencies = [
    "pybaseball>=2.2.7",
    "pandas>=2.2",
    "numpy>=1.26",
    "pyarrow>=15.0",
    "jupyterlab>=4.1",
    "ipykernel>=6.29",
    "matplotlib>=3.8",
    "seaborn>=0.13",
    "jinja2>=3.1",
    "weasyprint>=61.0",
    "typer>=0.12",
    "nbformat>=5.10",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "nbclient>=0.10",
    "ruff>=0.5",
    "mypy>=1.10",
    "import-linter>=2.0",
    "pre-commit>=3.7",
]

[project.scripts]
statslab = "mlb_stats_lab.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mlb_stats_lab"]

# ---- ruff ----
[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E", "F", "W",   # pycodestyle + pyflakes
    "I",             # isort
    "N",             # pep8-naming
    "UP",            # pyupgrade
    "B",             # bugbear
    "SIM",           # simplify
    "RUF",           # ruff-specific
]

[tool.ruff.format]
quote-style = "double"

# ---- mypy ----
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src/mlb_stats_lab"]

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
check_untyped_defs = true

[[tool.mypy.overrides]]
module = ["pybaseball.*", "weasyprint.*"]
ignore_missing_imports = true

# ---- pytest ----
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --cov=mlb_stats_lab --cov-report=term-missing"

# ---- import-linter ----
[tool.importlinter]
root_package = "mlb_stats_lab"

[[tool.importlinter.contracts]]
name = "Layered module dependencies"
type = "layers"
layers = [
    "mlb_stats_lab.cli",
    "mlb_stats_lab.reports",
    "mlb_stats_lab.viz",
    "mlb_stats_lab.batting | mlb_stats_lab.pitching | mlb_stats_lab.fielding",
    "mlb_stats_lab.filters",
    "mlb_stats_lab.data",
    "mlb_stats_lab.config",
]
```

> Reading the layers contract: top of list depends on layers below; bottom layer (`config`) imports nothing from inside `mlb_stats_lab`. Matches the arrow from `01_architecture.md`.

---

## `pre-commit` Config (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-yaml
      - id: check-toml

  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: uv run mypy
        language: system
        types: [python]
        pass_filenames: false
        args: [src/mlb_stats_lab]
```

Install: `uv run pre-commit install`.

---

## Pybaseball Notes

- Pybaseball ships `cache.enable()` which writes Parquet files to `~/.pybaseball/cache/`. We use that — no custom cache layer (confirmed in `00` planning).
- Be aware: pybaseball wraps the unofficial `baseballsavant.mlb.com` endpoints. Occasional schema drift happens season-to-season. If columns disappear, the `data/` module's wrappers absorb the change.
- Statcast date-range queries (`statcast(start_dt, end_dt)`) page by week. Long ranges = slow first call. Cache makes subsequent calls trivial.

### Pinning Recommendation

Watch pybaseball's release notes around mid-March (spring training) for new-season fixes. Bump `pybaseball` first when a new season starts.

---

## WeasyPrint System Dependencies (macOS)

WeasyPrint needs system libs that `uv` cannot install. One-time Homebrew install:

```sh
brew install pango cairo gdk-pixbuf libffi
```

Document this in `09_dev_setup.md` as part of bootstrap.

---

## Jupyter Kernel Registration

After `uv sync`, register the venv as a Jupyter kernel so the user can select it from JupyterLab:

```sh
uv run python -m ipykernel install --user --name mlb-stats-lab --display-name "MLB Stats Lab"
```

---

## Project Scripts Surface

| Command                       | What it does                                |
| ----------------------------- | ------------------------------------------- |
| `uv sync`                     | Install deps from lockfile                  |
| `uv run jupyter lab`          | Start JupyterLab                            |
| `uv run statslab <subcmd>`    | Run CLI                                     |
| `uv run pytest`               | Run tests                                   |
| `uv run mypy src/`            | Type-check source                           |
| `uv run ruff check src/ tests/` | Lint                                      |
| `uv run ruff format src/ tests/` | Format                                   |
| `uv run lint-imports`         | Enforce module dependency direction         |

These will be documented end-to-end in `09_dev_setup.md`.

---

## Decision Log

| Decision                            | Rationale                                                  |
| ----------------------------------- | ---------------------------------------------------------- |
| Python 3.12                         | Stable, stdlib `tomllib`, wide ecosystem support           |
| `uv` package manager                | Fast, deterministic, modern (per PRD)                      |
| Typer for CLI                       | Type-hint driven, low boilerplate, built on Click          |
| matplotlib + seaborn (no plotly)    | PDF-friendly static charts                                 |
| WeasyPrint for PDF                  | HTML/CSS templating ergonomic; layout control              |
| mypy strict on `src/`               | Helper signatures are public API — type safety matters     |
| ruff for lint + format              | One tool, fast, replaces black/isort/flake8                |
| import-linter                       | Encodes the `01_architecture.md` dependency rule           |
| `uv.lock` committed                 | Reproducible installs                                      |
| `nbformat` as runtime dep           | CLI uses it to generate notebooks from templates           |
| WeasyPrint sys deps via Homebrew    | Cannot be installed via uv; document in dev setup          |

---

## Open Items For User

- Confirm or drop: `pre-commit`, `pytest-cov` (both optional)
- Confirm or drop: `import-linter` (recommended — encodes architecture rule)
- Final repo dir name under `~/rileyedward/` (e.g. `mlb-stats-lab`)
