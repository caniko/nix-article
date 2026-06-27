# `anx_plot.layout` — Solver-driven panel export

Reads panel dimensions from FigureFit solver reports and exports panels at
their print-native size.

## Type alias

```python
PanelDrawFn: Callable[[plt.Axes], None]
```

## Functions

```python
apply_style() -> None
```
Apply consistent manuscript styling: Latin Modern Sans, `seaborn-v0_8`
theme, font sizes, colour palette.

```python
read_solver_report(
    report_path: Path,
) -> dict[str, tuple[float, float, float]]
```
Parse a FigureFit TOML report into panel dimensions. Returns
`{panel_id: (width_in, height_in, pad_in)}`.

```python
export_panels(
    panel_fns: Mapping[str, PanelDrawFn],
    output_dir: Path,
    prefix: str = "CF",
    *,
    report: Path | None = None,
) -> list[Path]
```
Export each panel as SVG + PNG at solver-determined dimensions. Panel
letters missing from the solver report are skipped. Returns list of saved
paths.
