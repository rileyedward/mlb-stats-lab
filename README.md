# MLB Stats Lab

MLB Statcast analytics playground with notebooks and team-themed PDF reports.

> **Status:** Active — in development.

## Overview

### What is MLB Stats Lab?

MLB Stats Lab is a personal MLB Statcast analytics playground. It pulls pitch-level data through [pybaseball](https://github.com/jldbc/pybaseball), lets you explore it in JupyterLab, and renders polished, team-themed PDF reports. A small CLI, `statslab`, scaffolds notebooks and reports from templates so a new batter or pitcher profile is one command away.

### Key Features

- **Guided Builder**: `statslab new` walks you through picking a report type, subject and format.
- **Notebook Scaffolding**: Generate a notebook from a template, and optionally execute it so it opens fully populated.
- **PDF Reports**: Render team-themed PDF reports directly, without a notebook.
- **Jupytext Templates**: Notebook templates are plain percent-format `.py` files paired to `.ipynb`, so they diff and edit cleanly.

## Getting Started

### Prerequisites

Ensure you have the following installed. You can verify each one by running the provided command in your terminal.

1. **Python** (3.12+) runs the project. Check it by running:

    ```bash
    python3 --version
    ```

2. **uv** manages the Python environment and dependencies. Check it by running:

    ```bash
    uv --version
    ```

3. **Homebrew** installs the native libraries PDF rendering needs (pango, cairo, gdk-pixbuf, libffi). Check it by running:

    ```bash
    brew --version
    ```

### Installation

1. Install the system dependencies (one time). On Apple Silicon use the arm64 Homebrew:

    ```bash
    arch -arm64 brew install pango cairo gdk-pixbuf libffi
    ```

2. Install the Python dependencies:

    ```bash
    uv sync --all-extras
    ```

3. Register the Jupyter kernel (it matches the kernel the templates target):

    ```bash
    uv run python -m ipykernel install --user --name mlb-stats-lab --display-name "MLB Stats Lab"
    ```

4. Optionally, install the git hooks:

    ```bash
    uv run pre-commit install
    ```

5. Start working:

    ```bash
    uv run statslab new                 # guided: pick report type, subject, format
    uv run jupyter lab                  # interactive exploration
    ```

> **PDF rendering** uses WeasyPrint, which loads native pango/cairo/glib libraries.
> On Apple Silicon they must be the **arm64** builds (`/opt/homebrew`). If you see a
> `dlopen … incompatible architecture` error, your libs are the Intel (`/usr/local`)
> build — reinstall with `arch -arm64 brew install …`.

## Usage

### Common Workflows

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

### Commands

| Command | Purpose |
| --- | --- |
| `uv run statslab new` | guided notebook/PDF builder (recommended) |
| `uv run statslab list-templates` | available templates |
| `uv run statslab new-notebook <name> ... [--run]` | scaffold (and optionally execute) a notebook |
| `uv run statslab new-report <name> ...` | render a PDF directly |
| `uv run statslab flush-cache [--older-than-days N]` | clear pybaseball cache |
| `uv run jupyter lab` | start JupyterLab |

## Project Structure

```text
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

See `docs/` for full architecture / data-layer / helper / viz / template / PDF /
CLI / dev-setup / roadmap specs.

## Development

| Command | Purpose |
| --- | --- |
| `uv run jupytext --sync reports/templates/notebooks/<name>.py` | pair `.py` ⇄ `.ipynb` |
| `uv run ruff check src/ tests/` / `ruff format src/ tests/` | lint / format |
| `uv run mypy src/` | type check |
| `uv run lint-imports` | enforce module dependency direction |
| `uv run pre-commit run --all-files` | run all hooks |

## Testing

Run the offline test suite:

```bash
uv run pytest -m "not network"
```

## Contributing

Bug reports, ideas and pull requests are welcome through [Issues](../../issues). This is a personal project I work on in my spare time, so replies can be slow and not every suggestion will make it in. For anything bigger than a small fix, open an issue first so we can talk it through.

## License

Released under the [MIT License](LICENSE).
