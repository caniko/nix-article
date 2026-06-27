"""Statistical significance annotation primitives for composite figures."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from anx_plot.sizing import FONT_SMALL

from .standard import place_axes_annotation
from .palette import GREY_DARK


# ── P-value formatting ───────────────────────────────────────────────


def format_pvalue(p: float, *, style: str = "stars") -> str:
    """Format a p-value for display.

    Parameters
    ----------
    p : float
        Raw p-value.
    style : str
        ``"stars"``  -> ``"***"`` / ``"**"`` / ``"*"`` / ``"ns"``.
        ``"text"``   -> ``"$p < 0.001$"`` or ``"$p = 0.023$"``.
    """
    if not np.isfinite(p):
        return "n/a"
    if style == "stars":
        if p < 0.001:
            return "***"
        if p < 0.01:
            return "**"
        if p < 0.05:
            return "*"
        return "ns"
    if style == "text":
        if p < 0.001:
            return "$p < 0.001$"
        return f"$p = {p:.3f}$"
    return f"p={p:.3f}"


def format_statistic(value: float, *, precision: int = 2, fallback: str = "n/a") -> str:
    if not np.isfinite(value):
        return fallback
    return f"{value:.{precision}f}"


# ── Multiple-comparison correction ───────────────────────────────────


def correct_pvalues(
    pvalues: list[float],
    method: str = "holm",
) -> list[float]:
    """Apply multiple-comparison correction.

    Parameters
    ----------
    pvalues : list[float]
        Raw p-values.
    method : str
        ``"holm"`` (default), ``"bonferroni"``, or ``"fdr_bh"``
        (Benjamini-Hochberg).
    """
    n = len(pvalues)
    if n == 0:
        return []

    if method == "bonferroni":
        return [min(p * n, 1.0) for p in pvalues]

    if method == "holm":
        order = np.argsort(pvalues)
        corrected = np.empty(n)
        cummax = 0.0
        for rank, idx in enumerate(order):
            adj = pvalues[idx] * (n - rank)
            cummax = max(cummax, adj)
            corrected[idx] = min(cummax, 1.0)
        return corrected.tolist()

    if method == "fdr_bh":
        order = np.argsort(pvalues)[::-1]
        corrected = np.empty(n)
        cummin = 1.0
        for rank_desc, idx in enumerate(order):
            rank_asc = n - rank_desc
            adj = pvalues[idx] * n / rank_asc
            cummin = min(cummin, adj)
            corrected[idx] = min(cummin, 1.0)
        return corrected.tolist()

    msg = f"Unknown correction method: {method!r}"
    raise ValueError(msg)


# ── Significance bracket ─────────────────────────────────────────────


def significance_bracket(
    ax: plt.Axes,
    x1: float,
    x2: float,
    y: float,
    p: float,
    *,
    height: float = 0.02,
    style: str = "stars",
    fontsize: float = FONT_SMALL,
    color: str = GREY_DARK,
    lw: float = 0.8,
) -> None:
    """Draw a significance bracket between two x-positions."""
    label = format_pvalue(p, style=style)
    if style == "stars" and label == "ns":
        return

    ymin, ymax = ax.get_ylim()
    tick = (ymax - ymin) * height
    ytop = y + tick

    ax.plot([x1, x1, x2, x2], [y, ytop, ytop, y], lw=lw, color=color, clip_on=False)
    ax.text(
        (x1 + x2) / 2,
        ytop,
        label,
        ha="center",
        va="bottom",
        fontsize=fontsize,
        color=color,
    )


# ── Omnibus test annotation ──────────────────────────────────────────


def annotate_omnibus(
    ax: plt.Axes,
    test_name: str,
    statistic: float,
    p: float,
    *,
    loc: str = "upper right",
    fontsize: float = FONT_SMALL,
    color: str = GREY_DARK,
) -> None:
    """Place an omnibus test result as corner text."""
    stat_str = format_statistic(statistic, precision=1)
    p_str = "p = n/a" if not np.isfinite(p) else format_pvalue(p, style="text")
    text = f"{test_name} = {stat_str}, {p_str}"
    place_axes_annotation(
        ax,
        text,
        loc=loc,
        fontsize=fontsize,
        color=color,
    )


# ── Heatmap significance overlay ─────────────────────────────────────


def heatmap_stars(
    ax: plt.Axes,
    p_matrix: np.ndarray,
    *,
    thresholds: tuple[float, ...] = (0.001, 0.01, 0.05),
    fontsize: float = FONT_SMALL,
    color: str = "white",
    offset_y: float = 0.15,
) -> None:
    """Overlay significance stars on an existing heatmap."""
    nrows, ncols = p_matrix.shape
    for i in range(nrows):
        for j in range(ncols):
            p = p_matrix[i, j]
            stars = format_pvalue(p, style="stars")
            if stars == "ns":
                continue
            ax.text(
                j + 0.5,
                i + 0.5 + offset_y,
                stars,
                ha="center",
                va="center",
                fontsize=fontsize,
                color=color,
                fontweight="bold",
            )


# ── Regression annotation ────────────────────────────────────────────


def annotate_regression(
    ax: plt.Axes,
    r_squared: float,
    p: float,
    *,
    loc: str = "upper left",
    fontsize: float = FONT_SMALL,
    color: str = GREY_DARK,
) -> None:
    """Place an R-squared + p-value annotation in a corner."""
    if not np.isfinite(r_squared) or not np.isfinite(p):
        text = "$R^2$ = n/a, p = n/a"
    else:
        p_str = format_pvalue(p, style="text")
        text = f"$R^2 = {r_squared:.2f}$, {p_str}"

    ha = "right" if "right" in loc else "left"
    va = "top" if "upper" in loc else "bottom"
    x = 0.97 if "right" in loc else 0.03
    y = 0.97 if "upper" in loc else 0.03

    ax.text(
        x,
        y,
        text,
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=fontsize,
        color=color,
    )
