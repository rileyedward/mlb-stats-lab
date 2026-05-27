"""Baseball field overlay for spray charts."""

from __future__ import annotations

import math

from matplotlib.axes import Axes
from matplotlib.patches import Arc, Polygon


def _draw_field_overlay(ax: Axes, max_dist: float = 400.0) -> None:
    """Draw foul lines, infield diamond, and outfield arc on ``ax``.

    Coordinates are in feet from home plate. Home plate is at ``(0, 0)``,
    centerfield is +y. Use after applying the Statcast spray transform.
    """
    # Foul lines: 45° from home plate.
    angle = math.radians(45)
    left_x = -math.sin(angle) * max_dist
    right_x = math.sin(angle) * max_dist
    far_y = math.cos(angle) * max_dist
    ax.plot([0, left_x], [0, far_y], color="#777", linewidth=1.0)
    ax.plot([0, right_x], [0, far_y], color="#777", linewidth=1.0)

    # Outfield arc at ~400 ft (rough).
    arc = Arc(
        (0, 0), max_dist * 2, max_dist * 2, theta1=45, theta2=135, color="#777", linewidth=1.0
    )
    ax.add_patch(arc)

    # Infield (diamond).
    base_dist = 90.0
    second = (0, base_dist * math.sqrt(2))
    first = (base_dist, base_dist)
    third = (-base_dist, base_dist)
    home = (0, 0)
    diamond = Polygon(
        [home, first, second, third], closed=True, fill=False, edgecolor="#aaa", linewidth=1.0
    )
    ax.add_patch(diamond)

    # Pitcher's mound.
    ax.plot([0], [60.5], marker="o", color="#aaa", markersize=4)
    ax.plot([0], [0], marker="s", color="#aaa", markersize=4)

    ax.set_xlim(-max_dist * 0.95, max_dist * 0.95)
    ax.set_ylim(-15, max_dist * 1.05)
    ax.set_aspect("equal")
    ax.grid(False)
    ax.spines[:].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
