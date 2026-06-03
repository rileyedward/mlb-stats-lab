"""``statslab new`` — guided, interactive report builder.

The recommended entry point: walks through report type, subject, season, and
output format, then dispatches to the same code paths as the explicit
``new-notebook`` / ``new-report`` commands.
"""

from __future__ import annotations

import typer

from mlb_stats_lab.cli import _output as out
from mlb_stats_lab.cli.new_notebook import _emit, _slug
from mlb_stats_lab.cli.new_report import _run
from mlb_stats_lab.cli.registry import TEMPLATES
from mlb_stats_lab.data import normalize_team

_PLAYER_TEMPLATES = {"batter-profile", "pitcher-profile"}


def _select(prompt: str, choices: list[str], default: str | None = None) -> str:
    try:
        import questionary

        answer = questionary.select(prompt, choices=choices, default=default or choices[0]).ask()
    except Exception:
        answer = None
    if answer is None:  # questionary unavailable or cancelled — fall back
        answer = typer.prompt(f"{prompt} {choices}", default=default or choices[0])
    if answer not in choices:
        raise typer.BadParameter(f"{answer!r} is not one of {choices}")
    return answer


def _text(prompt: str, default: str | None = None) -> str:
    try:
        import questionary

        answer = questionary.text(prompt, default=default or "").ask()
    except Exception:
        answer = None
    if answer is None:
        answer = typer.prompt(prompt, default=default or "")
    return answer.strip()


def _confirm(prompt: str, default: bool = False) -> bool:
    try:
        import questionary

        answer = questionary.confirm(prompt, default=default).ask()
        if answer is not None:
            return bool(answer)
    except Exception:
        pass
    return typer.confirm(prompt, default=default)


def new() -> None:
    """Interactively build a notebook or PDF report."""
    template = _select("Report type", sorted(TEMPLATES))

    args: dict[str, object] = {}
    slug_parts: list[str]
    if template in _PLAYER_TEMPLATES:
        player = _text("Player name", default="Aaron Judge")
        args["player"] = player
        slug_parts = [_slug(player)]
    elif template == "series-matchup":
        a = normalize_team(_text("Team A (abbrev)", default="SEA"))
        b = normalize_team(_text("Team B (abbrev)", default="LAD"))
        args["team_a"], args["team_b"] = a, b
        slug_parts = [a, "vs", b]
    else:  # team-season-snapshot
        team = normalize_team(_text("Team (abbrev)", default="SEA"))
        args["team"] = team
        slug_parts = [team]

    season = _text("Season (blank = current)", default="")
    args["season"] = int(season) if season else None
    args["start_date"] = None
    args["end_date"] = None

    fmt = _select("Output format", ["notebook", "pdf"])
    if fmt == "pdf":
        _run(template, args, slug_parts, None)
    else:
        run = _confirm("Execute the notebook now? (fetches from pybaseball)", default=False)
        _emit(template, args, slug_parts, run)

    out.info("Done. Run `statslab new` again any time.")
