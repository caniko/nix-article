"""Shared drawing primitives for composite figures."""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.transforms import Bbox

from anx_plot.sizing import FONT_BASE, FONT_SMALL

from .palette import DARK, GREY_LIGHT, GREY_MID

# ── Drawing primitives ─────────────────────────────────────────────────


def diagram_box(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    color: str,
    *,
    label: str = "",
    sublabel: str = "",
    ec: str = "black",
    lw: float = 1.2,
    alpha: float = 1.0,
    ls: str = "-",
    label_color: str = "white",
    sublabel_color: str | None = None,
    label_size: float = FONT_BASE,
    sublabel_size: float = FONT_SMALL,
    pad: float = 0.01,
    zorder: int = 1,
) -> None:
    """Draw a rounded box with optional centred label and sublabel.

    All coordinates are in the axes data space (expected ``[0, 1]``).
    """
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle=f"round,pad={pad}",
            edgecolor=ec,
            facecolor=color,
            linewidth=lw,
            alpha=alpha,
            linestyle=ls,
            zorder=zorder,
        )
    )
    if label:
        ly = y + h / 2 if not sublabel else y + h * 0.65
        ax.text(
            x + w / 2,
            ly,
            label,
            ha="center",
            va="center",
            fontsize=label_size,
            fontweight="bold",
            color=label_color,
            zorder=zorder + 1,
        )
    if sublabel:
        ax.text(
            x + w / 2,
            y + h * 0.30,
            sublabel,
            ha="center",
            va="center",
            fontsize=sublabel_size,
            color=sublabel_color or label_color,
            zorder=zorder + 1,
        )


def diagram_arrow(
    ax: plt.Axes,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    color: str = GREY_MID,
    lw: float = 1.0,
    style: str = "->",
    ms: int = 8,
    ls: str = "-",
    zorder: int = 2,
    **kw,
) -> None:
    """Draw a FancyArrowPatch in data coordinates."""
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle=style,
            color=color,
            linewidth=lw,
            mutation_scale=ms,
            linestyle=ls,
            zorder=zorder,
            **kw,
        )
    )


def _legend_bbox(fig: plt.Figure, leg) -> tuple[float, float, float, float]:
    renderer = fig.canvas.get_renderer()
    fig.draw(renderer)
    to_fig = fig.transFigure.inverted()
    bb = leg.get_window_extent(renderer).transformed(to_fig)
    return bb.x0, bb.y0, bb.x1, bb.y1


def _solve_bottom(
    fig: plt.Figure,
    ax: plt.Axes,
    leg,
    *,
    min_gap_pt: float = 8.0,
    init_bottom: float = 0.50,
    left: float = 0.18,
    right: float = 0.98,
) -> float:
    renderer = fig.canvas.get_renderer()
    fig.draw(renderer)
    to_fig = fig.transFigure.inverted()
    xlabel_bb = ax.xaxis.label.get_window_extent(renderer).transformed(to_fig)
    if xlabel_bb.height > 1e-6:
        below_axes = xlabel_bb.y0
    else:
        tick_bbs = [
            t.get_window_extent(renderer).transformed(to_fig)
            for t in ax.xaxis.get_ticklabels()
            if t.get_text()
        ]
        below_axes = min(bb.y0 for bb in tick_bbs) if tick_bbs else init_bottom
    overhead = init_bottom - below_axes
    leg_top = leg.get_window_extent(renderer).transformed(to_fig).y1
    target_gap = _pt_to_fig_y(fig, min_gap_pt)
    return leg_top + target_gap + overhead


_CLIP_TOL = 0.01
_MIN_BOTTOM_MARGIN_PT = 2.0
_MIN_LEFT_MARGIN_PT = 2.0
_SOLVER_EPS = 1e-9


def _pt_to_fig_y(fig: plt.Figure, points: float) -> float:
    return points / (fig.get_size_inches()[1] * 72.0)


def _pt_to_fig_x(fig: plt.Figure, points: float) -> float:
    return points / (fig.get_size_inches()[0] * 72.0)


def _draw_renderer(fig: plt.Figure):
    fig.canvas.draw()
    return fig.canvas.get_renderer()


def _bbox_in_fig(fig: plt.Figure, artist):
    renderer = _draw_renderer(fig)
    return artist.get_window_extent(renderer).transformed(fig.transFigure.inverted())


def _bottom_axis_bbox(fig: plt.Figure, ax: plt.Axes):
    renderer = _draw_renderer(fig)
    to_fig = fig.transFigure.inverted()
    bboxes = []
    xlabel = ax.xaxis.label
    if xlabel.get_visible() and xlabel.get_text():
        bbox = xlabel.get_window_extent(renderer).transformed(to_fig)
        if bbox.width > 1e-6 or bbox.height > 1e-6:
            bboxes.append(bbox)
    for tick in ax.get_xticklabels():
        if tick.get_visible() and tick.get_text():
            bbox = tick.get_window_extent(renderer).transformed(to_fig)
            if bbox.width > 1e-6 or bbox.height > 1e-6:
                bboxes.append(bbox)
    if not bboxes:
        return None
    return Bbox.union(bboxes)


def _left_label_bbox(fig: plt.Figure, ax: plt.Axes):
    renderer = _draw_renderer(fig)
    to_fig = fig.transFigure.inverted()
    bboxes = []
    ylabel = ax.yaxis.label
    if ylabel.get_visible() and ylabel.get_text():
        bbox = ylabel.get_window_extent(renderer).transformed(to_fig)
        if bbox.width > 1e-6 or bbox.height > 1e-6:
            bboxes.append(bbox)
    for tick in ax.get_yticklabels():
        if tick.get_visible() and tick.get_text():
            bbox = tick.get_window_extent(renderer).transformed(to_fig)
            if bbox.width > 1e-6 or bbox.height > 1e-6:
                bboxes.append(bbox)
    if not bboxes:
        return None
    return Bbox.union(bboxes)


def solve_left_label_margin(
    ax: plt.Axes,
    *,
    min_canvas_margin_pt: float = _MIN_LEFT_MARGIN_PT,
    max_left: float | None = None,
    min_axes_width: float = 0.05,
) -> None:
    fig: plt.Figure = ax.figure
    if not ax.axison:
        return
    target = _pt_to_fig_x(fig, min_canvas_margin_pt)
    for _ in range(2):
        bbox = _left_label_bbox(fig, ax)
        if bbox is None or bbox.x0 + _SOLVER_EPS >= target:
            return
        left = fig.subplotpars.left
        upper = fig.subplotpars.right - min_axes_width
        if max_left is not None:
            upper = min(upper, max_left)
        adjusted = min(upper, left + (target - bbox.x0))
        if adjusted <= left + _SOLVER_EPS:
            break
        fig.subplots_adjust(left=adjusted)
    _assert_left_label_margin(ax, min_canvas_margin_pt=min_canvas_margin_pt)


def _assert_left_label_margin(
    ax: plt.Axes,
    *,
    min_canvas_margin_pt: float = _MIN_LEFT_MARGIN_PT,
) -> None:
    bbox = _left_label_bbox(ax.figure, ax)
    if bbox is None:
        return
    target = _pt_to_fig_x(ax.figure, min_canvas_margin_pt)
    if bbox.x0 + _SOLVER_EPS >= target:
        return
    msg = (
        "left-label solver could not keep y tick labels/ylabel inside the "
        f"canvas; left x={bbox.x0:.3f}, required >= {target:.3f}. "
        "Increase left margin with finish_exact_panel, abbreviate y tick "
        "labels, or change the panel layout."
    )
    raise RuntimeError(msg)


def solve_bottom_axis_margin(
    ax: plt.Axes,
    *,
    min_canvas_margin_pt: float = _MIN_BOTTOM_MARGIN_PT,
    max_bottom: float | None = None,
) -> None:
    fig: plt.Figure = ax.figure
    if not ax.axison:
        return
    bbox = _bottom_axis_bbox(fig, ax)
    if bbox is None:
        return
    target = _pt_to_fig_y(fig, min_canvas_margin_pt)
    if bbox.y0 + _SOLVER_EPS >= target:
        return
    bottom = fig.subplotpars.bottom
    upper = max_bottom if max_bottom is not None else max(0.0, fig.subplotpars.top - 0.02)
    adjusted = min(upper, bottom + (target - bbox.y0))
    if adjusted <= bottom:
        return
    fig.subplots_adjust(bottom=adjusted)


def _assert_bottom_axis_margin(
    ax: plt.Axes,
    *,
    min_canvas_margin_pt: float = _MIN_BOTTOM_MARGIN_PT,
) -> None:
    bbox = _bottom_axis_bbox(ax.figure, ax)
    if bbox is None:
        return
    target = _pt_to_fig_y(ax.figure, min_canvas_margin_pt)
    if bbox.y0 + _SOLVER_EPS >= target:
        return
    msg = (
        "bottom-axis solver could not keep x tick labels/xlabel inside the "
        f"canvas; lowest y={bbox.y0:.3f}, required >= {target:.3f}. "
        "Increase bottom margin with finish_exact_panel or abbreviate/rotate "
        "x tick labels."
    )
    raise RuntimeError(msg)


def check_figure_clipping(
    fig: plt.Figure,
    *,
    tol: float = _CLIP_TOL,
) -> list[str]:
    """Check whether any visible artist is clipped by the figure boundary."""
    renderer = fig.canvas.get_renderer()
    fig.draw(renderer)
    to_fig = fig.transFigure.inverted()
    warnings: list[str] = []

    for leg in fig.legends:
        bb = leg.get_window_extent(renderer).transformed(to_fig)
        if bb.x0 < -tol:
            warnings.append(f"Legend clipped on LEFT by {-bb.x0:.3f} fig-frac")
        if bb.x1 > 1.0 + tol:
            warnings.append(f"Legend clipped on RIGHT by {bb.x1 - 1.0:.3f} fig-frac")
        if bb.y0 < -tol:
            warnings.append(f"Legend clipped on BOTTOM by {-bb.y0:.3f} fig-frac")
        if bb.y1 > 1.0 + tol:
            warnings.append(f"Legend clipped on TOP by {bb.y1 - 1.0:.3f} fig-frac")

    for ax in fig.axes:
        for name, artist in [
            ("xlabel", ax.xaxis.label),
            ("ylabel", ax.yaxis.label),
            ("title", ax.title),
        ]:
            bb = artist.get_window_extent(renderer).transformed(to_fig)
            if bb.width < 1e-6 and bb.height < 1e-6:
                continue
            if name == "ylabel":
                if bb.x0 < -tol or bb.x1 > 1.0 + tol:
                    warnings.append(
                        f"{name} clipped horizontally: x=[{bb.x0:.3f}, {bb.x1:.3f}]"
                    )
            elif name == "xlabel":
                if bb.y0 < -tol or bb.y1 > 1.0 + tol:
                    warnings.append(
                        f"{name} clipped vertically: y=[{bb.y0:.3f}, {bb.y1:.3f}]"
                    )
            else:
                if bb.x0 < -tol or bb.x1 > 1.0 + tol:
                    warnings.append(
                        f"{name} clipped horizontally: x=[{bb.x0:.3f}, {bb.x1:.3f}]"
                    )
                if bb.y0 < -tol or bb.y1 > 1.0 + tol:
                    warnings.append(
                        f"{name} clipped vertically: y=[{bb.y0:.3f}, {bb.y1:.3f}]"
                    )

    return warnings


def bottom_legend(
    ax: plt.Axes,
    *,
    ncol: int = 2,
    left: float = 0.18,
    right: float = 0.98,
    min_gap_pt: float = 8.0,
    min_canvas_margin_pt: float = _MIN_BOTTOM_MARGIN_PT,
    handles=None,
    labels=None,
    **legend_kw,
) -> None:
    """Place a legend centred below the axes, auto-solving for minimal margin."""
    from anx_plot.sizing import FONT_LEGEND

    if handles is None or labels is None:
        handles, labels = ax.get_legend_handles_labels()
    if not handles or not labels:
        return
    if (leg_old := ax.get_legend()) is not None:
        leg_old.remove()
    fig: plt.Figure = ax.figure
    fig._tight_bbox = False

    init_bottom = 0.50
    legend_anchor = legend_kw.pop("bbox_to_anchor", (0.5, 0.0))
    if not isinstance(legend_anchor, tuple) or len(legend_anchor) < 2:
        legend_anchor = (0.5, 0.0)
    legend_anchor_x = float(legend_anchor[0])
    legend_anchor_y = float(legend_anchor[1])

    kw = dict(
        fontsize=FONT_LEGEND,
        loc="lower center",
        bbox_to_anchor=(legend_anchor_x, legend_anchor_y),
        ncol=ncol,
        columnspacing=0.6,
        framealpha=1.0,
        edgecolor=GREY_LIGHT,
    )
    kw.update(legend_kw)

    cur_ncol = ncol
    while True:
        fig.subplots_adjust(bottom=init_bottom, left=left, right=right)
        kw["ncol"] = cur_ncol
        kw["bbox_to_anchor"] = (legend_anchor_x, legend_anchor_y)
        for old in fig.legends[:]:
            old.remove()
        leg = fig.legend(handles=handles, labels=labels, **kw)
        x0, _y0, x1, _y1 = _legend_bbox(fig, leg)
        if x0 >= -_CLIP_TOL and x1 <= 1.0 + _CLIP_TOL:
            break
        if cur_ncol <= 1:
            break
        cur_ncol -= 1

    min_canvas = _pt_to_fig_y(fig, min_canvas_margin_pt)
    for _ in range(3):
        _x0, y0, _x1, _y1 = _legend_bbox(fig, leg)
        if y0 + _SOLVER_EPS >= min_canvas:
            break
        legend_anchor_y += min_canvas - y0
        kw["bbox_to_anchor"] = (legend_anchor_x, legend_anchor_y)
        for old in fig.legends[:]:
            old.remove()
        leg = fig.legend(handles=handles, labels=labels, **kw)

    optimal = _solve_bottom(
        fig,
        ax,
        leg,
        min_gap_pt=min_gap_pt,
        init_bottom=init_bottom,
        left=left,
        right=right,
    )
    max_bottom = max(0.0, fig.subplotpars.top - 0.02)
    optimal = min(optimal, max_bottom)
    fig.subplots_adjust(bottom=optimal, left=left, right=right)
    _assert_bottom_axis_margin(ax, min_canvas_margin_pt=min_canvas_margin_pt)
    _assert_bottom_legend_layout(
        fig,
        ax,
        leg,
        min_gap_pt=min_gap_pt,
        min_canvas_margin_pt=min_canvas_margin_pt,
    )
    solve_left_label_margin(ax)


def _assert_bottom_legend_layout(
    fig: plt.Figure,
    ax: plt.Axes,
    leg,
    *,
    min_gap_pt: float,
    min_canvas_margin_pt: float,
) -> None:
    legend_bb = _bbox_in_fig(fig, leg)
    min_canvas = _pt_to_fig_y(fig, min_canvas_margin_pt)
    if legend_bb.y0 + _SOLVER_EPS < min_canvas:
        msg = (
            "bottom_legend could not keep legend inside the canvas; "
            f"legend y0={legend_bb.y0:.3f}, required >= {min_canvas:.3f}. "
            "Reduce legend columns/labels or increase the panel's available "
            "bottom margin."
        )
        raise RuntimeError(msg)
    axis_bb = _bottom_axis_bbox(fig, ax)
    if axis_bb is None:
        return
    min_gap = _pt_to_fig_y(fig, min_gap_pt)
    gap = axis_bb.y0 - legend_bb.y1
    if gap + _SOLVER_EPS < min_gap:
        msg = (
            "bottom_legend could not keep enough clearance between x-axis "
            f"text and the legend; gap={gap:.3f}, required >= {min_gap:.3f}. "
            "Increase bottom margin, reduce legend columns/labels, or shorten "
            "x tick labels."
        )
        raise RuntimeError(msg)


# ── Label abbreviation registry ─────────────────────────────────────
# Downstream projects can extend this dictionary or monkey-patch
# abbreviate_label to add domain-specific abbreviations.

_LABEL_ABBREVIATIONS: dict[str, dict[str, str]] = {}


def abbreviate_label(value: object, domain: str | None = None) -> str:
    """Return a registered abbreviation, preserving unknowns."""
    text = str(value)
    if domain is not None:
        return _LABEL_ABBREVIATIONS.get(domain, {}).get(text, text)
    for labels in _LABEL_ABBREVIATIONS.values():
        if text in labels:
            return labels[text]
    return text


def abbreviate_labels(values, domain: str | None = None) -> list[str]:
    return [abbreviate_label(value, domain=domain) for value in values]


def label_badge(
    ax: plt.Axes,
    x: float,
    y: float,
    text: str,
    *,
    fontsize: float = FONT_BASE,
    color: str = DARK,
    **kw,
) -> None:
    """Small labelled badge (white background, grey border)."""
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=color,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.25",
            facecolor="white",
            edgecolor=GREY_LIGHT,
            linewidth=0.8,
            alpha=0.95,
        ),
        **kw,
    )
