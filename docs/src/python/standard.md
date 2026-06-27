# `anx_plot.standard` — High-level figure export framework

Declarative export contracts, panel specs, required-artifact validation,
heatmap density policies, and common chart finishing for manuscript figures.

## Spec types

```python
@dataclass(frozen=True)
class PanelSpec:
    letter: str
    draw: PanelDrawFn
    required: bool = True
```

```python
@dataclass(frozen=True)
class ArtifactCommand:
    argv: tuple[str, ...]
    def render(self) -> str
```
A shell command stored as argv (diagnostics only).

```python
@dataclass(frozen=True)
class RequiredArtifact:
    path: Path
    description: str
    producer: str
    regenerate: ArtifactCommand
    validate: ArtifactCommand
```
A production data dependency required before exporting.

```python
@dataclass(frozen=True)
class FigureExportSpec:
    prefix: str
    panels: Mapping[str, PanelDrawFn] | Iterable[PanelSpec]
    required_artifacts: Iterable[RequiredArtifact] = ()
```
Declarative export contract for a registered manuscript figure.

## Heatmap density types

```python
@dataclass(frozen=True)
class HeatmapDensityPolicy:
    mode: str = "full"
    min_annotation_cell_width_pt: float = 8.0
    min_annotation_cell_height_pt: float = 6.0
    min_x_label_cell_width_pt: float = 6.0
    min_y_label_cell_height_pt: float = 5.0
    # ... +tick_labelsize_delta, annotation_size_delta
```
Print-size policy for dense heatmaps — thin labels/annotations when cells
are too small.

```python
@dataclass(frozen=True)
class HeatmapDensityDecision:
    policy: HeatmapDensityPolicy
    rows: int; cols: int
    cell_width_pt: float; cell_height_pt: float
    tick_labelsize: float; annotation_size: float
    show_annotations: bool; show_colorbar_label: bool
    x_tick_step: int; y_tick_step: int
```
Resolved choices for one rendered heatmap axes.

## Annotation types

```python
@dataclass(frozen=True)
class AnnotationCandidate:
    x: float; y: float
    ha: str = "left"; va: str = "bottom"
    dx_pt: float = 0.0; dy_pt: float = 0.0
```
Deterministic candidate for collision-aware annotation placement.

```python
@dataclass(frozen=True)
class EndpointLabel:
    x: float; y: float; text: str; color: str
```
Line endpoint label candidate in data coordinates.

## Figure lifecycle

```python
required_data_error(
    message: str,
    *,
    artifact: Path | str,
    description: str,
    producer: str,
    regenerate: ArtifactCommand | tuple[str, ...] | str,
    validate: ArtifactCommand | tuple[str, ...] | str,
) -> RuntimeError
```
Create a standard required-data failure error.

```python
require_artifacts(artifacts: Iterable[RequiredArtifact]) -> None
```
Fail with a descriptive error if any required artifact is missing.

```python
panel_mapping(
    panels: Mapping[str, PanelDrawFn] | Iterable[PanelSpec],
) -> dict[str, PanelDrawFn]
```
Normalize panel declarations to the mapping expected by FigureFit export.

```python
export_figure(
    spec: FigureExportSpec,
    output_dir: Path,
    *,
    prefix: str | None = None,
) -> list[Path]
```
Validate required inputs and export a standardized figure spec.

```python
mark_exact_margins(
    fig: plt.Figure,
    *,
    left: float | None = None, right: float | None = None,
    bottom: float | None = None, top: float | None = None,
) -> None
```
Apply fixed margins and opt into exact export boundary validation.

```python
finish_exact_panel(
    ax: plt.Axes,
    *,
    left: float | None = None, right: float | None = None,
    bottom: float | None = None, top: float | None = None,
) -> None
```
Apply fixed panel margins for export-size-sensitive panels. Calls
`mark_exact_margins` + `solve_left_label_margin` + `solve_bottom_axis_margin`.

## Chart finishing

```python
empty_panel(
    ax: plt.Axes,
    message: str,
    *,
    fontsize: float = FONT_SMALL,
    color: str = "#666666",
) -> None
```
Render the standard diagnostic empty panel (centred text, axes off).

```python
add_colorbar(
    im: Any,
    ax: plt.Axes,
    label: str,
    *,
    fraction: float = 0.04,
    pad: float = 0.015,
    labelsize: float = FONT_SMALL,
    tick_labelsize: float | None = None,
) -> Any
```
Attach a consistently styled vertical colorbar to a panel.

```python
finish_axes(
    ax: plt.Axes,
    *,
    x_label: str | None = None,
    y_label: str | None = None,
    grid_axis: str | None = "y",
    grid_alpha: float = 0.25,
    legend: bool = False,
    legend_loc: str = "best",
    bottom_legend_cols: int | None = None,
) -> None
```
Apply common manuscript chart finishing (labels, grid, tick params, legend).

## Annotation placement

```python
place_axes_annotation(
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
    **text_kw,
) -> Artist | None
```
Place axes-corner text at the first non-colliding deterministic candidate.

```python
place_data_annotation(
    ax: plt.Axes,
    text: str,
    xy: tuple[float, float],
    *,
    candidates: Sequence[AnnotationCandidate] = ...,
    avoid_artists: Sequence[Artist] = (),
    avoid_bboxes: Sequence[Bbox] = (),
    fontsize: float = FONT_SMALL,
    color: str = "#555555",
    min_margin_pt: float = 1.0,
    required: bool = False,
    arrow: bool = False,
    **text_kw,
) -> Artist | None
```
Place data-anchored text using deterministic offset candidates.

```python
place_endpoint_labels_or_legend(
    ax: plt.Axes,
    labels: Sequence[EndpointLabel],
    *,
    max_inline: int = 5,
    max_legend_items: int = 8,
    legend_title: str | None = None,
    fontsize: float = FONT_SMALL,
) -> str
```
Place endpoint labels or fall back to a compact legend when too dense.
Returns `"inline"` or `"legend"`.

```python
ensure_y_headroom(
    ax: plt.Axes,
    values: Sequence[float],
    *,
    fraction: float = 0.16,
) -> None
```
Expand the y-axis upper limit so marker/endpoint annotations have room.

## Heatmap finishing

```python
finish_heatmap(
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
) -> None
```
Apply heatmap ticks, optional annotations, and colorbar styling with
density-aware thinning.

```python
finish_seaborn_heatmap(
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
) -> None
```
Apply shared styling to a seaborn heatmap after `sns.heatmap`.
