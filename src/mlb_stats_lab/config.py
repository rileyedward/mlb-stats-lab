"""Project configuration — loads ``statslab.toml`` and applies env overrides.

The repo root is auto-detected by walking up from this file until a directory
containing ``statslab.toml`` (or ``pyproject.toml``) is found.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "statslab.toml").exists() or (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


REPO_ROOT: Path = _find_repo_root()
CONFIG_PATH: Path = REPO_ROOT / "statslab.toml"


@dataclass(frozen=True)
class Paths:
    notebooks_dir: Path
    generated_dir: Path
    reports_dir: Path
    templates_dir: Path
    output_dir: Path
    pdf_templates_dir: Path
    notebook_templates_dir: Path


@dataclass(frozen=True)
class Config:
    paths: Paths
    default_year: int | None
    cache_enabled: bool
    raw: dict[str, Any] = field(default_factory=dict)


def _load_raw() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


def _resolve(rel: str) -> Path:
    p = Path(rel)
    return p if p.is_absolute() else (REPO_ROOT / p).resolve()


@lru_cache(maxsize=1)
def get_config() -> Config:
    raw = _load_raw()
    paths_raw = raw.get("paths", {})
    season_raw = raw.get("season", {})
    pyb_raw = raw.get("pybaseball", {})

    notebooks_dir = _resolve(
        os.environ.get("STATSLAB_NOTEBOOKS_DIR", paths_raw.get("notebooks_dir", "notebooks"))
    )
    generated_dir = _resolve(
        os.environ.get(
            "STATSLAB_GENERATED_DIR",
            paths_raw.get("generated_dir", str(notebooks_dir / "generated")),
        )
    )
    reports_dir = _resolve(paths_raw.get("reports_dir", "reports"))
    templates_dir = _resolve(paths_raw.get("templates_dir", "reports/templates"))
    output_dir = _resolve(
        os.environ.get("STATSLAB_OUTPUT_DIR", paths_raw.get("output_dir", "reports/output"))
    )

    paths = Paths(
        notebooks_dir=notebooks_dir,
        generated_dir=generated_dir,
        reports_dir=reports_dir,
        templates_dir=templates_dir,
        output_dir=output_dir,
        pdf_templates_dir=templates_dir / "pdf",
        notebook_templates_dir=templates_dir / "notebooks",
    )

    env_year = os.environ.get("STATSLAB_SEASON")
    if env_year:
        default_year: int | None = int(env_year)
    else:
        cfg_year = season_raw.get("default_year")
        default_year = int(cfg_year) if cfg_year else None

    cache_enabled = bool(pyb_raw.get("cache_enabled", True))

    return Config(
        paths=paths,
        default_year=default_year,
        cache_enabled=cache_enabled,
        raw=raw,
    )


def verbose() -> bool:
    return bool(os.environ.get("STATSLAB_VERBOSE"))
