# `anx_plot.sizing` — Figure dimensions and font sizes

Single source of truth for figure geometry, font sizes, and resolution,
shared between Python figure generation and LaTeX via `generate_latex_*`.

## Page geometry

```python
PAGE_WIDTH_MM: float       # 210 (A4)
PAGE_HEIGHT_MM: float      # 297 (A4)
MARGIN_MM: float           # 25
LINEWIDTH_MM: float        # PAGE_WIDTH_MM - 2 * MARGIN_MM (160)
TEXTHEIGHT_MM: float       # PAGE_HEIGHT_MM - 2 * MARGIN_MM (247)
LINEWIDTH_IN: float        # LINEWIDTH_MM / 25.4
TEXTHEIGHT_IN: float       # TEXTHEIGHT_MM / 25.4
FIGWIDTH_IN: float         # LINEWIDTH_IN
SCALE: float               # 1.0
MAX_FIG_HEIGHT_IN: float   # (TEXTHEIGHT_MM - 31.0) / 25.4
```

## Resolution

```python
DPI_SAVE: int              # 300
DPI_DISPLAY: int           # 150
```

## Font families

```python
FONT_MAIN: str             # "Latin Modern Roman"
FONT_SANS: str             # "Latin Modern Sans"
FONT_MONO: str             # "Latin Modern Mono"
FONT_SANS_FALLBACK: list   # ["LM Sans 10", "Inter", "Helvetica", "Arial"]
```

## Font sizes

```python
FONT_SMALL: float          # 7.0 pt
FONT_BASE: float           # 8.0 pt
FONT_LABEL_AXIS: float     # 9.0 pt
FONT_BIG: float            # 10.0 pt
FONT_PANEL: float          # 14.0 pt
FONT_TICK: float           # alias for FONT_SMALL
FONT_LEGEND: float         # alias for FONT_SMALL
FONT_AXIS_LABEL: float     # alias for FONT_LABEL_AXIS
FONT_AXIS_TITLE: float     # alias for FONT_BIG
```

## Layout

```python
SUBPLOT_ADJUST: dict       # {top=0.94, bottom=0.04, left=0.08, right=0.98}
```

## Functions

```python
constrained_figsize(
    n_rows: int,
    row_height_in: float = 2.5,
    hspace_frac: float = 0.15,
) -> tuple[float, float]
```
Compute a figsize that fits within a single A4 page.

```python
generate_latex_fonts(output_path: Path | str) -> None
```
Write `fonts.tex` defining `\synSmall` … `\synTitle` macros and shared TikZ
styles (`syndb`, `synbox`, `synarr`, `synlbl`).

```python
generate_latex_sizes(output_path: Path | str) -> None
```
Write `figure_sizes.tex` setting `\setkeys{Gin}` defaults and
`\maxfigheight` in sync with Python constants.
