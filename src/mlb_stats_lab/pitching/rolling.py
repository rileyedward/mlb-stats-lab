"""Rolling pitcher line over recent starts or batters faced."""

from __future__ import annotations

from typing import Literal

import pandas as pd

from mlb_stats_lab.pitching.line import pitching_line


def rolling_pitching_line(
    df: pd.DataFrame,
    window: int = 5,
    over: Literal["starts", "BF"] = "starts",
) -> pd.DataFrame:
    """Rolling-window pitching line over recent starts or batters faced."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.sort_values(["game_date", "at_bat_number", "pitch_number"], na_position="last")

    if over == "starts":
        games = list(df["game_pk"].drop_duplicates())
        rows: list[pd.Series] = []
        labels: list[str] = []
        for i in range(window, len(games) + 1):
            window_games = games[i - window : i]
            rows.append(pitching_line(df[df["game_pk"].isin(window_games)]))
            labels.append(str(games[i - 1]))
        if not rows:
            return pd.DataFrame()
        out = pd.DataFrame(rows, index=labels)
        out.index.name = "game_pk"
        return out

    pa_df = df[df["events"].notna()].reset_index(drop=True)
    rows = []
    labels_pa: list[int] = []
    for end in range(window, len(pa_df) + 1):
        window_pa = pa_df.iloc[end - window : end]
        ids = set(zip(window_pa["game_pk"], window_pa["at_bat_number"]))
        mask = df.apply(lambda r: (r["game_pk"], r["at_bat_number"]) in ids, axis=1)
        rows.append(pitching_line(df[mask]))
        labels_pa.append(end)
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows, index=labels_pa)
    out.index.name = "BF"
    return out
