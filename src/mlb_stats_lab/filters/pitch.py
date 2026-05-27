"""Pitch-type / zone-based filters."""

from __future__ import annotations

import pandas as pd

FASTBALLS = ("FF", "SI", "FC", "FS")
BREAKING = ("SL", "ST", "SV", "CU", "KC")
OFFSPEED = ("CH", "FS", "FO", "KN")

ZONE_X = 0.83
HEART_X = 0.25
SZ_TOP_DEFAULT = 3.5
SZ_BOT_DEFAULT = 1.5


def by_pitch_type(df: pd.DataFrame, *pitch_types: str) -> pd.DataFrame:
    """Filter to one or more pitch-type codes."""
    if df.empty or not pitch_types:
        return df
    return df[df["pitch_type"].isin(pitch_types)]


def fastballs(df: pd.DataFrame) -> pd.DataFrame:
    """FF, SI, FC, FS."""
    return by_pitch_type(df, *FASTBALLS)


def breaking_balls(df: pd.DataFrame) -> pd.DataFrame:
    """SL, ST, SV, CU, KC."""
    return by_pitch_type(df, *BREAKING)


def offspeed(df: pd.DataFrame) -> pd.DataFrame:
    """CH, FS, FO, KN."""
    return by_pitch_type(df, *OFFSPEED)


def by_zone(df: pd.DataFrame, *zones: int) -> pd.DataFrame:
    """Statcast zones 1–9 (in zone) or 11–14 (chase). Multiple via varargs."""
    if df.empty or not zones:
        return df
    return df[df["zone"].isin(zones)]


def in_zone(df: pd.DataFrame) -> pd.DataFrame:
    """Statcast zones 1–9."""
    if df.empty:
        return df
    return df[df["zone"].between(1, 9, inclusive="both")]


def out_of_zone(df: pd.DataFrame) -> pd.DataFrame:
    """Statcast chase zones 11–14."""
    if df.empty:
        return df
    return df[df["zone"].between(11, 14, inclusive="both")]


def _sz(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    top = (
        df["sz_top"].fillna(SZ_TOP_DEFAULT)
        if "sz_top" in df.columns
        else pd.Series(SZ_TOP_DEFAULT, index=df.index)
    )
    bot = (
        df["sz_bot"].fillna(SZ_BOT_DEFAULT)
        if "sz_bot" in df.columns
        else pd.Series(SZ_BOT_DEFAULT, index=df.index)
    )
    return top, bot


def edge_pitches(df: pd.DataFrame) -> pd.DataFrame:
    """Approximate edge of strike zone (between ``HEART_X`` and ``ZONE_X``)."""
    if df.empty:
        return df
    abs_x = df["plate_x"].abs()
    top, bot = _sz(df)
    near_edge_x = (abs_x >= HEART_X) & (abs_x <= ZONE_X)
    near_edge_z = (df["plate_z"].between(bot - 0.2, bot + 0.3)) | (
        df["plate_z"].between(top - 0.3, top + 0.2)
    )
    return df[near_edge_x | near_edge_z]


def heart_pitches(df: pd.DataFrame) -> pd.DataFrame:
    """Middle third of the strike zone."""
    if df.empty:
        return df
    abs_x = df["plate_x"].abs()
    top, bot = _sz(df)
    mid = (top + bot) / 2
    half_height = (top - bot) / 6
    in_x = abs_x <= HEART_X
    in_z = df["plate_z"].between(mid - half_height, mid + half_height)
    return df[in_x & in_z]
