"""Synthetic Statcast-like DataFrame for offline tests."""

from __future__ import annotations

import numpy as np
import pandas as pd


def make_batter_df(seed: int = 0) -> pd.DataFrame:
    """200 pitches across ~50 PAs of varied outcomes for one batter."""
    rng = np.random.default_rng(seed)
    n = 200

    descriptions = rng.choice(
        [
            "ball",
            "called_strike",
            "swinging_strike",
            "foul",
            "hit_into_play",
        ],
        size=n,
        p=[0.30, 0.18, 0.10, 0.22, 0.20],
    )
    types = np.where(
        np.isin(descriptions, ["called_strike", "swinging_strike", "foul"]),
        "S",
        np.where(descriptions == "hit_into_play", "X", "B"),
    )

    in_play_idx = np.where(types == "X")[0]
    events = np.array([None] * n, dtype=object)
    for i in in_play_idx:
        ev = rng.choice(
            ["single", "double", "triple", "home_run", "field_out", "grounded_into_double_play"],
            p=[0.18, 0.06, 0.01, 0.05, 0.60, 0.10],
        )
        events[i] = ev
    walk_idx = rng.choice(np.where(descriptions == "ball")[0], size=8, replace=False)
    for i in walk_idx:
        events[i] = "walk"
    k_idx = rng.choice(np.where(descriptions == "swinging_strike")[0], size=10, replace=False)
    for i in k_idx:
        events[i] = "strikeout"

    df = pd.DataFrame(
        {
            "game_pk": rng.integers(700000, 700050, size=n),
            "game_date": pd.to_datetime(
                rng.choice(pd.date_range("2024-04-01", "2024-09-29"), size=n)
            ).astype(str),
            "at_bat_number": np.arange(n) // 4 + 1,
            "pitch_number": np.tile([1, 2, 3, 4], n // 4),
            "batter": np.full(n, 592450),
            "pitcher": rng.integers(500000, 700000, size=n),
            "stand": np.full(n, "R"),
            "p_throws": rng.choice(["L", "R"], size=n, p=[0.3, 0.7]),
            "pitch_type": rng.choice(["FF", "SL", "CH", "CU", "SI"], size=n),
            "release_speed": rng.uniform(82, 99, size=n),
            "release_spin_rate": rng.uniform(1800, 2700, size=n),
            "pfx_x": rng.uniform(-1.5, 1.5, size=n),
            "pfx_z": rng.uniform(-1.0, 2.0, size=n),
            "plate_x": rng.uniform(-1.5, 1.5, size=n),
            "plate_z": rng.uniform(1.0, 4.0, size=n),
            "zone": rng.choice(list(range(1, 10)) + list(range(11, 15)), size=n),
            "sz_top": np.full(n, 3.4),
            "sz_bot": np.full(n, 1.6),
            "description": descriptions,
            "events": events,
            "type": types,
            "launch_speed": np.where(types == "X", rng.uniform(60, 115, size=n), np.nan),
            "launch_angle": np.where(types == "X", rng.uniform(-20, 50, size=n), np.nan),
            "hc_x": np.where(types == "X", rng.uniform(50, 200, size=n), np.nan),
            "hc_y": np.where(types == "X", rng.uniform(50, 200, size=n), np.nan),
            "bb_type": rng.choice(["ground_ball", "fly_ball", "line_drive", "popup"], size=n),
            "hit_distance_sc": rng.uniform(150, 420, size=n),
            "estimated_ba_using_speedangle": rng.uniform(0.05, 0.85, size=n),
            "estimated_woba_using_speedangle": rng.uniform(0.05, 1.2, size=n),
            "estimated_slg_using_speedangle": rng.uniform(0.05, 2.0, size=n),
            "balls": rng.integers(0, 4, size=n),
            "strikes": rng.integers(0, 3, size=n),
            "outs_when_up": rng.integers(0, 3, size=n),
            "inning": rng.integers(1, 10, size=n),
            "inning_topbot": rng.choice(["Top", "Bot"], size=n),
            "on_1b": rng.choice([np.nan, 600000], size=n),
            "on_2b": rng.choice([np.nan, 600001], size=n),
            "on_3b": rng.choice([np.nan, 600002], size=n),
            "home_team": np.full(n, "SEA"),
            "away_team": np.full(n, "LAD"),
            "bat_score": rng.integers(0, 10, size=n),
            "fld_score": rng.integers(0, 10, size=n),
            "post_bat_score": rng.integers(0, 10, size=n),
            "delta_run_exp": rng.uniform(-0.2, 0.2, size=n),
            "launch_speed_angle": rng.integers(1, 7, size=n),
            "woba_value": rng.uniform(0, 2.0, size=n),
            "woba_denom": np.where(np.array([e is not None for e in events]), 1.0, np.nan),
        }
    )
    return df


def make_pitcher_df(seed: int = 1) -> pd.DataFrame:
    df = make_batter_df(seed=seed)
    # Pitcher-perspective: subject is one pitcher.
    df = df.copy()
    df["pitcher"] = 600000
    return df
