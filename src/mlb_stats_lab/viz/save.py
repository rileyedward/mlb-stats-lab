"""Save matplotlib Figures to disk or in-memory bytes."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def fig_to_png(fig: Figure, path: str | Path, dpi: int = 200) -> Path:
    """Save ``fig`` as PNG. Closes the figure. Returns the path."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(p, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return p


def fig_to_svg(fig: Figure, path: str | Path) -> Path:
    """Save ``fig`` as SVG. Closes the figure."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(p, format="svg", bbox_inches="tight")
    plt.close(fig)
    return p


def fig_to_bytes(fig: Figure, fmt: Literal["png", "svg"] = "png", dpi: int = 200) -> bytes:
    """Render ``fig`` to in-memory bytes. Closes the figure."""
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()
