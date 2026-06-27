# `anx_plot.line_style` — Compact line panel style

Shared style defaults for dense multi-series line charts.

## Style type

```python
@dataclass(frozen=True)
class LinePanelStyle:
    line_width: float = 1.0
    reference_line_width: float = 0.8
    marker_size: float = 2.5
    band_alpha: float = 0.10
    line_alpha: float = 0.85
    grid_alpha: float = 0.15
    tick_labelsize: float = FONT_SMALL - 1
    legend_fontsize: float = FONT_LEGEND - 1
```

## Constants

```python
COMPACT_LINE_STYLE: LinePanelStyle
```
Default instance of `LinePanelStyle()`.

## Functions

```python
plot_series(
    ax: plt.Axes, x: Any, y: Any,
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
    **kwargs,
) -> Any
```
Plot a single data series with compact defaults.

```python
plot_band(
    ax: plt.Axes, x: Any, low: Any, high: Any,
    *,
    color: str,
    style: LinePanelStyle = COMPACT_LINE_STYLE,
    alpha: float | None = None,
    label: str | None = None,
    zorder: int | None = None,
    **kwargs,
) -> Any
```
Plot a filled uncertainty band via `ax.fill_between`.

```python
finish_line_panel(
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
) -> None
```
Apply consistent finishing (log scales, labels, ticks, grid, legend, exact
margins) to a line panel.

```python
compact_legend_kwargs(
    *,
    style: LinePanelStyle = COMPACT_LINE_STYLE,
    **overrides: Any,
) -> dict[str, Any]
```
Return keyword arguments for a compact legend.
