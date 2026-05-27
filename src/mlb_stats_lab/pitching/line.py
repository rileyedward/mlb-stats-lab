"""``pitching_line`` — comprehensive pitcher line."""

from __future__ import annotations

import pandas as pd

OUT_EVENTS: dict[str, int] = {
    "field_out": 1,
    "force_out": 1,
    "grounded_into_double_play": 2,
    "double_play": 2,
    "triple_play": 3,
    "strikeout": 1,
    "strikeout_double_play": 2,
    "sac_fly": 1,
    "sac_fly_double_play": 2,
    "sac_bunt": 1,
    "sac_bunt_double_play": 2,
    "fielders_choice": 1,
    "fielders_choice_out": 1,
    "other_out": 1,
}

_HIT_EVENTS = {"single", "double", "triple", "home_run"}
_HR_EVENTS = {"home_run"}
_BB_EVENTS = {"walk", "intent_walk"}
_HBP_EVENTS = {"hit_by_pitch"}
_K_EVENTS = {"strikeout", "strikeout_double_play"}


def _safe(num: float, den: float) -> float:
    return float(num) / float(den) if den else 0.0


def pitching_line(df: pd.DataFrame) -> pd.Series:
    """Pitcher mirror of ``batting_line``."""
    if df is None or df.empty:
        return _empty_line()

    pa_df = df[df["events"].notna()]
    events = pa_df["events"].astype(str)
    bf = len(pa_df)

    outs = int(events.map(lambda e: OUT_EVENTS.get(e, 0)).sum())
    ip_thirds = outs
    ip = ip_thirds / 3.0

    hits = int(events.isin(_HIT_EVENTS).sum())
    hr = int(events.isin(_HR_EVENTS).sum())
    bb = int(events.isin(_BB_EVENTS).sum())
    hbp = int(events.isin(_HBP_EVENTS).sum())
    k = int(events.isin(_K_EVENTS).sum())

    runs = 0
    er = 0
    if "delta_run_exp" in pa_df.columns:
        # Very rough — sum of positive-for-batter delta_run_exp on completed PA pitches.
        pass
    if "post_bat_score" in pa_df.columns and "bat_score" in pa_df.columns:
        runs = int((pa_df["post_bat_score"] - pa_df["bat_score"]).clip(lower=0).sum())
        er = runs

    ab_against = bf - bb - hbp
    baa = _safe(hits, ab_against)

    woba_val = pa_df["woba_value"] if "woba_value" in pa_df.columns else None
    woba_den = pa_df["woba_denom"] if "woba_denom" in pa_df.columns else None
    if woba_val is not None and woba_den is not None and woba_den.fillna(0).sum() > 0:
        woba_against = float(woba_val.fillna(0).sum()) / float(woba_den.fillna(0).sum())
    else:
        woba_against = 0.0

    in_play = df[df["type"] == "X"] if "type" in df else pd.DataFrame()
    xwoba_against = (
        float(in_play["estimated_woba_using_speedangle"].dropna().mean())
        if "estimated_woba_using_speedangle" in in_play
        else 0.0
    )

    data = {
        "BF": bf,
        "IP": round(ip, 2),
        "H": hits,
        "R": runs,
        "ER": er,
        "BB": bb,
        "HBP": hbp,
        "K": k,
        "HR": hr,
        "K/9": _safe(9 * k, ip),
        "BB/9": _safe(9 * bb, ip),
        "K%": _safe(k, bf),
        "BB%": _safe(bb, bf),
        "K-BB%": _safe(k - bb, bf),
        "HR/9": _safe(9 * hr, ip),
        "WHIP": _safe(hits + bb, ip),
        "BAA": baa,
        "wOBA-against": woba_against,
        "xwOBA-against": xwoba_against,
    }
    return pd.Series(data, name="pitching_line")


def _empty_line() -> pd.Series:
    keys = [
        "BF",
        "IP",
        "H",
        "R",
        "ER",
        "BB",
        "HBP",
        "K",
        "HR",
        "K/9",
        "BB/9",
        "K%",
        "BB%",
        "K-BB%",
        "HR/9",
        "WHIP",
        "BAA",
        "wOBA-against",
        "xwOBA-against",
    ]
    return pd.Series({k: 0 for k in keys}, name="pitching_line")
