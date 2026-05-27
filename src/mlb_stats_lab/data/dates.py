"""Season-aware date helpers."""

from __future__ import annotations

import calendar
import os
from datetime import date, timedelta

OPENING_DAYS: dict[int, date] = {
    2021: date(2021, 4, 1),
    2022: date(2022, 4, 7),
    2023: date(2023, 3, 30),
    2024: date(2024, 3, 28),
    2025: date(2025, 3, 27),
    2026: date(2026, 3, 26),
    2027: date(2027, 4, 1),
}

REG_SEASON_END: dict[int, date] = {
    2021: date(2021, 10, 3),
    2022: date(2022, 10, 5),
    2023: date(2023, 10, 1),
    2024: date(2024, 9, 29),
    2025: date(2025, 9, 28),
    2026: date(2026, 9, 27),
}


def _last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    d = date(year, month, last_day)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def opening_day(year: int) -> date:
    """Regular-season opening day for the given year.

    Looks up the hardcoded table; falls back to the last Thursday of March.
    """
    if year in OPENING_DAYS:
        return OPENING_DAYS[year]
    return _last_weekday_of_month(year, 3, calendar.THURSDAY)


def regular_season_end(year: int) -> date:
    """Approximate regular-season end date for ``year``."""
    if year in REG_SEASON_END:
        return REG_SEASON_END[year]
    # Heuristic: last Sunday of September.
    return _last_weekday_of_month(year, 9, calendar.SUNDAY)


def _env_year() -> int | None:
    raw = os.environ.get("STATSLAB_SEASON")
    return int(raw) if raw else None


def current_season() -> int:
    """Current MLB season per env / config / auto-detect rule."""
    env = _env_year()
    if env is not None:
        return env
    from mlb_stats_lab.config import get_config

    cfg = get_config()
    if cfg.default_year is not None:
        return cfg.default_year
    today = date.today()
    return today.year if today >= opening_day(today.year) else today.year - 1


def current_season_range() -> tuple[date, date]:
    """``(opening_day(current_season), today)``."""
    year = current_season()
    return (opening_day(year), date.today())


def season_range(year: int) -> tuple[date, date]:
    """``(opening_day(year), regular_season_end(year))`` — clamped to today if in progress."""
    od = opening_day(year)
    end = regular_season_end(year)
    today = date.today()
    if today < end:
        end = today
    if today < od:
        end = od
    return (od, end)


def last_n_days(n: int, anchor: date | None = None) -> tuple[date, date]:
    """``(anchor - n + 1, anchor)``. Anchor defaults to today."""
    anchor = anchor or date.today()
    start = anchor - timedelta(days=max(n - 1, 0))
    return (start, anchor)


def parse_date(value: date | str | None) -> date | None:
    """Coerce ``date`` / ISO string / ``None`` to a date or ``None``."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))
