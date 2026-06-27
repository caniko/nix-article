"""Shared style helpers for compact manuscript line panels."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt

from anx_plot.sizing import FONT_LEGEND, FONT_SMALL

from .helpers import bottom_legend
from .palette import GREY_LIGHT
from .standard import finish_exact_panel


@dataclass(frozen=True)
class LinePanelStyle:
    """Visual defaults for dense multi-series manuscript line charts."""

    line_width: float = 1.0
    reference_line_width: float = 0.8
    marker_size: float = 2.5
    band_alpha: float = 0.10
    line_alpha: float = 0.85
    grid_alpha: float = 0.15
    tick_labelsize: float = FONT_SMALL - 1
    legend_fontsize: float = FONT_LEGEND - 1


COMPACT_LINE_STYLE = LinePanelStyle()


def compact_legend_kwargs(
    *,
    style: LinePanelStyle = COMPACT_LINE_STYLE,
    **overrides: Any,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "fontsize": style.legend_fontsize,
        "frameon": True,
        "framealpha": 1,
        "facecolor": "white",
        "edgecolor": GREY_LIGHT,
        "handlelength": 1.2,
        "handletextpad": 0.35,
        "columnspacing": 0.6,
        "borderpad": 0.25,
        "labelspacing": 0.25,
    }
    kwargs.update(overrides)
    return kwargs


def plot_series(
    ax: plt.Axes,
    x: Any,
    y: Any,
    *,
    color: str,
    label: str | None = None,
    marker: str | None = "o",
    linestyle: str = "-",
    style: LinePanelStyle = COMPACT_LINE_STYLE,
    linewidth: float | None = None,
    markersize: float | None = None,
    alpha: float | None = None,
    zorder: int | None = None,
    **kwargs: Any,
) -> Any:
    return ax.plot(
        x,
        y,
        linestyle=linestyle,
        marker=marker,
        color=color,
        linewidth=style.line_width if linewidth is None else linewidth,
        markersize=style.marker_size if markersize is None else markersize,
        alpha=style.line_alpha if alpha is None else alpha,
        label=label,
        zorder=zorder,
        **kwargs,
    )


def plot_band(
    ax: plt.Axes,
    x: Any,
    low: Any,
    high: Any,
    *,
    color: str,
    style: LinePanelStyle = COMPACT_LINE_STYLE,
    alpha: float | None = None,
    label: str | None = None,
    zorder: int | None = None,
    **kwargs: Any,
) -> Any:
    return ax.fill_between(
        x,
        low,
        high,
        color=color,
        alpha=style.band_alpha if alpha is None else alpha,
        linewidth=0,
        label=label,
        zorder=zorder,
        **kwargs,
    )


def finish_line_panel(
    ax: plt.Axes,
    *,
    x_label: str | None = None,
    y_label: str | None = None,
    log_x: bool = False,
    log_y: bool = False,
    grid_axis: str | None = None,
    legend: bool | Mapping[str, Any] = False,
    bottom_legend_cols: int | None = None,
    bottom_legend_kwargs: Mapping[str, Any] | None = None,
    margins: Mapping[str, float] | None = None,
    style: LinePanelStyle = COMPACT_LINE_STYLE,
) -> None:
    if log_x:
        ax.set_xscale("log")
    if log_y:
        ax.set_yscale("log")
    if x_label is not None:
        ax.set_xlabel(x_label, fontsize=FONT_SMALL)
    if y_label is not None:
        ax.set_ylabel(y_label, fontsize=FONT_SMALL)
    ax.tick_params(labelsize=style.tick_labelsize)
    if grid_axis is not None:
        ax.grid(True, axis=grid_axis, which="both", alpha=style.grid_alpha)
    else:
        ax.grid(True, which="both", alpha=style.grid_alpha)

    if bottom_legend_cols is not None:
        legend_kwargs = compact_legend_kwargs(style=style)
        if bottom_legend_kwargs is not None:
            legend_kwargs.update(bottom_legend_kwargs)
        bottom_legend(ax, ncol=bottom_legend_cols, **legend_kwargs)
    elif legend:
        legend_kwargs = compact_legend_kwargs(style=style)
        if isinstance(legend, Mapping):
            legend_kwargs.update(legend)
        ax.legend(**legend_kwargs)

    if margins:
        finish_exact_panel(ax, **dict(margins))


__all__ = [
    "COMPACT_LINE_STYLE",
    "LinePanelStyle",
    "compact_legend_kwargs",
    "finish_line_panel",
    "plot_band",
    "plot_series",
]
