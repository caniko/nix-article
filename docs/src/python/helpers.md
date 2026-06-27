# `anx_plot.helpers` — Drawing primitives and layout solvers

Shared drawing primitives for composite manuscript figures. All diagram
coordinates are in normalized axes space `[0, 1]`.

## Diagram primitives

```python
diagram_box(
    ax: plt.Axes,
    x: float, y: float, w: float, h: float,
    color: str,
    *,
    label: str = "", sublabel: str = "",
    ec: str = "black", lw: float = 1.2, alpha: float = 1.0, ls: str = "-",
    label_color: str = "white",
    sublabel_color: str | None = None,
    label_size: float = FONT_BASE, sublabel_size: float = FONT_SMALL,
    pad: float = 0.01, zorder: int = 1,
) -> None
```
Draw a rounded rectangle with optional centred label and sublabel.

```python
diagram_arrow(
    ax: plt.Axes,
    x1: float, y1: float, x2: float, y2: float,
    *,
    color: str = GREY_MID, lw: float = 1.0, style: str = "->",
    ms: int = 8, ls: str = "-", zorder: int = 2,
    **kw,
) -> None
```
Draw a `FancyArrowPatch` between two data-coordinate points.

```python
label_badge(
    ax: plt.Axes,
    x: float, y: float, text: str,
    *,
    fontsize: float = FONT_BASE, color: str = DARK,
    **kw,
) -> None
```
Small labelled badge (white background, grey border).

## Label abbreviation

```python
abbreviate_label(value: object, domain: str | None = None) -> str
```
Return a registered abbreviation for `value`; preserve unknowns as-is.

```python
abbreviate_labels(values, domain: str | None = None) -> list[str]
```
Batch abbreviation of labels.

## Layout solvers

```python
solve_left_label_margin(
    ax: plt.Axes,
    *,
    min_canvas_margin_pt: float = 2.0,
    max_left: float | None = None,
    min_axes_width: float = 0.05,
) -> None
```
Iteratively expand `left` margin so y-axis labels fit inside the figure
canvas.

```python
solve_bottom_axis_margin(
    ax: plt.Axes,
    *,
    min_canvas_margin_pt: float = 2.0,
    max_bottom: float | None = None,
) -> None
```
Adjust `bottom` margin so x-axis labels fit inside the canvas.

```python
bottom_legend(
    ax: plt.Axes,
    *,
    ncol: int = 2, left: float = 0.18, right: float = 0.98,
    min_gap_pt: float = 8.0, min_canvas_margin_pt: float = 2.0,
    handles=None, labels=None,
    **legend_kw,
) -> None
```
Place a legend centred below the axes, auto-solving minimal bottom margin.

## Diagnostics

```python
check_figure_clipping(
    fig: plt.Figure,
    *,
    tol: float = 0.01,
) -> list[str]
```
Check whether any visible artist is clipped by the figure boundary. Returns
warning strings (empty if clean).
