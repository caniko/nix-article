"""Shared standards for manuscript composite figure exports."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
import math
from pathlib import Path
import shlex
from typing import Any

from matplotlib.artist import Artist
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from matplotlib.colors import Colormap
from matplotlib.transforms import Bbox

from anx_plot.sizing import FONT_LEGEND, FONT_SMALL

from .helpers import (
    bottom_legend,
    solve_bottom_axis_margin,
    solve_left_label_margin,
)
from .layout import export_panels as _export_panels_impl
from .palette import GREY_LIGHT

PanelDrawFn = Callable[[plt.Axes], None]


@dataclass(frozen=True)
class PanelSpec:
    """Declarative export metadata for one figure panel."""

    letter: str
    draw: PanelDrawFn
    required: bool = True


@dataclass(frozen=True)
class ArtifactCommand:
    """A shell command stored as argv and rendered only for diagnostics."""

    argv: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.argv:
            raise ValueError("ArtifactCommand requires at least one argv item")

    def render(self) -> str:
        return shlex.join(self.argv)

    def __str__(self) -> str:
        return self.render()


@dataclass(frozen=True)
class RequiredArtifact:
    """A production input required before a manuscript figure can export."""

    path: Path
    description: str
    producer: str
    regenerate: ArtifactCommand
    validate: ArtifactCommand


@dataclass(frozen=True)
class HeatmapDensityPolicy:
    """Print-size policy for dense manuscript heatmaps."""

    mode: str = "full"
    min_annotation_cell_width_pt: float = 8.0
    min_annotation_cell_height_pt: float = 6.0
    min_x_label_cell_width_pt: float = 6.0
    min_y_label_cell_height_pt: float = 5.0
    min_colorbar_label_axes_width_pt: float = 0.0
    tick_labelsize_delta: float = 0.0
    annotation_size_delta: float = 0.0


@dataclass(frozen=True)
class HeatmapDensityDecision:
    """Resolved heatmap density choices for one rendered axes."""

    policy: HeatmapDensityPolicy
    rows: int
    cols: int
    cell_width_pt: float
    cell_height_pt: float
    axes_width_pt: float
    axes_height_pt: float
    tick_labelsize: float
    annotation_size: float
    show_annotations: bool
    show_colorbar_label: bool
    x_tick_step: int
    y_tick_step: int


_HEATMAP_DENSITY_POLICIES = {
    "full": HeatmapDensityPolicy(mode="full"),
    "compact": HeatmapDensityPolicy(
        mode="compact",
        min_annotation_cell_width_pt=12.0,
        min_annotation_cell_height_pt=8.0,
        min_x_label_cell_width_pt=9.0,
        min_y_label_cell_height_pt=6.0,
        min_colorbar_label_axes_width_pt=90.0,
        tick_labelsize_delta=0.5,
        annotation_size_delta=0.5,
    ),
    "tiny_panel": HeatmapDensityPolicy(
        mode="tiny_panel",
        min_annotation_cell_width_pt=16.0,
        min_annotation_cell_height_pt=10.0,
        min_x_label_cell_width_pt=12.0,
        min_y_label_cell_height_pt=7.5,
        min_colorbar_label_axes_width_pt=120.0,
        tick_labelsize_delta=1.0,
        annotation_size_delta=1.0,
    ),
}


@dataclass(frozen=True)
class AnnotationCandidate:
    """Deterministic candidate for collision-aware annotation placement."""

    x: float
    y: float
    ha: str = "left"
    va: str = "bottom"
    dx_pt: float = 0.0
    dy_pt: float = 0.0


@dataclass(frozen=True)
class EndpointLabel:
    """Line endpoint label candidate in data coordinates."""

    x: float
    y: float
    text: str
    color: str


_CORNER_ANNOTATION_CANDIDATES: dict[str, tuple[AnnotationCandidate, ...]] = {
    "upper right": (
        AnnotationCandidate(0.97, 0.97, "right", "top"),
        AnnotationCandidate(0.03, 0.97, "left", "top"),
        AnnotationCandidate(0.97, 0.03, "right", "bottom"),
        AnnotationCandidate(0.03, 0.03, "left", "bottom"),
    ),
    "upper left": (
        AnnotationCandidate(0.03, 0.97, "left", "top"),
        AnnotationCandidate(0.97, 0.97, "right", "top"),
        AnnotationCandidate(0.03, 0.03, "left", "bottom"),
        AnnotationCandidate(0.97, 0.03, "right", "bottom"),
    ),
    "lower right": (
        AnnotationCandidate(0.97, 0.03, "right", "bottom"),
        AnnotationCandidate(0.03, 0.03, "left", "bottom"),
        AnnotationCandidate(0.97, 0.97, "right", "top"),
        AnnotationCandidate(0.03, 0.97, "left", "top"),
    ),
    "lower left": (
        AnnotationCandidate(0.03, 0.03, "left", "bottom"),
        AnnotationCandidate(0.97, 0.03, "right", "bottom"),
        AnnotationCandidate(0.03, 0.97, "left", "top"),
        AnnotationCandidate(0.97, 0.97, "right", "top"),
    ),
}

_DATA_ANNOTATION_OFFSETS: tuple[AnnotationCandidate, ...] = (
    AnnotationCandidate(0.0, 0.0, "left", "bottom", 6.0, 4.0),
    AnnotationCandidate(0.0, 0.0, "right", "bottom", -6.0, 4.0),
    AnnotationCandidate(0.0, 0.0, "left", "top", 6.0, -4.0),
    AnnotationCandidate(0.0, 0.0, "right", "top", -6.0, -4.0),
    AnnotationCandidate(0.0, 0.0, "center", "bottom", 0.0, 8.0),
    AnnotationCandidate(0.0, 0.0, "center", "top", 0.0, -8.0),
)


@dataclass(frozen=True)
class FigureExportSpec:
    """Declarative export contract for a registered manuscript figure."""

    prefix: str
    panels: Mapping[str, PanelDrawFn] | Iterable[PanelSpec]
    required_artifacts: Iterable[RequiredArtifact] = ()


def _format_artifact_error(
    message: str,
    artifact: RequiredArtifact,
) -> RuntimeError:
    return RuntimeError(
        f"{message}\n"
        f"Missing or invalid artifact: `{artifact.path}`\n"
        f"Why required: {artifact.description}\n"
        f"Upstream producer: `{artifact.producer}`\n"
        f"Regenerate with: `{artifact.regenerate}`\n"
        f"Validate with: `{artifact.validate}`"
    )


def required_data_error(
    message: str,
    *,
    artifact: Path | str,
    description: str,
    producer: str,
    regenerate: ArtifactCommand | tuple[str, ...] | str,
    validate: ArtifactCommand | tuple[str, ...] | str,
) -> RuntimeError:
    """Create a standard required-data failure for production figure exports."""

    def _command(value: ArtifactCommand | tuple[str, ...] | str) -> ArtifactCommand:
        if isinstance(value, ArtifactCommand):
            return value
        if isinstance(value, tuple):
            return ArtifactCommand(value)
        return ArtifactCommand(("sh", "-lc", value))

    return _format_artifact_error(
        message,
        RequiredArtifact(
            path=Path(artifact),
            description=description,
            producer=producer,
            regenerate=_command(regenerate),
            validate=_command(validate),
        ),
    )


def require_artifacts(artifacts: Iterable[RequiredArtifact]) -> None:
    """Fail if any required artifact is missing."""
    for artifact in artifacts:
        if not artifact.path.exists():
            raise _format_artifact_error(
                "Required figure artifact is missing.", artifact
            )


def panel_mapping(
    panels: Mapping[str, PanelDrawFn] | Iterable[PanelSpec],
) -> dict[str, PanelDrawFn]:
    """Normalize panel declarations to the mapping expected by FigureFit export."""
    if isinstance(panels, Mapping):
        return dict(panels)
    return {panel.letter: panel.draw for panel in panels if panel.required}


def export_figure(
    spec: FigureExportSpec,
    output_dir: Path,
    *,
    prefix: str | None = None,
) -> list[Path]:
    """Validate required inputs and export a standardized figure spec."""
    require_artifacts(spec.required_artifacts)
    return _export_panels_impl(
        panel_mapping(spec.panels),
        output_dir,
        prefix=prefix or spec.prefix,
    )


def mark_exact_margins(
    fig: plt.Figure,
    *,
    left: float | None = None,
    right: float | None = None,
    bottom: float | None = None,
    top: float | None = None,
) -> None:
    """Apply fixed margins and opt into exact export boundary validation."""
    kwargs = {
        name: value
        for name, value in {
            "left": left,
            "right": right,
            "bottom": bottom,
            "top": top,
        }.items()
        if value is not None
    }
    if kwargs:
        fig.subplots_adjust(**kwargs)
    fig._tight_bbox = False


def finish_exact_panel(
    ax: plt.Axes,
    *,
    left: float | None = None,
    right: float | None = None,
    bottom: float | None = None,
    top: float | None = None,
) -> None:
    """Apply fixed panel margins for export-size-sensitive panels."""
    mark_exact_margins(ax.figure, left=left, right=right, bottom=bottom, top=top)
    solve_left_label_margin(ax)
    solve_bottom_axis_margin(ax)


def empty_panel(
    ax: plt.Axes,
    message: str,
    *,
    fontsize: float = FONT_SMALL,
    color: str = "#666666",
) -> None:
    """Render the standard diagnostic empty panel."""
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=fontsize, color=color)
    ax.set_axis_off()


def add_colorbar(
    im: Any,
    ax: plt.Axes,
    label: str,
    *,
    fraction: float = 0.04,
    pad: float = 0.015,
    labelsize: float = FONT_SMALL,
    tick_labelsize: float | None = None,
) -> Any:
    """Attach a consistently styled vertical colorbar to a panel."""
    cbar = ax.figure.colorbar(im, ax=ax, fraction=fraction, pad=pad)
    decision = getattr(ax, "_anx_heatmap_density_decision", None)
    if isinstance(decision, HeatmapDensityDecision) and not decision.show_colorbar_label:
        label = ""
    cbar.set_label(label, fontsize=labelsize)
    cbar.ax.tick_params(labelsize=tick_labelsize or FONT_SMALL - 1)
    return cbar


def finish_axes(
    ax: plt.Axes,
    *,
    x_label: str | None = None,
    y_label: str | None = None,
    grid_axis: str | None = "y",
    grid_alpha: float = 0.25,
    legend: bool = False,
    legend_loc: str = "best",
    bottom_legend_cols: int | None = None,
) -> None:
    """Apply common manuscript chart finishing."""
    if x_label is not None:
        ax.set_xlabel(x_label, fontsize=FONT_SMALL)
    if y_label is not None:
        ax.set_ylabel(y_label, fontsize=FONT_SMALL)
    if grid_axis:
        ax.grid(True, axis=grid_axis, alpha=grid_alpha)
    ax.tick_params(labelsize=FONT_SMALL)
    if bottom_legend_cols is not None:
        bottom_legend(ax, ncol=bottom_legend_cols)
    elif legend:
        ax.legend(
            loc=legend_loc,
            fontsize=FONT_LEGEND,
            frameon=True,
            framealpha=1,
            facecolor="white",
            edgecolor=GREY_LIGHT,
        )


def _margin_px(fig: plt.Figure, margin_pt: float) -> float:
    return margin_pt * fig.dpi / 72.0


def _expand_bbox(bbox: Bbox, margin_px: float) -> Bbox:
    return Bbox.from_extents(
        bbox.x0 - margin_px,
        bbox.y0 - margin_px,
        bbox.x1 + margin_px,
        bbox.y1 + margin_px,
    )


def _artist_window_bbox(
    artist: Artist,
    renderer,
) -> Bbox | None:
    try:
        bbox = artist.get_window_extent(renderer)
        if bbox.width > 0.0 or bbox.height > 0.0:
            return bbox
    except Exception:
        pass
    if isinstance(artist, Line2D):
        path = artist.get_path()
        if path.vertices.size == 0:
            return None
        points = artist.get_transform().transform(path.vertices)
        bbox = Bbox.null()
        bbox.update_from_data_xy(points, ignore=True)
        return bbox
    return None


def _annotation_fits(
    ax: plt.Axes,
    artist: Artist,
    *,
    avoid_artists: Sequence[Artist] = (),
    avoid_bboxes: Sequence[Bbox] = (),
    keep_inside: str = "axes",
    min_margin_pt: float = 1.0,
) -> bool:
    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox = _artist_window_bbox(artist, renderer)
    if bbox is None:
        return False
    margin = _margin_px(fig, min_margin_pt)
    boundary = ax.bbox if keep_inside == "axes" else fig.bbox
    if (
        bbox.x0 < boundary.x0 + margin
        or bbox.x1 > boundary.x1 - margin
        or bbox.y0 < boundary.y0 + margin
        or bbox.y1 > boundary.y1 - margin
    ):
        return False
    blockers = list(avoid_bboxes)
    for blocker in avoid_artists:
        blocker_bbox = _artist_window_bbox(blocker, renderer)
        if blocker_bbox is not None:
            blockers.append(blocker_bbox)
    for blocker_bbox in blockers:
        if bbox.overlaps(_expand_bbox(blocker_bbox, margin)):
            return False
    return True


def place_axes_annotation(
    ax: plt.Axes,
    text: str,
    *,
    loc: str = "upper right",
    candidates: Sequence[AnnotationCandidate] | None = None,
    avoid_artists: Sequence[Artist] = (),
    avoid_bboxes: Sequence[Bbox] = (),
    fontsize: float = FONT_SMALL,
    color: str = "#555555",
    bbox: Mapping[str, Any] | None = None,
    min_margin_pt: float = 1.0,
    required: bool = True,
    **text_kw: Any,
) -> Artist | None:
    """Place axes-corner text at the first non-colliding deterministic candidate."""
    options = tuple(candidates or _CORNER_ANNOTATION_CANDIDATES.get(loc, ()))
    if not options:
        options = _CORNER_ANNOTATION_CANDIDATES["upper right"]
    fallback: Artist | None = None
    for candidate in options:
        artist = ax.annotate(
            text,
            (candidate.x, candidate.y),
            xycoords=ax.transAxes,
            xytext=(candidate.dx_pt, candidate.dy_pt),
            textcoords="offset points",
            ha=candidate.ha,
            va=candidate.va,
            fontsize=fontsize,
            color=color,
            bbox=bbox,
            **text_kw,
        )
        if _annotation_fits(
            ax,
            artist,
            avoid_artists=avoid_artists,
            avoid_bboxes=avoid_bboxes,
            min_margin_pt=min_margin_pt,
        ):
            if fallback is not None:
                fallback.remove()
            return artist
        if fallback is None and required:
            fallback = artist
        else:
            artist.remove()
    return fallback


def place_data_annotation(
    ax: plt.Axes,
    text: str,
    xy: tuple[float, float],
    *,
    candidates: Sequence[AnnotationCandidate] = _DATA_ANNOTATION_OFFSETS,
    avoid_artists: Sequence[Artist] = (),
    avoid_bboxes: Sequence[Bbox] = (),
    fontsize: float = FONT_SMALL,
    color: str = "#555555",
    min_margin_pt: float = 1.0,
    required: bool = False,
    arrow: bool = False,
    **text_kw: Any,
) -> Artist | None:
    """Place data-anchored text using deterministic offset candidates."""
    fallback: Artist | None = None
    for candidate in candidates:
        arrowprops = (
            {"arrowstyle": "-", "color": color, "linewidth": 0.6, "shrinkA": 0, "shrinkB": 2}
            if arrow
            else None
        )
        artist = ax.annotate(
            text,
            xy,
            xycoords="data",
            xytext=(candidate.dx_pt, candidate.dy_pt),
            textcoords="offset points",
            ha=candidate.ha,
            va=candidate.va,
            fontsize=fontsize,
            color=color,
            arrowprops=arrowprops,
            **text_kw,
        )
        if _annotation_fits(
            ax,
            artist,
            avoid_artists=avoid_artists,
            avoid_bboxes=avoid_bboxes,
            min_margin_pt=min_margin_pt,
        ):
            if fallback is not None:
                fallback.remove()
            return artist
        if fallback is None and required:
            fallback = artist
        else:
            artist.remove()
    return fallback


def place_endpoint_labels_or_legend(
    ax: plt.Axes,
    labels: Sequence[EndpointLabel],
    *,
    max_inline: int = 5,
    max_legend_items: int = 8,
    legend_title: str | None = None,
    fontsize: float = FONT_SMALL,
) -> str:
    """Place endpoint labels or use a compact legend when labels are too dense."""
    ordered = sorted(labels, key=lambda label: (label.text, label.x, label.y))
    if not ordered:
        return "none"
    if len(ordered) > max_inline:
        handles = [
            Line2D([0], [0], color=label.color, lw=1.2, label=label.text)
            for label in ordered[:max_legend_items]
        ]
        remaining = len(ordered) - len(handles)
        if remaining > 0:
            handles.append(
                Line2D([0], [0], color="#888888", lw=0.0, label=f"+{remaining} more")
            )
        ax.legend(
            handles=handles,
            title=legend_title,
            fontsize=max(fontsize - 1.0, 4.5),
            title_fontsize=max(fontsize - 0.5, 5.0),
            loc="upper left",
            frameon=True,
            framealpha=0.9,
            borderpad=0.25,
            handlelength=1.2,
            labelspacing=0.25,
        )
        return "legend"

    placed_bboxes: list[Bbox] = []
    placed_artists: list[Artist] = []
    for label in ordered:
        artist = place_data_annotation(
            ax,
            label.text,
            (label.x, label.y),
            avoid_bboxes=placed_bboxes,
            fontsize=fontsize,
            color=label.color,
        )
        if artist is None:
            for placed in placed_artists:
                placed.remove()
            ax.legend(
                handles=[
                    Line2D([0], [0], color=item.color, lw=1.2, label=item.text)
                    for item in ordered[:max_legend_items]
                ],
                title=legend_title,
                fontsize=max(fontsize - 1.0, 4.5),
                loc="upper left",
                frameon=True,
                framealpha=0.9,
            )
            return "legend"
        ax.figure.canvas.draw()
        bbox = _artist_window_bbox(
            artist,
            ax.figure.canvas.get_renderer(),
        )
        if bbox is not None:
            placed_bboxes.append(bbox)
        placed_artists.append(artist)
    return "inline"


def ensure_y_headroom(
    ax: plt.Axes,
    values: Sequence[float],
    *,
    fraction: float = 0.16,
) -> None:
    """Expand the y-axis upper limit so marker/endpoint annotations have room."""
    finite = [float(value) for value in values if math.isfinite(float(value))]
    if not finite:
        return
    ymax_value = max(finite)
    ymin, ymax = ax.get_ylim()
    if ax.get_yscale() == "log":
        if ymax_value <= 0:
            return
        target = ymax_value * (1.0 + max(fraction, 0.0) * 2.0)
    else:
        span = ymax - ymin if ymax > ymin else max(abs(ymax_value), 1.0)
        target = ymax_value + span * max(fraction, 0.0)
    if target > ymax:
        ax.set_ylim(ymin, target)


def _resolve_heatmap_density_policy(
    density_policy: HeatmapDensityPolicy | str | None,
) -> HeatmapDensityPolicy:
    if density_policy is None:
        return _HEATMAP_DENSITY_POLICIES["full"]
    if isinstance(density_policy, HeatmapDensityPolicy):
        return density_policy
    try:
        return _HEATMAP_DENSITY_POLICIES[density_policy]
    except KeyError as exc:
        modes = ", ".join(sorted(_HEATMAP_DENSITY_POLICIES))
        raise ValueError(
            f"unknown heatmap density policy {density_policy!r}; expected one of {modes}"
        ) from exc


def _heatmap_density_decision(
    ax: plt.Axes,
    *,
    rows: int,
    cols: int,
    tick_labelsize: float,
    annotation_size: float,
    density_policy: HeatmapDensityPolicy | str | None,
) -> HeatmapDensityDecision:
    policy = _resolve_heatmap_density_policy(density_policy)
    ax.figure.canvas.draw()
    bbox = ax.get_position()
    fig_width_pt, fig_height_pt = ax.figure.get_size_inches() * 72.0
    axes_width_pt = max(fig_width_pt * bbox.width, 0.0)
    axes_height_pt = max(fig_height_pt * bbox.height, 0.0)
    cell_width_pt = axes_width_pt / max(cols, 1)
    cell_height_pt = axes_height_pt / max(rows, 1)

    if policy.mode == "full":
        x_tick_step = 1
        y_tick_step = 1
        show_annotations = True
        show_colorbar_label = True
    else:
        x_tick_step = max(
            1,
            math.ceil(policy.min_x_label_cell_width_pt / max(cell_width_pt, 1e-9)),
        )
        y_tick_step = max(
            1,
            math.ceil(policy.min_y_label_cell_height_pt / max(cell_height_pt, 1e-9)),
        )
        show_annotations = (
            cell_width_pt >= policy.min_annotation_cell_width_pt
            and cell_height_pt >= policy.min_annotation_cell_height_pt
        )
        show_colorbar_label = axes_width_pt >= policy.min_colorbar_label_axes_width_pt

    return HeatmapDensityDecision(
        policy=policy,
        rows=rows,
        cols=cols,
        cell_width_pt=cell_width_pt,
        cell_height_pt=cell_height_pt,
        axes_width_pt=axes_width_pt,
        axes_height_pt=axes_height_pt,
        tick_labelsize=max(4.5, tick_labelsize - policy.tick_labelsize_delta),
        annotation_size=max(4.5, annotation_size - policy.annotation_size_delta),
        show_annotations=show_annotations,
        show_colorbar_label=show_colorbar_label,
        x_tick_step=x_tick_step,
        y_tick_step=y_tick_step,
    )


def _thin_heatmap_labels(labels: Sequence[str], step: int) -> list[str]:
    if step <= 1:
        return [str(label) for label in labels]
    return [str(label) if idx % step == 0 else "" for idx, label in enumerate(labels)]


def _hide_existing_heatmap_annotations(ax: plt.Axes) -> None:
    for text in ax.texts:
        text.set_visible(False)


def _prune_colorbar_ticks_to_norm(cbar: Any) -> None:
    norm = getattr(cbar, "norm", None)
    vmin = getattr(norm, "vmin", None)
    vmax = getattr(norm, "vmax", None)
    if vmin is None:
        vmin = getattr(cbar, "vmin", None)
    if vmax is None:
        vmax = getattr(cbar, "vmax", None)
    if vmin is None or vmax is None:
        return
    ticks = list(cbar.get_ticks())
    visible_ticks = [tick for tick in ticks if vmin <= tick <= vmax]
    if visible_ticks and visible_ticks != ticks:
        cbar.set_ticks(visible_ticks)


def finish_heatmap(
    ax: plt.Axes,
    rows: Sequence[str],
    cols: Sequence[str],
    *,
    x_rotation: float = 45,
    tick_labelsize: float = FONT_SMALL - 1,
    x_ha: str = "right",
    im: Any | None = None,
    colorbar_label: str | None = None,
    colorbar_fraction: float = 0.04,
    colorbar_pad: float = 0.015,
    annotations: Iterable[tuple[int, int, str]] | None = None,
    annotation_size: float = FONT_SMALL - 1,
    bad_color: str | None = None,
    boundary_grid: bool = False,
    boundary_grid_color: str = "#D0D0D0",
    boundary_grid_linewidth: float = 0.6,
    y_label_domain: str | None = None,
    density_policy: HeatmapDensityPolicy | str | None = None,
) -> None:
    """Apply common heatmap ticks, optional annotations, and colorbar styling."""
    decision = _heatmap_density_decision(
        ax,
        rows=len(rows),
        cols=len(cols),
        tick_labelsize=tick_labelsize,
        annotation_size=annotation_size,
        density_policy=density_policy,
    )
    ax._anx_heatmap_density_decision = decision
    row_labels = _thin_heatmap_labels(
        [str(label) for label in rows],
        decision.y_tick_step,
    )
    col_labels = _thin_heatmap_labels(
        [str(col) for col in cols],
        decision.x_tick_step,
    )

    if bad_color and im is not None:
        cmap = getattr(im, "cmap", None)
        if isinstance(cmap, Colormap):
            cmap.set_bad(bad_color)

    ax.grid(False, which="both")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(
        col_labels,
        rotation=x_rotation,
        ha=x_ha,
        fontsize=decision.tick_labelsize,
    )
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(row_labels, fontsize=decision.tick_labelsize)
    ax.tick_params(length=0)
    if boundary_grid:
        ax.set_xticks([idx - 0.5 for idx in range(len(cols) + 1)], minor=True)
        ax.set_yticks([idx - 0.5 for idx in range(len(rows) + 1)], minor=True)
        ax.grid(
            True,
            which="minor",
            color=boundary_grid_color,
            linewidth=boundary_grid_linewidth,
        )
        ax.tick_params(which="minor", bottom=False, left=False)

    if annotations and decision.show_annotations:
        for row, col, text in annotations:
            ax.text(
                col,
                row,
                text,
                ha="center",
                va="center",
                fontsize=decision.annotation_size,
            )

    if im is not None and colorbar_label is not None:
        add_colorbar(
            im,
            ax,
            colorbar_label if decision.show_colorbar_label else "",
            fraction=colorbar_fraction,
            pad=colorbar_pad,
        )


def finish_seaborn_heatmap(
    ax: plt.Axes,
    *,
    x_rotation: float = 45,
    x_ha: str = "right",
    y_rotation: float = 0,
    tick_labelsize: float = FONT_SMALL - 1,
    colorbar_label: str | None = None,
    colorbar_tick_labelsize: float | None = None,
    left: float | None = None,
    right: float | None = None,
    bottom: float | None = None,
    top: float | None = None,
    annotations: Iterable[tuple[float, float, str]] | None = None,
    annotation_size: float = FONT_SMALL - 1,
    annotation_color: str = "black",
    y_label_domain: str | None = None,
    density_policy: HeatmapDensityPolicy | str | None = None,
) -> None:
    """Apply shared styling to a seaborn heatmap after ``sns.heatmap``."""
    if any(value is not None for value in (left, right, bottom, top)):
        mark_exact_margins(ax.figure, left=left, right=right, bottom=bottom, top=top)
    x_labels = [label.get_text() for label in ax.get_xticklabels()]
    ytick_labels = [label.get_text() for label in ax.get_yticklabels()]
    decision = _heatmap_density_decision(
        ax,
        rows=len(ytick_labels),
        cols=len(x_labels),
        tick_labelsize=tick_labelsize,
        annotation_size=annotation_size,
        density_policy=density_policy,
    )
    ax._anx_heatmap_density_decision = decision

    ax.set_xticklabels(
        _thin_heatmap_labels(x_labels, decision.x_tick_step),
        fontsize=decision.tick_labelsize,
        rotation=x_rotation,
        ha=x_ha,
    )
    ax.set_yticklabels(
        _thin_heatmap_labels(
            ytick_labels,
            decision.y_tick_step,
        ),
        fontsize=decision.tick_labelsize,
        rotation=y_rotation,
    )
    ax.tick_params(length=0)

    cbar = ax.collections[-1].colorbar if ax.collections else None
    if cbar is not None:
        _prune_colorbar_ticks_to_norm(cbar)
        if decision.show_colorbar_label and colorbar_label is not None:
            cbar.set_label(colorbar_label, fontsize=FONT_SMALL)
        elif not decision.show_colorbar_label:
            cbar.set_label("")
        cbar.ax.tick_params(
            labelsize=colorbar_tick_labelsize or decision.tick_labelsize
        )

    if not decision.show_annotations:
        _hide_existing_heatmap_annotations(ax)
    elif annotations:
        for x, y, text in annotations:
            ax.text(
                x,
                y,
                text,
                ha="center",
                va="center",
                fontsize=decision.annotation_size,
                color=annotation_color,
            )

    if any(value is not None for value in (left, right, bottom, top)):
        finish_exact_panel(ax, left=left, right=right, bottom=bottom, top=top)


__all__ = [
    "ArtifactCommand",
    "AnnotationCandidate",
    "EndpointLabel",
    "FigureExportSpec",
    "HeatmapDensityDecision",
    "HeatmapDensityPolicy",
    "PanelDrawFn",
    "PanelSpec",
    "RequiredArtifact",
    "add_colorbar",
    "empty_panel",
    "ensure_y_headroom",
    "export_figure",
    "finish_axes",
    "finish_exact_panel",
    "finish_heatmap",
    "mark_exact_margins",
    "panel_mapping",
    "place_axes_annotation",
    "place_data_annotation",
    "place_endpoint_labels_or_legend",
    "require_artifacts",
    "required_data_error",
    "finish_seaborn_heatmap",
]
