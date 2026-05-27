"""Auto-bullet helpers — text takeaways pulled from helper outputs."""

from __future__ import annotations

from typing import Any

import pandas as pd


def _get(d: Any, key: str, default: float = 0.0) -> float:
    v = d.get(key, default) if isinstance(d, (pd.Series, dict)) else default
    try:
        return float(v)
    except Exception:
        return default


def batter_bullets(line: Any, discipline: Any, contact: Any) -> list[str]:
    """Build auto-takeaway bullets for a Batter Profile."""
    bullets: list[str] = []

    pa = _get(line, "PA")
    if pa < 30:
        bullets.append(f"→ Small sample: only {int(pa)} PA so far.")

    woba = _get(line, "wOBA")
    if woba >= 0.380:
        bullets.append(f"→ wOBA {woba:.3f} — elite production tier.")
    elif woba >= 0.340:
        bullets.append(f"→ wOBA {woba:.3f} — above-average bat.")
    elif woba <= 0.290 and pa >= 30:
        bullets.append(f"→ wOBA {woba:.3f} — below-average production.")

    iso = _get(line, "ISO")
    if iso >= 0.220:
        bullets.append(f"→ ISO {iso:.3f} — top-tier power.")

    bb = _get(line, "BB%")
    k = _get(line, "K%")
    if bb >= 0.12:
        bullets.append(f"→ BB% {bb:.1%} — strong plate patience.")
    if k >= 0.28:
        bullets.append(f"→ K% {k:.1%} — strikeouts are a problem.")

    chase = _get(discipline, "Chase%")
    if chase >= 0.32:
        bullets.append(f"→ Chase% {chase:.1%} — vulnerable to breakers off the plate.")
    whiff = _get(discipline, "Whiff%")
    if whiff >= 0.30:
        bullets.append(f"→ Whiff% {whiff:.1%} — swing-and-miss prone.")

    barrel = _get(contact, "Barrel%")
    hardhit = _get(contact, "HardHit%")
    if barrel >= 0.10:
        bullets.append(f"→ Barrel% {barrel:.1%} — premium contact quality.")
    if hardhit >= 0.45:
        bullets.append(f"→ HardHit% {hardhit:.1%} — punishes mistakes.")

    return bullets or ["→ No standout traits detected at this sample size."]


def pitcher_bullets(line: Any, arsenal_df: pd.DataFrame, command: Any) -> list[str]:
    """Build auto-takeaway bullets for a Pitcher Profile."""
    bullets: list[str] = []
    bf = _get(line, "BF")
    if bf < 50:
        bullets.append(f"→ Small sample: only {int(bf)} BF so far.")

    k_minus_bb = _get(line, "K-BB%")
    if k_minus_bb >= 0.19:
        bullets.append(f"→ K-BB% {k_minus_bb:.1%} — top-quartile dominance.")
    elif k_minus_bb <= 0.05 and bf >= 50:
        bullets.append(f"→ K-BB% {k_minus_bb:.1%} — weak control / stuff combination.")

    hr9 = _get(line, "HR/9")
    if hr9 >= 1.5:
        bullets.append(f"→ HR/9 {hr9:.2f} — vulnerable to power.")

    whip = _get(line, "WHIP")
    if whip <= 1.0 and bf >= 50:
        bullets.append(f"→ WHIP {whip:.2f} — limits traffic on the bases.")

    if not arsenal_df.empty:
        primary = arsenal_df.iloc[0]
        bullets.append(
            f"→ Primary pitch: {primary.name} ({primary['Usage%']:.0%}, {primary['Avg Velo']:.1f} mph)."
        )

    fps = _get(command, "First-Pitch Strike%")
    if fps >= 0.62:
        bullets.append(f"→ First-Pitch Strike% {fps:.1%} — works ahead consistently.")
    elif fps <= 0.55 and bf >= 50:
        bullets.append(f"→ First-Pitch Strike% {fps:.1%} — falls behind too often.")

    return bullets or ["→ No standout traits detected at this sample size."]


def team_bullets(line: Any, staff_line: Any) -> list[str]:
    """Bullets for a Team Season Snapshot."""
    bullets: list[str] = []
    woba = _get(line, "wOBA")
    if woba >= 0.330:
        bullets.append(f"→ Offense wOBA {woba:.3f} — above-average bats.")
    elif woba <= 0.300:
        bullets.append(f"→ Offense wOBA {woba:.3f} — struggling to produce.")

    k_pct = _get(staff_line, "K%")
    if k_pct >= 0.25:
        bullets.append(f"→ Staff K% {k_pct:.1%} — high strikeout pitching.")
    hr9 = _get(staff_line, "HR/9")
    if hr9 >= 1.4:
        bullets.append(f"→ Staff HR/9 {hr9:.2f} — vulnerable to power.")

    return bullets or ["→ Run the notebook for richer takeaways."]
