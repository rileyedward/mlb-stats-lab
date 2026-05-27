"""Strike zone overlay."""

from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

ZONE_HALF_WIDTH = 0.83
ZONE_TOP_DEFAULT = 3.5
ZONE_BOT_DEFAULT = 1.5


def _draw_zone_overlay(
    ax: Axes,
    sz_top: float = ZONE_TOP_DEFAULT,
    sz_bot: float = ZONE_BOT_DEFAULT,
    chase: bool = True,
) -> None:
    """Draw the strike zone rectangle (and optional dashed chase zone)."""
    zone = Rectangle(
        (-ZONE_HALF_WIDTH, sz_bot),
        ZONE_HALF_WIDTH * 2,
        sz_top - sz_bot,
        fill=False,
        edgecolor="#222",
        linewidth=1.4,
    )
    ax.add_patch(zone)
    if chase:
        chase_rect = Rectangle(
            (-ZONE_HALF_WIDTH - 0.5, sz_bot - 0.4),
            (ZONE_HALF_WIDTH + 0.5) * 2,
            (sz_top - sz_bot) + 0.8,
            fill=False,
            edgecolor="#888",
            linewidth=0.8,
            linestyle="--",
        )
        ax.add_patch(chase_rect)
    ax.set_xlim(-2, 2)
    ax.set_ylim(0.5, 4.5)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    ax.spines[:].set_visible(False)
