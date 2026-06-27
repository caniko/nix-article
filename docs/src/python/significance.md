# `anx_plot.significance` — Statistical annotation primitives

Functions for formatting and annotating statistical significance on
manuscript figures.

## Formatting

```python
format_pvalue(p: float, *, style: str = "stars") -> str
```
Format a p-value for display. `style="stars"` returns `"***"`/`"**"`/`"*"`/
`"ns"`; `style="text"` returns `"$p < 0.001$"` or `"$p = 0.023$"`.

```python
format_statistic(
    value: float,
    *,
    precision: int = 2,
    fallback: str = "n/a",
) -> str
```
Format a numeric statistic value with given precision.

## Correction

```python
correct_pvalues(
    pvalues: list[float],
    method: str = "holm",
) -> list[float]
```
Apply multiple-comparison correction. Methods: `"holm"` (default),
`"bonferroni"`, `"fdr_bh"` (Benjamini-Hochberg).

## Annotation

```python
significance_bracket(
    ax: plt.Axes,
    x1: float, x2: float, y: float,
    p: float,
    *,
    height: float = 0.02,
    style: str = "stars",
    fontsize: float = FONT_SMALL,
    color: str = GREY_DARK,
    lw: float = 0.8,
) -> None
```
Draw a significance bracket between two x-positions with a star/text label.

```python
annotate_omnibus(
    ax: plt.Axes,
    test_name: str,
    statistic: float,
    p: float,
    *,
    loc: str = "upper right",
    fontsize: float = FONT_SMALL,
    color: str = GREY_DARK,
) -> None
```
Place an omnibus test result as corner text (e.g. `"ANOVA: F=12.3, p<0.001"`).

```python
heatmap_stars(
    ax: plt.Axes,
    p_matrix: np.ndarray,
    *,
    thresholds: tuple[float, ...] = (0.001, 0.01, 0.05),
    fontsize: float = FONT_SMALL,
    color: str = "white",
    offset_y: float = 0.15,
) -> None
```
Overlay significance stars on an existing heatmap.

```python
annotate_regression(
    ax: plt.Axes,
    r_squared: float,
    p: float,
    *,
    loc: str = "upper left",
    fontsize: float = FONT_SMALL,
    color: str = GREY_DARK,
) -> None
```
Place an R² + p-value annotation in a corner.
