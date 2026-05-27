"""Spray chart — batted balls on the field, colored by outcome."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from mlb_stats_lab.viz.field import _draw_field_overlay
from mlb_stats_lab.viz.theme import outcome_color, team_color


def _transform(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    x = df["hc_x"].to_numpy() - 125.0
    y = 200.0 - df["hc_y"].to_numpy()
    # Scale to feet (Statcast hit-chart is roughly 250 px = ~500 ft span).
    return x * 2.5, y * 2.5


def spray_chart(
    df: pd.DataFrame,
    *,
    title: str | None = None,
    show_outs: bool = True,
    team_color_abbrev: str | None = None,
    figsize: tuple[float, float] = (7, 7),
) -> Figure:
    """Spray chart of batted balls. Marker color encodes outcome."""
    fig, ax = plt.subplots(figsize=figsize)
    _draw_field_overlay(ax)

    if df is None or df.empty or "hc_x" not in df.columns or "hc_y" not in df.columns:
        ax.set_title(title or "Spray Chart — no data")
        return fig

    in_play = df[(df["type"] == "X")].dropna(subset=["hc_x", "hc_y"])
    if not show_outs and "events" in in_play.columns:
        keep_events = {"single", "double", "triple", "home_run", "walk", "hit_by_pitch"}
        in_play = in_play[in_play["events"].isin(keep_events)]

    if in_play.empty:
        ax.set_title(title or "Spray Chart — no in-play data")
        return fig

    xs, ys = _transform(in_play)
    speeds = in_play["launch_speed"].fillna(0).clip(30, 150)
    sizes = ((speeds - 30) / 120 * 70 + 18).to_numpy()

    seen: dict[str, int] = {}
    for x, y, ev, sz in zip(xs, ys, in_play["events"].fillna("field_out"), sizes):
        ax.scatter(
            x, y, c=outcome_color(str(ev)), s=sz, alpha=0.75, edgecolors="white", linewidths=0.4
        )
        seen[str(ev)] = seen.get(str(ev), 0) + 1

    handles = [
        plt.Line2D(
            [],
            [],
            marker="o",
            linestyle="",
            markerfacecolor=outcome_color(ev),
            markeredgecolor="white",
            markersize=7,
            label=f"{ev} ({n})",
        )
        for ev, n in sorted(seen.items(), key=lambda kv: -kv[1])
    ]
    if handles:
        ax.legend(
            handles=handles,
            loc="lower center",
            ncols=min(4, len(handles)),
            fontsize=8,
            bbox_to_anchor=(0.5, -0.02),
        )

    accent = team_color(team_color_abbrev) if team_color_abbrev else None
    ax.set_title(title or "Spray Chart", color=accent or "#222")
    return fig
