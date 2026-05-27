"""Pitch-location + EV/LA scatter charts."""

from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.patches import Polygon

from mlb_stats_lab.viz.theme import outcome_color, pitch_color
from mlb_stats_lab.viz.zone import _draw_zone_overlay

Perspective = Literal["batter", "pitcher"]
ColorBy = Literal["pitch_type", "description", "result"]


def pitch_location_scatter(
    df: pd.DataFrame,
    *,
    color_by: ColorBy = "pitch_type",
    perspective: Perspective = "batter",
    title: str | None = None,
    figsize: tuple[float, float] = (5, 6),
) -> Figure:
    """Pitches plotted in the zone, colored by ``color_by``."""
    fig, ax = plt.subplots(figsize=figsize)
    _draw_zone_overlay(ax)

    if df is None or df.empty:
        ax.set_title(title or "Pitch Locations — no data")
        return fig
    d = df.dropna(subset=["plate_x", "plate_z"]).copy()
    if perspective == "batter":
        sign = d.get("stand", pd.Series("R", index=d.index)).map({"L": -1, "R": 1}).fillna(1)
        d["plate_x"] = d["plate_x"] * sign

    if color_by == "pitch_type":
        colors = d["pitch_type"].map(pitch_color)
        key_series = d["pitch_type"].fillna("UNK")
    elif color_by == "result":
        colors = d.get("events", pd.Series("field_out", index=d.index)).map(outcome_color)
        key_series = d.get("events", pd.Series("field_out", index=d.index)).fillna("field_out")
    else:
        colors = d.get("description", pd.Series("", index=d.index)).map(
            lambda v: (
                outcome_color(v) if v in outcome_color.__globals__["OUTCOME_COLORS"] else "#888"
            )
        )
        key_series = d.get("description", pd.Series("", index=d.index)).fillna("")

    ax.scatter(
        d["plate_x"],
        d["plate_z"],
        c=list(colors),
        s=30,
        alpha=0.7,
        edgecolors="white",
        linewidths=0.3,
    )

    counts = key_series.value_counts()
    handles = [
        plt.Line2D(
            [],
            [],
            marker="o",
            linestyle="",
            markerfacecolor=pitch_color(k) if color_by == "pitch_type" else outcome_color(k),
            markeredgecolor="white",
            markersize=7,
            label=f"{k} ({v})",
        )
        for k, v in counts.head(10).items()
    ]
    if handles:
        ax.legend(
            handles=handles,
            loc="lower center",
            ncols=min(4, len(handles)),
            fontsize=8,
            bbox_to_anchor=(0.5, -0.05),
        )
    ax.set_title(title or "Pitch Locations")
    return fig


def ev_la_scatter(
    df: pd.DataFrame,
    *,
    overlay_barrel_zone: bool = True,
    color_by: Literal["outcome", "bb_type", "none"] = "outcome",
    title: str | None = None,
    figsize: tuple[float, float] = (7, 5),
) -> Figure:
    """Exit-velocity vs launch-angle scatter for batted balls."""
    fig, ax = plt.subplots(figsize=figsize)

    if df is None or df.empty:
        ax.set_title(title or "EV vs LA — no data")
        return fig
    in_play = (
        df[df["type"] == "X"].dropna(subset=["launch_speed", "launch_angle"])
        if "type" in df
        else df.dropna(subset=["launch_speed", "launch_angle"])
    )
    if in_play.empty:
        ax.set_title(title or "EV vs LA — no data")
        return fig

    if overlay_barrel_zone:
        # Approximate barrel zone (EV >= 98, LA roughly 8°-50° with tighter bounds at lower EV).
        verts = np.array(
            [
                [98, 26],
                [98, 30],
                [105, 22],
                [115, 16],
                [120, 12],
                [120, 50],
                [105, 50],
                [98, 30],
            ]
        )
        ax.add_patch(Polygon(verts[:, [1, 0]], closed=True, alpha=0.10, color="#d62728"))

    if color_by == "outcome":
        colors = in_play.get("events", pd.Series("field_out", index=in_play.index)).map(
            outcome_color
        )
    elif color_by == "bb_type":
        palette = {
            "ground_ball": "#1f77b4",
            "fly_ball": "#ff7f0e",
            "line_drive": "#2ca02c",
            "popup": "#7f7f7f",
        }
        colors = in_play.get("bb_type", pd.Series("", index=in_play.index)).map(
            lambda v: palette.get(str(v), "#bbb")
        )
    else:
        colors = pd.Series("#1f77b4", index=in_play.index)

    ax.scatter(
        in_play["launch_angle"],
        in_play["launch_speed"],
        c=list(colors),
        s=24,
        alpha=0.7,
        edgecolors="white",
        linewidths=0.3,
    )
    ax.set_xlabel("Launch Angle (°)")
    ax.set_ylabel("Exit Velocity (mph)")
    ax.set_xlim(-30, 60)
    ax.set_ylim(40, 125)
    ax.set_title(title or "EV vs Launch Angle")
    return fig
