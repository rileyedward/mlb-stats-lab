"""Single-metric distribution helpers (EV, LA, velocity)."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from mlb_stats_lab.viz.theme import NEUTRAL_PRIMARY, pitch_color


def _hist(
    df: pd.DataFrame,
    col: str,
    by: str | None,
    title: str,
    xlabel: str,
    figsize: tuple[float, float],
) -> Figure:
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty or col not in df.columns:
        ax.set_title(f"{title} — no data")
        return fig
    d = df.dropna(subset=[col])
    if d.empty:
        ax.set_title(f"{title} — no data")
        return fig
    if by and by in d.columns:
        for key, sub in d.groupby(by):
            sns.kdeplot(sub[col], ax=ax, label=str(key), fill=True, alpha=0.25)
        ax.legend(fontsize=8)
    else:
        sns.histplot(d[col], ax=ax, kde=True, color=NEUTRAL_PRIMARY, bins=24)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    return fig


def ev_distribution(
    df: pd.DataFrame,
    *,
    by: str | None = None,
    title: str | None = None,
    figsize: tuple[float, float] = (8, 5),
) -> Figure:
    return _hist(df, "launch_speed", by, title or "Exit Velocity", "mph", figsize)


def la_distribution(
    df: pd.DataFrame,
    *,
    by: str | None = None,
    title: str | None = None,
    figsize: tuple[float, float] = (8, 5),
) -> Figure:
    return _hist(df, "launch_angle", by, title or "Launch Angle", "°", figsize)


def velocity_box(
    df: pd.DataFrame,
    *,
    by: str = "pitch_type",
    title: str | None = None,
    figsize: tuple[float, float] = (8, 5),
) -> Figure:
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty or "release_speed" not in df.columns:
        ax.set_title(title or "Velocity — no data")
        return fig
    d = df.dropna(subset=["release_speed", by])
    if d.empty:
        ax.set_title(title or "Velocity — no data")
        return fig
    order = list(d[by].value_counts().index)
    palette = {pt: pitch_color(pt) for pt in order} if by == "pitch_type" else None
    sns.boxplot(data=d, x=by, y="release_speed", order=order, palette=palette, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("Velocity (mph)")
    ax.set_title(title or "Velocity")
    return fig
