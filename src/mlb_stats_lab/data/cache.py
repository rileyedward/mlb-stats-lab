"""Pybaseball cache enable / disable / flush."""

from __future__ import annotations

from pathlib import Path

_enabled: bool = False


def enable_default() -> None:
    """Call ``pybaseball.cache.enable()`` (idempotent)."""
    global _enabled
    if _enabled:
        return
    try:
        from pybaseball import cache  # type: ignore[import-untyped]

        cache.enable()
        _enabled = True
    except Exception:
        # Pybaseball missing or broken cache — silently skip; downstream calls
        # will surface a clearer error if the lib itself is unavailable.
        pass


def disable() -> None:
    """Disable pybaseball's cache. Useful in tests or to force fresh fetches."""
    global _enabled
    try:
        from pybaseball import cache

        cache.disable()
    except Exception:
        pass
    _enabled = False


def flush(older_than_days: int | None = None) -> int:
    """Remove pybaseball cache files. Returns count of files removed.

    Args:
        older_than_days: if provided, only remove files older than this. Pass 0
            to flush everything.
    """
    cache_dir = Path.home() / ".pybaseball" / "cache"
    if not cache_dir.exists():
        return 0
    import time

    now = time.time()
    removed = 0
    for p in cache_dir.iterdir():
        if not p.is_file():
            continue
        if older_than_days is not None and older_than_days > 0:
            age_days = (now - p.stat().st_mtime) / 86400
            if age_days < older_than_days:
                continue
        try:
            p.unlink()
            removed += 1
        except OSError:
            continue
    return removed
