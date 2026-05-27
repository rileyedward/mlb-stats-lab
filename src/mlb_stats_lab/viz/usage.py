"""Pitcher pitch-usage bar / pie."""

from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from mlb_stats_lab.viz.theme import pitch_color


def pitch_usage_bar(
    df: pd.DataFrame,
    *,
    by: Literal["overall", "vs_hand", "count_state"] = "overall",
    title: str | None = None,
    figsize: tuple[float, float] = (6, 4),
) -> Figure:
    """Horizontal bar chart of pitch usage."""
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty or "pitch_type" not in df.columns:
        ax.set_title(title or "Pitch Usage — no data")
        return fig
    d = df.dropna(subset=["pitch_type"])
    if d.empty:
        ax.set_title(title or "Pitch Usage — no data")
        return fig

    if by == "overall":
        counts = d["pitch_type"].value_counts()
        usage = counts / counts.sum()
        ax.barh(
            usage.index[::-1], usage.values[::-1], color=[pitch_color(p) for p in usage.index[::-1]]
        )
        for y, (_pt, u) in enumerate(zip(usage.index[::-1], usage.values[::-1])):
            ax.text(u + 0.005, y, f"{u:.0%}", va="center", fontsize=8)
        ax.set_xlim(0, max(usage.max() * 1.15, 0.05))
        ax.set_xlabel("Usage")
    elif by == "vs_hand":
        for i, hand in enumerate(["L", "R"]):
            sub = d[d["stand"] == hand]
            if sub.empty:
                continue
            counts = sub["pitch_type"].value_counts(normalize=True)
            offset = i * 0.4 - 0.2
            ys = [j + offset for j in range(len(counts))]
            ax.barh(
                ys,
                counts.values,
                height=0.35,
                color=[pitch_color(p) for p in counts.index],
                label=f"vs {hand}HB",
                alpha=0.75 if i else 1.0,
            )
            for y_pos, (_pt, u) in zip(ys, counts.items()):
                ax.text(u + 0.005, y_pos, f"{u:.0%}", va="center", fontsize=7)
        ax.set_yticks(range(len(counts)))
        ax.set_yticklabels(counts.index)
        ax.set_xlabel("Usage")
        ax.legend(fontsize=8)
    elif by == "count_state":
        ahead = d["balls"] > d["strikes"]
        behind = d["balls"] < d["strikes"]
        buckets = {"Ahead": d[ahead], "Even": d[~ahead & ~behind], "Behind": d[behind]}
        idx = pd.Index(d["pitch_type"].value_counts().head(6).index, name="pitch_type")
        bar_w = 0.25
        for i, (label, sub) in enumerate(buckets.items()):
            if sub.empty:
                continue
            counts = sub["pitch_type"].value_counts(normalize=True).reindex(idx).fillna(0)
            ys = [j + i * bar_w - bar_w for j in range(len(idx))]
            ax.barh(
                ys,
                counts.values,
                height=bar_w,
                color=[pitch_color(p) for p in idx],
                alpha=1 - i * 0.25,
                label=label,
            )
        ax.set_yticks(range(len(idx)))
        ax.set_yticklabels(idx)
        ax.set_xlabel("Usage")
        ax.legend(fontsize=8)
    ax.set_title(title or "Pitch Usage")
    return fig


def pitch_usage_pie(
    df: pd.DataFrame,
    *,
    title: str | None = None,
    figsize: tuple[float, float] = (5, 5),
) -> Figure:
    """Donut chart of overall pitch usage."""
    fig, ax = plt.subplots(figsize=figsize)
    if df is None or df.empty or "pitch_type" not in df.columns:
        ax.set_title(title or "Pitch Usage — no data")
        return fig
    counts = df["pitch_type"].dropna().value_counts()
    if counts.empty:
        ax.set_title(title or "Pitch Usage — no data")
        return fig
    colors = [pitch_color(p) for p in counts.index]
    ax.pie(
        counts.values,
        labels=counts.index,
        colors=colors,
        autopct="%1.0f%%",
        wedgeprops={"width": 0.4, "edgecolor": "white"},
        textprops={"fontsize": 9},
    )
    ax.set_title(title or "Pitch Usage")
    return fig
