"""Rolling-window metric line plot."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from mlb_stats_lab.viz.theme import NEUTRAL_PRIMARY


def rolling_metric_line(
    series_or_df: pd.Series | pd.DataFrame,
    *,
    metric: str | None = None,
    title: str | None = None,
    league_average: float | None = None,
    figsize: tuple[float, float] = (10, 4),
) -> Figure:
    """Rolling-window trend line. Accepts a Series or DataFrame + metric column."""
    fig, ax = plt.subplots(figsize=figsize)
    if series_or_df is None or len(series_or_df) == 0:
        ax.set_title(title or "Rolling Metric — no data")
        return fig
    if isinstance(series_or_df, pd.DataFrame):
        if not metric:
            ax.set_title(title or "Rolling Metric — no metric specified")
            return fig
        if metric not in series_or_df.columns:
            ax.set_title(title or f"Rolling Metric — column {metric!r} not found")
            return fig
        s = series_or_df[metric]
    else:
        s = series_or_df

    ax.plot(s.index, s.values, color=NEUTRAL_PRIMARY, linewidth=1.6)
    if league_average is not None:
        ax.axhline(
            league_average,
            color="#888",
            linestyle="--",
            linewidth=1,
            label=f"MLB avg ({league_average:.3f})",
        )
        ax.legend(fontsize=8)
    ax.set_xlabel(str(s.index.name or ""))
    ax.set_ylabel(metric or s.name or "")
    ax.set_title(title or f"Rolling {metric or s.name or ''}".strip())
    return fig
