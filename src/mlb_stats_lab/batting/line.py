"""``batting_line`` — comprehensive slash-line + advanced metrics for a hitter."""

from __future__ import annotations

import numpy as np
import pandas as pd

# wOBA weights — fall-back when ``woba_value`` / ``woba_denom`` not present.
# Per Fangraphs guts table (rough, year-agnostic).
_WOBA_WEIGHTS: dict[str, float] = {
    "walk": 0.69,
    "hit_by_pitch": 0.72,
    "single": 0.88,
    "double": 1.25,
    "triple": 1.58,
    "home_run": 2.02,
}

_HIT_EVENTS = {"single", "double", "triple", "home_run"}
_BB_EVENTS = {"walk"}
_IBB_EVENTS = {"intent_walk"}
_HBP_EVENTS = {"hit_by_pitch"}
_SO_EVENTS = {"strikeout", "strikeout_double_play"}
_SF_EVENTS = {"sac_fly", "sac_fly_double_play"}
_SH_EVENTS = {"sac_bunt", "sac_bunt_double_play"}


def _safe_div(num: float, den: float) -> float:
    return float(num) / float(den) if den else 0.0


def batting_line(df: pd.DataFrame) -> pd.Series:
    """Comprehensive hitter line as a Series.

    Reads Statcast columns ``events``, ``description``, ``estimated_woba_using_speedangle``,
    ``estimated_ba_using_speedangle``, ``woba_value`` (optional), ``woba_denom`` (optional).
    """
    if df is None or df.empty or "events" not in df.columns:
        return _empty_line()

    pa_df = df[df["events"].notna()]
    events = pa_df["events"].astype(str)

    h_1b = int((events == "single").sum())
    h_2b = int((events == "double").sum())
    h_3b = int((events == "triple").sum())
    hr = int((events == "home_run").sum())
    h = h_1b + h_2b + h_3b + hr
    bb = int(events.isin(_BB_EVENTS | _IBB_EVENTS).sum())
    ibb = int(events.isin(_IBB_EVENTS).sum())
    hbp = int(events.isin(_HBP_EVENTS).sum())
    so = int(events.isin(_SO_EVENTS).sum())
    sf = int(events.isin(_SF_EVENTS).sum())
    sh = int(events.isin(_SH_EVENTS).sum())

    pa = len(pa_df)
    ab = pa - bb - hbp - sf - sh
    ab = max(ab, 0)

    tb = h_1b + 2 * h_2b + 3 * h_3b + 4 * hr
    avg = _safe_div(h, ab)
    obp = _safe_div(h + bb + hbp, ab + bb + hbp + sf)
    slg = _safe_div(tb, ab)
    ops = obp + slg
    iso = slg - avg

    bb_pct = _safe_div(bb, pa)
    k_pct = _safe_div(so, pa)
    bb_k = _safe_div(bb, so)

    # wOBA: prefer Statcast woba_value/woba_denom if present.
    woba_val = pa_df["woba_value"] if "woba_value" in pa_df.columns else None
    woba_den = pa_df["woba_denom"] if "woba_denom" in pa_df.columns else None
    if woba_val is not None and woba_den is not None and woba_den.fillna(0).sum() > 0:
        woba = float(woba_val.fillna(0).sum()) / float(woba_den.fillna(0).sum())
    else:
        weighted = sum(_WOBA_WEIGHTS.get(ev, 0.0) for ev in events)
        denom = ab + bb - ibb + sf + hbp
        woba = _safe_div(weighted, denom)

    in_play = df[df["type"] == "X"] if "type" in df else pd.DataFrame()
    xwoba = (
        float(in_play["estimated_woba_using_speedangle"].dropna().mean())
        if "estimated_woba_using_speedangle" in in_play
        else float("nan")
    )
    xba = (
        float(in_play["estimated_ba_using_speedangle"].dropna().mean())
        if "estimated_ba_using_speedangle" in in_play
        else float("nan")
    )

    data = {
        "PA": pa,
        "AB": ab,
        "H": h,
        "1B": h_1b,
        "2B": h_2b,
        "3B": h_3b,
        "HR": hr,
        "BB": bb,
        "IBB": ibb,
        "HBP": hbp,
        "SO": so,
        "SF": sf,
        "SH": sh,
        "TB": tb,
        "AVG": avg,
        "OBP": obp,
        "SLG": slg,
        "OPS": ops,
        "ISO": iso,
        "BB%": bb_pct,
        "K%": k_pct,
        "BB/K": bb_k,
        "wOBA": float(woba),
        "xwOBA": xwoba if not np.isnan(xwoba) else 0.0,
        "xBA": xba if not np.isnan(xba) else 0.0,
    }
    return pd.Series(data, name="batting_line")


def _empty_line() -> pd.Series:
    keys = [
        "PA",
        "AB",
        "H",
        "1B",
        "2B",
        "3B",
        "HR",
        "BB",
        "IBB",
        "HBP",
        "SO",
        "SF",
        "SH",
        "TB",
        "AVG",
        "OBP",
        "SLG",
        "OPS",
        "ISO",
        "BB%",
        "K%",
        "BB/K",
        "wOBA",
        "xwOBA",
        "xBA",
    ]
    return pd.Series({k: 0 for k in keys}, name="batting_line")
