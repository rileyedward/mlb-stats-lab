"""Strike-zone heatmaps (KDE + binned grid)."""

from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from mlb_stats_lab.viz.zone import (
    ZONE_BOT_DEFAULT,
    ZONE_HALF_WIDTH,
    ZONE_TOP_DEFAULT,
    _draw_zone_overlay,
)

Metric = Literal["density", "whiff_rate", "swing_rate", "xwoba", "count", "avg"]
Perspective = Literal["batter", "pitcher"]

_SWING_DESC = (
    "swinging_strike",
    "swinging_strike_blocked",
    "foul",
    "foul_tip",
    "hit_into_play",
    "missed_bunt",
)
_WHIFF_DESC = ("swinging_strike", "swinging_strike_blocked", "missed_bunt")


def _flip(df: pd.DataFrame, perspective: Perspective) -> pd.DataFrame:
    if perspective == "batter":
        # Batter perspective: flip plate_x so positive = inside (handedness-dependent).
        out = df.copy()
        sign = out.get("stand", pd.Series("R", index=out.index)).map({"L": -1, "R": 1}).fillna(1)
        out["plate_x"] = out["plate_x"] * sign
        return out
    return df


def zone_heatmap(
    df: pd.DataFrame,
    *,
    metric: Metric = "density",
    perspective: Perspective = "batter",
    title: str | None = None,
    figsize: tuple[float, float] = (5, 6),
) -> Figure:
    """KDE-style heatmap of pitch locations or metric values around the zone."""
    fig, ax = plt.subplots(figsize=figsize)
    _draw_zone_overlay(ax)

    if df is None or df.empty or "plate_x" not in df.columns or "plate_z" not in df.columns:
        ax.set_title(title or "Zone Heatmap — no data")
        return fig

    d = _flip(df.dropna(subset=["plate_x", "plate_z"]), perspective)

    if metric == "density":
        try:
            sns.kdeplot(
                x=d["plate_x"],
                y=d["plate_z"],
                ax=ax,
                fill=True,
                cmap="viridis",
                levels=10,
                alpha=0.6,
            )
        except Exception:
            ax.scatter(d["plate_x"], d["plate_z"], alpha=0.4, s=10)
    else:
        # Binned heatmap of metric over a coarse grid.
        if metric == "whiff_rate":
            d = d.assign(_m=d["description"].isin(_WHIFF_DESC).astype(float))
            denom_mask = d["description"].isin(_SWING_DESC)
            d = d[denom_mask]
        elif metric == "swing_rate":
            d = d.assign(_m=d["description"].isin(_SWING_DESC).astype(float))
        elif metric == "xwoba":
            d = d.assign(_m=d["estimated_woba_using_speedangle"].fillna(0.0))
        else:
            d = d.assign(_m=1.0)

        if d.empty:
            ax.set_title(title or "Zone Heatmap — no data")
            return fig
        x_bins = np.linspace(-1.5, 1.5, 13)
        z_bins = np.linspace(0.8, 4.2, 13)
        stat, *_ = np.histogram2d(
            d["plate_x"], d["plate_z"], bins=[x_bins, z_bins], weights=d["_m"]
        )
        counts, *_ = np.histogram2d(d["plate_x"], d["plate_z"], bins=[x_bins, z_bins])
        with np.errstate(invalid="ignore", divide="ignore"):
            arr = np.where(counts > 0, stat / np.where(counts == 0, 1, counts), np.nan)
        if metric == "count":
            arr = stat
        ax.imshow(
            arr.T,
            origin="lower",
            extent=(-1.5, 1.5, 0.8, 4.2),
            cmap="RdYlBu_r",
            aspect="auto",
            alpha=0.85,
        )
        _draw_zone_overlay(ax)

    ax.set_title(title or f"Zone {metric.replace('_', ' ').title()}")
    return fig


def zone_grid(
    df: pd.DataFrame,
    *,
    metric: Metric = "count",
    bins: Literal[3, 5] = 3,
    perspective: Perspective = "batter",
    title: str | None = None,
    figsize: tuple[float, float] = (5, 6),
) -> Figure:
    """Discrete bin grid with metric value labels."""
    fig, ax = plt.subplots(figsize=figsize)

    if df is None or df.empty or "plate_x" not in df.columns:
        _draw_zone_overlay(ax)
        ax.set_title(title or "Zone Grid — no data")
        return fig

    d = _flip(df.dropna(subset=["plate_x", "plate_z"]), perspective)

    n = bins
    x_edges = np.linspace(-ZONE_HALF_WIDTH, ZONE_HALF_WIDTH, n + 1)
    z_edges = np.linspace(ZONE_BOT_DEFAULT, ZONE_TOP_DEFAULT, n + 1)

    counts, *_ = np.histogram2d(d["plate_x"], d["plate_z"], bins=[x_edges, z_edges])

    if metric == "count":
        vals = counts
        fmt = "{:.0f}"
    elif metric == "whiff_rate":
        whiff = d["description"].isin(_WHIFF_DESC).astype(float)
        swing_mask = d["description"].isin(_SWING_DESC)
        d2 = d[swing_mask]
        if d2.empty:
            vals = np.zeros_like(counts)
        else:
            w_counts, *_ = np.histogram2d(d2["plate_x"], d2["plate_z"], bins=[x_edges, z_edges])
            w_whiff, *_ = np.histogram2d(
                d2["plate_x"], d2["plate_z"], bins=[x_edges, z_edges], weights=whiff.loc[d2.index]
            )
            with np.errstate(invalid="ignore", divide="ignore"):
                vals = np.where(w_counts > 0, w_whiff / w_counts, 0.0)
        fmt = "{:.0%}"
    elif metric == "swing_rate":
        sw = d["description"].isin(_SWING_DESC).astype(float)
        s_counts, *_ = np.histogram2d(d["plate_x"], d["plate_z"], bins=[x_edges, z_edges])
        sw_counts, *_ = np.histogram2d(
            d["plate_x"], d["plate_z"], bins=[x_edges, z_edges], weights=sw
        )
        with np.errstate(invalid="ignore", divide="ignore"):
            vals = np.where(s_counts > 0, sw_counts / s_counts, 0.0)
        fmt = "{:.0%}"
    elif metric == "xwoba":
        xw = d["estimated_woba_using_speedangle"].fillna(0.0)
        sums, *_ = np.histogram2d(d["plate_x"], d["plate_z"], bins=[x_edges, z_edges], weights=xw)
        with np.errstate(invalid="ignore", divide="ignore"):
            vals = np.where(counts > 0, sums / counts, 0.0)
        fmt = "{:.3f}"
    else:
        vals = counts
        fmt = "{:.0f}"

    im = ax.imshow(
        vals.T,
        origin="lower",
        extent=(-ZONE_HALF_WIDTH, ZONE_HALF_WIDTH, ZONE_BOT_DEFAULT, ZONE_TOP_DEFAULT),
        cmap="RdYlBu_r",
        aspect="auto",
    )
    for i, xc in enumerate((x_edges[:-1] + x_edges[1:]) / 2):
        for j, zc in enumerate((z_edges[:-1] + z_edges[1:]) / 2):
            v = vals[i, j]
            ax.text(xc, zc, fmt.format(v), ha="center", va="center", fontsize=8, color="#222")
    _draw_zone_overlay(ax)
    fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
    ax.set_title(title or f"Zone {metric.replace('_', ' ').title()}")
    return fig
