"""Splits bar chart."""

from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from mlb_stats_lab.viz.theme import NEUTRAL_PRIMARY


def splits_bar_chart(
    splits_df: pd.DataFrame,
    metric: str,
    *,
    title: str | None = None,
    sort: Literal["index", "value"] = "index",
    figsize: tuple[float, float] = (8, 5),
) -> Figure:
    """Bar of ``metric`` across the splits-DataFrame's buckets."""
    fig, ax = plt.subplots(figsize=figsize)
    if splits_df is None or splits_df.empty or metric not in splits_df.columns:
        ax.set_title(title or f"Splits — {metric} (no data)")
        return fig
    d = splits_df.copy()
    if sort == "value":
        d = d.sort_values(metric)
    bars = ax.bar(d.index.astype(str), d[metric].astype(float), color=NEUTRAL_PRIMARY)
    sample_col = "PA" if "PA" in d.columns else ("BF" if "BF" in d.columns else None)
    for bar, label in zip(bars, d.index.astype(str)):
        h = bar.get_height()
        suffix = f" (n={int(d.loc[label, sample_col])})" if sample_col else ""
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h,
            f"{h:.3f}{suffix}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    overall = float(d[metric].mean())
    ax.axhline(overall, color="#888", linestyle="--", linewidth=0.8)
    ax.set_ylabel(metric)
    ax.set_title(title or f"Splits — {metric}")
    return fig
