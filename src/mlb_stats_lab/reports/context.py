"""Per-template context dataclasses and ``build_*_context`` functions.

Each builder fetches data, runs helpers, builds figures, and returns a context
dict suitable for both the matching Jinja PDF template and the matching
notebook template.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import pandas as pd

from mlb_stats_lab.batting import (
    batting_line,
    contact_quality,
    performance_by_pitch_type,
    plate_discipline,
    rolling_batting_line,
)
from mlb_stats_lab.batting.splits import splits as batting_splits
from mlb_stats_lab.data import (
    current_season,
    get_standings,
    get_statcast_batter,
    get_statcast_for_team,
    get_statcast_pitcher,
    normalize_team,
    season_range,
    team_schedule,
)
from mlb_stats_lab.pitching import (
    arsenal_summary,
    command_metrics,
    pitching_line,
    results_by_pitch,
    rolling_pitching_line,
)
from mlb_stats_lab.pitching.splits import splits as pitching_splits
from mlb_stats_lab.reports.assets import figs_to_context
from mlb_stats_lab.reports.summary import (
    batter_bullets,
    pitcher_bullets,
    team_bullets,
)
from mlb_stats_lab.viz import (
    ev_la_scatter,
    pitch_movement_chart,
    pitch_usage_bar,
    pitch_usage_pie,
    rolling_metric_line,
    splits_bar_chart,
    spray_chart,
    velocity_distribution,
    zone_grid,
    zone_heatmap,
)


def _to_record(series: pd.Series) -> dict[str, Any]:
    return {str(k): (float(v) if isinstance(v, (int, float)) else v) for k, v in series.items()}


def _date_range(
    season: int | None, start: date | str | None, end: date | str | None
) -> tuple[int, date, date]:
    yr = season or current_season()
    s_default, e_default = season_range(yr)
    s = pd.to_datetime(start).date() if start else s_default
    e = pd.to_datetime(end).date() if end else e_default
    return yr, s, e


def _detect_team(df: pd.DataFrame, perspective: str) -> str | None:
    """Find the most-frequent team for the subject player in ``df``.

    perspective="batter" → team of the row where the player batted
    (bottom-of-inning → home team batting, top → away team batting).
    """
    if df.empty:
        return None
    is_top = df["inning_topbot"].astype(str).str.lower().str.startswith("top")
    if perspective == "batter":
        teams = df["home_team"].where(~is_top, df["away_team"])
    else:
        teams = df["home_team"].where(is_top, df["away_team"])
    counts = teams.value_counts()
    return str(counts.index[0]) if not counts.empty else None


# ---------------------------------------------------------------------------
# Batter Profile
# ---------------------------------------------------------------------------


@dataclass
class BatterProfileContext:
    report_title: str
    report_subtitle: str
    generated_at: str
    team: str
    player: str
    line: dict[str, Any]
    discipline: dict[str, Any]
    contact: dict[str, Any]
    by_pitch: list[dict[str, Any]]
    figs: dict[str, str]
    takeaways: list[str]


def build_batter_profile_context(args: dict[str, Any]) -> BatterProfileContext:
    player = str(args["player"])
    season = args.get("season")
    yr, start, end = _date_range(season, args.get("start_date"), args.get("end_date"))

    df = get_statcast_batter(player, start=start, end=end)
    line = batting_line(df)
    disc = plate_discipline(df)
    contact = contact_quality(df)
    by_pitch_df = performance_by_pitch_type(df)
    rolling = rolling_batting_line(df, window=int(args.get("recent_form_pas", 25)))

    team = _detect_team(df, "batter") or "—"

    figs = figs_to_context(
        spray=spray_chart(
            df, team_color_abbrev=team if team != "—" else None, title=f"{player} — Batted Balls"
        ),
        zone_density=zone_heatmap(df, metric="density", title="Pitches Seen"),
        zone_swing=zone_heatmap(df, metric="swing_rate", title="Swing Rate"),
        zone_xwoba=zone_grid(df, metric="xwoba", bins=3, title="xwOBA by Zone"),
        ev_la=ev_la_scatter(df, title="EV vs LA"),
        splits_hand=splits_bar_chart(
            batting_splits(df, axis="vs_hand"), metric="wOBA", title="vs Handedness"
        ),
        splits_home_away=splits_bar_chart(
            batting_splits(df, axis="home_away"), metric="wOBA", title="Home / Away"
        ),
        splits_month=splits_bar_chart(
            batting_splits(df, axis="month"), metric="wOBA", title="By Month"
        ),
        rolling_woba=rolling_metric_line(
            rolling, metric="wOBA", league_average=0.320, title="Rolling wOBA"
        ),
    )

    takeaways = batter_bullets(line, disc, contact)

    by_pitch = (
        [
            {"pitch_type": idx, **{str(k): float(v) for k, v in row.items()}}
            for idx, row in by_pitch_df.iterrows()
        ]
        if not by_pitch_df.empty
        else []
    )

    return BatterProfileContext(
        report_title=f"Batter Profile — {player}",
        report_subtitle=f"{yr} Season · {start.isoformat()} → {end.isoformat()}",
        generated_at=datetime.now().isoformat(timespec="seconds"),
        team=team,
        player=player,
        line=_to_record(line),
        discipline=_to_record(disc),
        contact=_to_record(contact),
        by_pitch=by_pitch,
        figs=figs,
        takeaways=takeaways,
    )


# ---------------------------------------------------------------------------
# Pitcher Profile
# ---------------------------------------------------------------------------


@dataclass
class PitcherProfileContext:
    report_title: str
    report_subtitle: str
    generated_at: str
    team: str
    player: str
    line: dict[str, Any]
    command: dict[str, Any]
    arsenal: list[dict[str, Any]]
    results: list[dict[str, Any]]
    figs: dict[str, str]
    takeaways: list[str]


def build_pitcher_profile_context(args: dict[str, Any]) -> PitcherProfileContext:
    player = str(args["player"])
    season = args.get("season")
    yr, start, end = _date_range(season, args.get("start_date"), args.get("end_date"))

    df = get_statcast_pitcher(player, start=start, end=end)
    line = pitching_line(df)
    arsenal = arsenal_summary(df)
    cmd = command_metrics(df)
    results = results_by_pitch(df)
    rolling = rolling_pitching_line(
        df, window=int(args.get("recent_form_starts", 5)), over="starts"
    )

    team = _detect_team(df, "pitcher") or "—"

    figs = figs_to_context(
        movement=pitch_movement_chart(df, title=f"{player} — Arsenal Movement"),
        velocity=velocity_distribution(df, kind="violin", title="Velocity Distribution"),
        usage_pie=pitch_usage_pie(df, title="Pitch Mix"),
        usage_hand=pitch_usage_bar(df, by="vs_hand", title="Usage vs Hand"),
        zone_density=zone_heatmap(
            df, perspective="pitcher", metric="density", title="Pitch Locations"
        ),
        zone_whiff=zone_grid(
            df, perspective="pitcher", metric="whiff_rate", title="Whiff% by Zone"
        ),
        splits_hand=splits_bar_chart(
            pitching_splits(df, axis="vs_hand"), metric="K-BB%", title="K-BB% vs Hand"
        ),
        splits_innings=splits_bar_chart(
            pitching_splits(df, axis="innings"), metric="K-BB%", title="K-BB% by Innings"
        ),
        rolling_k=rolling_metric_line(
            rolling, metric="K%", league_average=0.225, title="Rolling K%"
        ),
    )

    takeaways = pitcher_bullets(line, arsenal, cmd)

    return PitcherProfileContext(
        report_title=f"Pitcher Profile — {player}",
        report_subtitle=f"{yr} Season · {start.isoformat()} → {end.isoformat()}",
        generated_at=datetime.now().isoformat(timespec="seconds"),
        team=team,
        player=player,
        line=_to_record(line),
        command=_to_record(cmd),
        arsenal=[
            {"pitch_type": idx, **{str(k): float(v) for k, v in row.items()}}
            for idx, row in arsenal.iterrows()
        ],
        results=[
            {"pitch_type": idx, **{str(k): float(v) for k, v in row.items()}}
            for idx, row in results.iterrows()
        ],
        figs=figs,
        takeaways=takeaways,
    )


# ---------------------------------------------------------------------------
# Team Season Snapshot
# ---------------------------------------------------------------------------


@dataclass
class TeamSnapshotContext:
    report_title: str
    report_subtitle: str
    generated_at: str
    team: str
    record: dict[str, Any]
    offense: dict[str, Any]
    pitching: dict[str, Any]
    figs: dict[str, str]
    takeaways: list[str]


def build_team_snapshot_context(args: dict[str, Any]) -> TeamSnapshotContext:
    team = normalize_team(str(args["team"]))
    season = args.get("season")
    yr, start, end = _date_range(season, args.get("start_date"), args.get("end_date"))

    schedule = team_schedule(team, year=yr)
    standings = get_standings(yr)
    bat_df = get_statcast_for_team(team, start=start, end=end, side="batting")
    pit_df = get_statcast_for_team(team, start=start, end=end, side="pitching")

    off_line = batting_line(bat_df)
    staff_line = pitching_line(pit_df)
    off_contact = contact_quality(bat_df)
    off_disc = plate_discipline(bat_df)

    record = {"team": team, "season": yr}
    if not schedule.empty:
        w = int((schedule.get("W/L", pd.Series(dtype=str)).astype(str).str.startswith("W")).sum())
        l = int((schedule.get("W/L", pd.Series(dtype=str)).astype(str).str.startswith("L")).sum())
        record["W"] = w
        record["L"] = l
        record["games"] = len(schedule)

    figs = figs_to_context(
        offense_hand=splits_bar_chart(
            batting_splits(bat_df, axis="vs_hand"), metric="wOBA", title="Offense vs Hand"
        ),
        offense_month=splits_bar_chart(
            batting_splits(bat_df, axis="month"), metric="wOBA", title="Offense by Month"
        ),
        offense_ev_la=ev_la_scatter(
            bat_df.sample(min(len(bat_df), 1500), random_state=0) if not bat_df.empty else bat_df,
            title="Team EV / LA",
        ),
        staff_usage=pitch_usage_bar(pit_df, title="Staff Usage"),
        staff_velocity=velocity_distribution(pit_df, kind="box", title="Staff Velocity"),
    )

    takeaways = team_bullets(off_line, staff_line)

    return TeamSnapshotContext(
        report_title=f"Team Snapshot — {team}",
        report_subtitle=f"{yr} Season · {start.isoformat()} → {end.isoformat()}",
        generated_at=datetime.now().isoformat(timespec="seconds"),
        team=team,
        record=record,
        offense={
            "line": _to_record(off_line),
            "discipline": _to_record(off_disc),
            "contact": _to_record(off_contact),
        },
        pitching={"line": _to_record(staff_line)},
        figs=figs,
        takeaways=takeaways,
    )


# ---------------------------------------------------------------------------
# Series Matchup
# ---------------------------------------------------------------------------


@dataclass
class SeriesMatchupContext:
    report_title: str
    report_subtitle: str
    generated_at: str
    team_a: str
    team_b: str
    team_a_offense: dict[str, Any]
    team_b_offense: dict[str, Any]
    team_a_pitching: dict[str, Any]
    team_b_pitching: dict[str, Any]
    figs: dict[str, str]
    takeaways: list[str]


def build_series_matchup_context(args: dict[str, Any]) -> SeriesMatchupContext:
    team_a = normalize_team(str(args["team_a"]))
    team_b = normalize_team(str(args["team_b"]))
    season = args.get("season")
    yr, start, end = _date_range(season, args.get("start_date"), args.get("end_date"))

    a_bat = get_statcast_for_team(team_a, start=start, end=end, side="batting")
    a_pit = get_statcast_for_team(team_a, start=start, end=end, side="pitching")
    b_bat = get_statcast_for_team(team_b, start=start, end=end, side="batting")
    b_pit = get_statcast_for_team(team_b, start=start, end=end, side="pitching")

    a_off_line = batting_line(a_bat)
    a_staff_line = pitching_line(a_pit)
    b_off_line = batting_line(b_bat)
    b_staff_line = pitching_line(b_pit)

    figs = figs_to_context(
        a_offense_hand=splits_bar_chart(
            batting_splits(a_bat, axis="vs_hand"), metric="wOBA", title=f"{team_a} vs Hand"
        ),
        b_offense_hand=splits_bar_chart(
            batting_splits(b_bat, axis="vs_hand"), metric="wOBA", title=f"{team_b} vs Hand"
        ),
        a_staff_usage=pitch_usage_bar(a_pit, title=f"{team_a} Staff Usage"),
        b_staff_usage=pitch_usage_bar(b_pit, title=f"{team_b} Staff Usage"),
        a_velocity=velocity_distribution(a_pit, kind="kde", title=f"{team_a} Velo"),
        b_velocity=velocity_distribution(b_pit, kind="kde", title=f"{team_b} Velo"),
    )

    take = [
        f"→ {team_a} wOBA {a_off_line.get('wOBA', 0):.3f} vs {team_b} wOBA {b_off_line.get('wOBA', 0):.3f}.",
        f"→ {team_a} staff xwOBA-against {a_staff_line.get('xwOBA-against', 0):.3f} vs {team_b} staff xwOBA-against {b_staff_line.get('xwOBA-against', 0):.3f}.",
    ]

    return SeriesMatchupContext(
        report_title=f"Series Matchup — {team_a} vs {team_b}",
        report_subtitle=f"{yr} Season · {start.isoformat()} → {end.isoformat()}",
        generated_at=datetime.now().isoformat(timespec="seconds"),
        team_a=team_a,
        team_b=team_b,
        team_a_offense=_to_record(a_off_line),
        team_b_offense=_to_record(b_off_line),
        team_a_pitching=_to_record(a_staff_line),
        team_b_pitching=_to_record(b_staff_line),
        figs=figs,
        takeaways=take,
    )
