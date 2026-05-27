"""Chart-embedding helpers for the report pipeline."""

from __future__ import annotations

import base64
from typing import Literal

from matplotlib.figure import Figure

from mlb_stats_lab.viz.save import fig_to_bytes


def fig_to_data_uri(fig: Figure, fmt: Literal["png", "svg"] = "png", dpi: int = 200) -> str:
    """Render ``fig`` to a base64 data URI for direct ``<img src>`` embedding."""
    raw = fig_to_bytes(fig, fmt=fmt, dpi=dpi)
    b64 = base64.b64encode(raw).decode("ascii")
    mime = "image/svg+xml" if fmt == "svg" else "image/png"
    return f"data:{mime};base64,{b64}"


def figs_to_context(**figs: Figure | None) -> dict[str, str]:
    """Bulk: ``{name: figure}`` → ``{name: data_uri}``. ``None`` figures omitted."""
    out: dict[str, str] = {}
    for name, fig in figs.items():
        if fig is None:
            continue
        out[name] = fig_to_data_uri(fig)
    return out
