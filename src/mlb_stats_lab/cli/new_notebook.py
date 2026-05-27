"""``statslab new-notebook`` subcommands."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import nbformat
import typer

from mlb_stats_lab.cli import _output as out
from mlb_stats_lab.cli.registry import get as get_spec
from mlb_stats_lab.config import get_config
from mlb_stats_lab.data import normalize_team

app = typer.Typer(no_args_is_help=True, help="Scaffold a parameterized notebook from a template.")


def _slug(value: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return s or "unknown"


def _today() -> str:
    return date.today().isoformat()


def _format_param(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, (int, float)):
        return repr(value)
    return repr(str(value))


def _rewrite_parameters(nb_path: Path, params: dict[str, Any]) -> nbformat.NotebookNode:
    nb = nbformat.read(str(nb_path), as_version=4)
    rewrote = False
    for cell in nb.cells:
        tags = cell.get("metadata", {}).get("tags", []) or []
        if "parameters" in tags:
            lines = ["# parameters"]
            for k, v in params.items():
                lines.append(f"{k} = {_format_param(v)}")
            cell["source"] = "\n".join(lines) + "\n"
            rewrote = True
            break
    if not rewrote:
        raise RuntimeError(f"No 'parameters' cell found in {nb_path}")
    return nb


def _write(nb: nbformat.NotebookNode, out_dir: Path, filename: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    with path.open("w") as f:
        nbformat.write(nb, f)
    return path


def _emit(template: str, params: dict[str, Any], slug_parts: list[str]) -> Path:
    cfg = get_config()
    spec = get_spec(template)
    nb_path = spec.notebook_path
    if not nb_path.exists():
        raise FileNotFoundError(f"Notebook template missing: {nb_path}")
    nb = _rewrite_parameters(nb_path, params)
    slug = "_".join(filter(None, slug_parts))
    name = f"{template.replace('-', '_')}__{slug}__{_today()}.ipynb"
    path = _write(nb, cfg.paths.reports_dir, name)
    out.success(f"Generated {path}")
    out.info(f"Open with: uv run jupyter lab {path}")
    return path


@app.command("batter-profile")
def batter_profile(
    player: str = typer.Option(..., "--player", help="Hitter display name"),
    season: int | None = typer.Option(None, "--season"),
    start: str | None = typer.Option(None, "--start"),
    end: str | None = typer.Option(None, "--end"),
    recent_form_pas: int = typer.Option(25, "--recent-form-pas"),
) -> None:
    """Scaffold a batter-profile notebook."""
    _emit(
        "batter-profile",
        {
            "player": player,
            "season": season,
            "start_date": start,
            "end_date": end,
            "recent_form_pas": recent_form_pas,
        },
        [_slug(player)],
    )


@app.command("pitcher-profile")
def pitcher_profile(
    player: str = typer.Option(..., "--player", help="Pitcher display name"),
    season: int | None = typer.Option(None, "--season"),
    start: str | None = typer.Option(None, "--start"),
    end: str | None = typer.Option(None, "--end"),
    recent_form_starts: int = typer.Option(5, "--recent-form-starts"),
) -> None:
    """Scaffold a pitcher-profile notebook."""
    _emit(
        "pitcher-profile",
        {
            "player": player,
            "season": season,
            "start_date": start,
            "end_date": end,
            "recent_form_starts": recent_form_starts,
        },
        [_slug(player)],
    )


@app.command("team-season-snapshot")
def team_season_snapshot(
    team: str = typer.Option(..., "--team", help="Team abbreviation"),
    season: int | None = typer.Option(None, "--season"),
    start: str | None = typer.Option(None, "--start"),
    end: str | None = typer.Option(None, "--end"),
    recent_window_games: int = typer.Option(15, "--recent-window-games"),
) -> None:
    """Scaffold a team-season-snapshot notebook."""
    team_n = normalize_team(team)
    _emit(
        "team-season-snapshot",
        {
            "team": team_n,
            "season": season,
            "start_date": start,
            "end_date": end,
            "recent_window_games": recent_window_games,
        },
        [team_n],
    )


@app.command("series-matchup")
def series_matchup(
    team_a: str = typer.Option(..., "--team-a"),
    team_b: str = typer.Option(..., "--team-b"),
    season: int | None = typer.Option(None, "--season"),
    start: str | None = typer.Option(None, "--start"),
    end: str | None = typer.Option(None, "--end"),
    recent_form_games: int = typer.Option(10, "--recent-form-games"),
) -> None:
    """Scaffold a series-matchup notebook."""
    a = normalize_team(team_a)
    b = normalize_team(team_b)
    _emit(
        "series-matchup",
        {
            "team_a": a,
            "team_b": b,
            "season": season,
            "start_date": start,
            "end_date": end,
            "recent_form_games": recent_form_games,
        },
        [a, "vs", b],
    )
