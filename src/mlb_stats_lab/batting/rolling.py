"""Rolling batting line over recent PAs or games."""

from __future__ import annotations

from typing import Literal

import pandas as pd

from mlb_stats_lab.batting.line import batting_line


def rolling_batting_line(
    df: pd.DataFrame,
    window: int = 25,
    over: Literal["PA", "games"] = "PA",
) -> pd.DataFrame:
    """Rolling-window slash line anchored at each PA (or game).

    Returns a DataFrame with one row per anchor and ``batting_line`` columns.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.sort_values(["game_date", "at_bat_number", "pitch_number"], na_position="last")

    if over == "PA":
        pa_df = df[df["events"].notna()].reset_index(drop=True)
        rows: list[pd.Series] = []
        labels: list[int] = []
        for end in range(window, len(pa_df) + 1):
            window_pa = pa_df.iloc[end - window : end]
            ids = set(zip(window_pa["game_pk"], window_pa["at_bat_number"]))
            mask = df.apply(lambda r: (r["game_pk"], r["at_bat_number"]) in ids, axis=1)
            rows.append(batting_line(df[mask]))
            labels.append(end)
        if not rows:
            return pd.DataFrame()
        out = pd.DataFrame(rows, index=labels)
        out.index.name = "PA #"
        return out

    # over == "games"
    games = list(df["game_pk"].drop_duplicates())
    rows = []
    labels_g: list[str] = []
    for i in range(window, len(games) + 1):
        window_games = games[i - window : i]
        rows.append(batting_line(df[df["game_pk"].isin(window_games)]))
        labels_g.append(str(games[i - 1]))
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows, index=labels_g)
    out.index.name = "game_pk"
    return out
