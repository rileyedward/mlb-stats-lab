"""Pitcher arsenal — movement chart and velocity distributions."""

from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from mlb_stats_lab.viz.theme import pitch_color


def pitch_movement_chart(
    df: pd.DataFrame,
    *,
    title: str | None = None,
    figsize: tuple[float, float] = (7, 6),
) -> Figure:
    """H vs V movement scatter, colored by ``pitch_type``."""
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty:
        ax.set_title(title or "Pitch Movement — no data")
        return fig
    d = df.dropna(subset=["pfx_x", "pfx_z"]).copy()
    # Convert ft → inches and flip horizontal so positive = arm side for RHP.
    d["h"] = d["pfx_x"] * -12.0
    d["v"] = d["pfx_z"] * 12.0
    for pt, sub in d.groupby("pitch_type"):
        ax.scatter(sub["h"], sub["v"], s=18, alpha=0.6, color=pitch_color(pt), label=str(pt))
        cx, cy = sub["h"].mean(), sub["v"].mean()
        velo = sub.get("release_speed", pd.Series(dtype=float)).dropna()
        label = f"{pt} {velo.mean():.1f} mph" if not velo.empty else str(pt)
        ax.text(cx, cy, label, ha="center", va="center", fontsize=8, color="#222")
    ax.axhline(0, color="#bbb", linewidth=0.6)
    ax.axvline(0, color="#bbb", linewidth=0.6)
    ax.set_xlabel("Horizontal Break (in)")
    ax.set_ylabel("Vertical Break (in)")
    ax.set_aspect("equal")
    ax.set_title(title or "Arsenal — Movement")
    return fig


def velocity_distribution(
    df: pd.DataFrame,
    *,
    kind: Literal["kde", "violin", "box"] = "kde",
    title: str | None = None,
    figsize: tuple[float, float] = (8, 4),
) -> Figure:
    """Velocity distribution per pitch type."""
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty or "release_speed" not in df.columns:
        ax.set_title(title or "Velocity Distribution — no data")
        return fig
    d = df.dropna(subset=["release_speed", "pitch_type"]).copy()
    if d.empty:
        ax.set_title(title or "Velocity Distribution — no data")
        return fig

    pt_order = list(d["pitch_type"].value_counts().index)
    palette = {pt: pitch_color(pt) for pt in pt_order}

    if kind == "kde":
        for pt in pt_order:
            sns.kdeplot(
                d[d["pitch_type"] == pt]["release_speed"],
                ax=ax,
                color=palette[pt],
                label=pt,
                fill=True,
                alpha=0.25,
            )
        ax.legend(fontsize=8, ncols=min(4, len(pt_order)))
    elif kind == "violin":
        sns.violinplot(
            data=d,
            x="pitch_type",
            y="release_speed",
            order=pt_order,
            palette=palette,
            ax=ax,
            inner="quartile",
            cut=0,
        )
    else:
        sns.boxplot(
            data=d, x="pitch_type", y="release_speed", order=pt_order, palette=palette, ax=ax
        )
    ax.set_xlabel("")
    ax.set_ylabel("Velocity (mph)")
    ax.set_title(title or "Velocity Distribution")
    return fig
