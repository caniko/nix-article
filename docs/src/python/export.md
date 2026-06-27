# `anx_plot.export` — SVG+PNG export pipeline

Saves figures as SVG + rasterized PNG with pre-export boundary guard.

## Exceptions

```python
class ExportBoundaryError(RuntimeError):
    ...
```
Raised when exact-size export would clip publication-relevant artists.

## Violation type

```python
@dataclass(frozen=True)
class ExportBoundaryViolation:
    artist: str
    sides: tuple[str, ...]
    gaps_pt: dict[str, float]
    required_margin_pt: float
    def describe(self) -> str
```
A rendered artist that touches or crosses the fixed export canvas.

## Functions

```python
allow_export_boundary_clip(
    artist: Artist,
    reason: str,
) -> Artist
```
Mark an artist as intentionally allowed to cross the export boundary.

```python
measure_export_boundary_violations(
    fig: plt.Figure,
    *,
    safety_margin_pt: float = 1.0,
) -> list[ExportBoundaryViolation]
```
Measure visible publication artists against the rendered canvas.

```python
validate_export_boundary(
    fig: plt.Figure,
    *,
    safety_margin_pt: float = 1.0,
    context: str | None = None,
) -> None
```
Fail with `ExportBoundaryError` if exact-size export would place visible
artists on the boundary.

```python
export_fig(
    fig: plt.Figure,
    stem: Path | None,
    *,
    pad_inches: float = 0.04,
) -> plt.Figure
```
Save figure as SVG + PNG if `stem` is provided; else return unchanged. PNG
is rasterized from SVG via Inkscape (with matplotlib fallback). When
`fig._tight_bbox` is `False`, tight bbox is disabled to preserve exact
figsize.
