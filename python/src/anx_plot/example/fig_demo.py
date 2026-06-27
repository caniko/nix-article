"""Example figure module demonstrating the anx_plot framework protocol.

Downstream projects should follow this pattern:
1. Define a ``figures.toml`` registry
2. Create a layout spec in ``figures/layouts/``
3. Implement ``export_panels()`` that returns a mapping of panel letters
   to drawing functions
4. Run ``anx layout solve`` followed by ``anx figure panels``
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from anx_plot.palette import BLUE, GREEN, GREY_LIGHT, ORANGE, RED
from anx_plot.standard import finish_axes

PANEL_LETTERS = ["A", "B", "C"]


def _draw_panel_a(ax: plt.Axes) -> None:
    """Demo panel: simple line plot."""
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    ax.plot(x, y1, color=BLUE, label="sin")
    ax.plot(x, y2, color=RED, label="cos")
    finish_axes(ax, x_label="x", y_label="y", legend=True)


def _draw_panel_b(ax: plt.Axes) -> None:
    """Demo panel: bar chart."""
    categories = ["A", "B", "C", "D", "E"]
    values = [3, 7, 2, 9, 5]
    colors = [BLUE, GREEN, RED, ORANGE, BLUE]
    ax.bar(categories, values, color=colors, edgecolor="white", linewidth=0.5)
    finish_axes(ax, x_label="Category", y_label="Value", grid_axis="y")


def _draw_panel_c(ax: plt.Axes) -> None:
    """Demo panel: scatter plot."""
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 50)
    y = rng.normal(0, 1, 50)
    ax.scatter(x, y, color=GREEN, alpha=0.7, edgecolors="white", linewidth=0.3)
    ax.axhline(0, color=GREY_LIGHT, linewidth=0.5)
    ax.axvline(0, color=GREY_LIGHT, linewidth=0.5)
    finish_axes(ax, x_label="X", y_label="Y", grid_axis="both")


def export_panels(
    output_dir: Path,
    prefix: str = "CF",
    **kwargs,
) -> list[Path]:
    """Export demo figure panels using the anx_plot framework.

    This is the canonical entry point that anx expects from figure modules.
    """
    from anx_plot.layout import export_panels as _export

    panel_fns = {
        "A": _draw_panel_a,
        "B": _draw_panel_b,
        "C": _draw_panel_c,
    }
    return _export(panel_fns, output_dir, prefix=prefix)
