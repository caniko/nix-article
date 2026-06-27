"""Shared figure export: SVG + PNG (via inkscape) pipeline."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import re
import shutil
import subprocess
from pathlib import Path

from matplotlib.artist import Artist
from matplotlib.legend import Legend
import matplotlib.pyplot as plt
from matplotlib.text import Text

logger = logging.getLogger(__name__)

_PATCH1_RE = re.compile(
    r"<g\s[^>]*id=\"patch_1\"[^>]*>\s*<path\b[^/]*/>\s*</g>",
    re.DOTALL,
)

_BOUNDARY_GUARD_IGNORE_ATTR = "_anx_export_boundary_guard_ignore"


@dataclass(frozen=True)
class ExportBoundaryViolation:
    """A rendered artist that touches or crosses the fixed export canvas."""

    artist: str
    sides: tuple[str, ...]
    gaps_pt: dict[str, float]
    required_margin_pt: float

    def describe(self) -> str:
        side_text = "/".join(self.sides)
        gap_text = ", ".join(
            f"{side}={self.gaps_pt[side]:.1f} pt" for side in self.sides
        )
        return (
            f"{self.artist} touches {side_text} export boundary "
            f"({gap_text}; requires >= {self.required_margin_pt:.1f} pt)"
        )


class ExportBoundaryError(RuntimeError):
    """Raised when exact-size export would clip publication-relevant artists."""


def allow_export_boundary_clip(artist: Artist, reason: str) -> Artist:
    """Mark one artist as intentionally allowed to cross the export boundary."""
    setattr(artist, _BOUNDARY_GUARD_IGNORE_ATTR, reason)
    return artist


def measure_export_boundary_violations(
    fig: plt.Figure,
    *,
    safety_margin_pt: float = 1.0,
) -> list[ExportBoundaryViolation]:
    """Measure visible publication artists against the rendered canvas."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    canvas = fig.bbox
    margin_px = safety_margin_pt * fig.dpi / 72.0
    violations: list[ExportBoundaryViolation] = []
    seen: set[int] = set()

    for label, artist in _boundary_guard_artists(fig):
        identity = id(artist)
        if identity in seen:
            continue
        seen.add(identity)
        if _is_boundary_guard_ignored(artist) or not artist.get_visible():
            continue
        bbox = artist.get_window_extent(renderer)
        if bbox.width <= 0.0 and bbox.height <= 0.0:
            continue

        gaps = {
            "left": bbox.x0 - canvas.x0,
            "right": canvas.x1 - bbox.x1,
            "bottom": bbox.y0 - canvas.y0,
            "top": canvas.y1 - bbox.y1,
        }
        sides = tuple(side for side, gap in gaps.items() if gap < margin_px)
        if not sides:
            continue
        violations.append(
            ExportBoundaryViolation(
                artist=label,
                sides=sides,
                gaps_pt={side: gaps[side] * 72.0 / fig.dpi for side in sides},
                required_margin_pt=safety_margin_pt,
            )
        )

    return violations


def validate_export_boundary(
    fig: plt.Figure,
    *,
    safety_margin_pt: float = 1.0,
    context: str | None = None,
) -> None:
    """Fail if exact-size export would place visible artists on the boundary."""
    violations = measure_export_boundary_violations(
        fig, safety_margin_pt=safety_margin_pt
    )
    if not violations:
        return

    prefix = (
        f"Export boundary guard failed for {context}:"
        if context
        else "Export boundary guard failed:"
    )
    details = "\n".join(f"- {violation.describe()}" for violation in violations)
    sides = {side for violation in violations for side in violation.sides}
    fix = _boundary_guard_fix(sides)
    raise ExportBoundaryError(f"{prefix}\n{details}\nRecommended fix: {fix}")


def _boundary_guard_artists(fig: plt.Figure) -> list[tuple[str, Artist]]:
    artists: list[tuple[str, Artist]] = []
    for idx, text in enumerate(fig.texts):
        artists.append((f"figure text {idx}", text))
    for idx, legend in enumerate(fig.legends):
        artists.append((f"figure legend {idx}", legend))

    for ax_index, ax in enumerate(fig.axes):
        axis_name = f"axes {ax_index}"
        if ax.axison:
            artists.extend(
                [
                    (f"{axis_name} x label", ax.xaxis.label),
                    (f"{axis_name} y label", ax.yaxis.label),
                    (f"{axis_name} title", ax.title),
                    (f"{axis_name} left title", ax._left_title),
                    (f"{axis_name} right title", ax._right_title),
                    (f"{axis_name} x offset", ax.xaxis.offsetText),
                    (f"{axis_name} y offset", ax.yaxis.offsetText),
                ]
            )
            for tick_index, text in enumerate(ax.get_xticklabels()):
                artists.append((f"{axis_name} x tick label {tick_index}", text))
            for tick_index, text in enumerate(ax.get_yticklabels()):
                artists.append((f"{axis_name} y tick label {tick_index}", text))
        for text_index, text in enumerate(ax.texts):
            artists.append((f"{axis_name} annotation {text_index}", text))
        legend = ax.get_legend()
        if isinstance(legend, Legend):
            artists.append((f"{axis_name} legend", legend))
    return [(label, artist) for label, artist in artists if _has_boundary_extent(artist)]


def _has_boundary_extent(artist: Artist) -> bool:
    if isinstance(artist, Text):
        return bool(artist.get_text())
    return hasattr(artist, "get_window_extent")


def _is_boundary_guard_ignored(artist: Artist) -> bool:
    return bool(getattr(artist, _BOUNDARY_GUARD_IGNORE_ATTR, False))


def _boundary_guard_fix(sides: set[str]) -> str:
    fixes: list[str] = []
    if "left" in sides:
        fixes.append(
            "increase left margin with finish_exact_panel/mark_exact_margins "
            "or abbreviate y tick labels"
        )
    if "right" in sides:
        fixes.append(
            "increase right margin with finish_exact_panel/mark_exact_margins "
            "or shorten right-side annotations"
        )
    if "bottom" in sides:
        fixes.append(
            "increase bottom margin with finish_exact_panel/mark_exact_margins, "
            "rotate/abbreviate x tick labels, or use bottom_legend"
        )
    if "top" in sides:
        fixes.append(
            "increase top margin with finish_exact_panel/mark_exact_margins "
            "or move top annotations inward"
        )
    return "; ".join(fixes)


def _strip_figure_background(svg_path: Path) -> None:
    """Remove matplotlib's figure-level background rect (``patch_1``)."""
    text = svg_path.read_text()
    text_new = _PATCH1_RE.sub("", text, count=1)
    if text_new != text:
        svg_path.write_text(text_new)


def export_fig(
    fig: plt.Figure,
    stem: Path | None,
    *,
    pad_inches: float = 0.04,
) -> plt.Figure:
    """Save *fig* as SVG + PNG if *stem* is provided, else return unchanged.

    The PNG is rasterised from the SVG via ``inkscape``.  If inkscape is
    not on ``$PATH`` the PNG is written directly by matplotlib as a fallback.

    When ``fig._tight_bbox`` is set to ``False`` (see
    :func:`mark_exact_margins`), tight bbox is disabled and the export
    preserves the exact ``figsize`` — use this for panels that manage
    their own margins via ``subplots_adjust``.
    """
    if stem is None:
        return fig

    stem = stem.with_suffix("")
    stem.parent.mkdir(parents=True, exist_ok=True)

    savefig_dpi = plt.rcParams.get("savefig.dpi", 300)
    dpi = int(fig.dpi if savefig_dpi == "figure" else savefig_dpi)

    tight = getattr(fig, "_tight_bbox", True)
    bbox_kw: dict = {"bbox_inches": "tight", "pad_inches": pad_inches} if tight else {}
    if not tight:
        validate_export_boundary(fig, context=stem.name)

    svg_path = stem.with_suffix(".svg")
    fig.savefig(str(svg_path), format="svg", transparent=True, **bbox_kw)

    png_path = stem.with_suffix(".png")
    if shutil.which("inkscape") is not None:
        if tight:
            _strip_figure_background(svg_path)
            subprocess.run(
                [
                    "inkscape",
                    str(svg_path),
                    "--export-area-drawing",
                    "--export-type=svg",
                    f"--export-filename={svg_path}",
                ],
                check=True,
                capture_output=True,
            )
        export_area = "--export-area-drawing" if tight else "--export-area-page"
        subprocess.run(
            [
                "inkscape",
                str(svg_path),
                export_area,
                "--export-type=png",
                f"--export-dpi={dpi}",
                f"--export-filename={png_path}",
                "--export-background=#ffffff",
            ],
            check=True,
            capture_output=True,
        )
    else:
        logger.debug("inkscape not found, falling back to matplotlib PNG")
        fig.savefig(str(png_path), format="png", dpi=dpi, **bbox_kw)

    return fig
