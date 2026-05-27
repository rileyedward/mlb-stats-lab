"""``statslab new-report`` subcommands — build context + render PDF."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import typer

from mlb_stats_lab.cli import _output as out
from mlb_stats_lab.cli.registry import get as get_spec
from mlb_stats_lab.data import normalize_team
from mlb_stats_lab.reports.engine import render_report

app = typer.Typer(no_args_is_help=True, help="Render a PDF report directly.")


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_") or "unknown"


def _today() -> str:
    return date.today().isoformat()


def _default_out(template: str, slug_parts: list[str]) -> str:
    slug = "_".join(filter(None, slug_parts))
    return f"{template.replace('-', '_')}__{slug}__{_today()}.pdf"


def _run(template: str, args: dict[str, Any], slug_parts: list[str], out_path: str | None) -> Path:
    spec = get_spec(template)
    out.step("Building context (may fetch from pybaseball)...")
    ctx = spec.builder(args)
    target = out_path or _default_out(template, slug_parts)
    out.step(f"Rendering {template}...")
    path = render_report(template, ctx, target)
    out.success(f"Wrote {path}")
    return path


@app.command("batter-profile")
def batter_profile(
    player: str = typer.Option(..., "--player"),
    season: int | None = typer.Option(None, "--season"),
    start: str | None = typer.Option(None, "--start"),
    end: str | None = typer.Option(None, "--end"),
    recent_form_pas: int = typer.Option(25, "--recent-form-pas"),
    out_path: str | None = typer.Option(None, "--out", help="Override output path"),
) -> None:
    _run(
        "batter-profile",
        {
            "player": player,
            "season": season,
            "start_date": start,
            "end_date": end,
            "recent_form_pas": recent_form_pas,
        },
        [_slug(player)],
        out_path,
    )


@app.command("pitcher-profile")
def pitcher_profile(
    player: str = typer.Option(..., "--player"),
    season: int | None = typer.Option(None, "--season"),
    start: str | None = typer.Option(None, "--start"),
    end: str | None = typer.Option(None, "--end"),
    recent_form_starts: int = typer.Option(5, "--recent-form-starts"),
    out_path: str | None = typer.Option(None, "--out"),
) -> None:
    _run(
        "pitcher-profile",
        {
            "player": player,
            "season": season,
            "start_date": start,
            "end_date": end,
            "recent_form_starts": recent_form_starts,
        },
        [_slug(player)],
        out_path,
    )


@app.command("team-season-snapshot")
def team_season_snapshot(
    team: str = typer.Option(..., "--team"),
    season: int | None = typer.Option(None, "--season"),
    start: str | None = typer.Option(None, "--start"),
    end: str | None = typer.Option(None, "--end"),
    out_path: str | None = typer.Option(None, "--out"),
) -> None:
    t = normalize_team(team)
    _run(
        "team-season-snapshot",
        {"team": t, "season": season, "start_date": start, "end_date": end},
        [t],
        out_path,
    )


@app.command("series-matchup")
def series_matchup(
    team_a: str = typer.Option(..., "--team-a"),
    team_b: str = typer.Option(..., "--team-b"),
    season: int | None = typer.Option(None, "--season"),
    start: str | None = typer.Option(None, "--start"),
    end: str | None = typer.Option(None, "--end"),
    out_path: str | None = typer.Option(None, "--out"),
) -> None:
    a = normalize_team(team_a)
    b = normalize_team(team_b)
    _run(
        "series-matchup",
        {"team_a": a, "team_b": b, "season": season, "start_date": start, "end_date": end},
        [a, "vs", b],
        out_path,
    )
