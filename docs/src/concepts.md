# Concepts

The anx toolchain orchestrates a four-stage article production pipeline:

```
sizing → layout → figures → compilation
```

## Project Configuration

Every article has an `article.toml` at its root. This declares the article
name, LaTeX entry point, figure paths, tool binaries, sizing constants, and
plugin configuration. The `anx` CLI searches upward from the current directory
to find it.

## Figure Registry (`figures.toml`)

The registry maps figure slugs to composite numbers, Python modules, and layout
specs. Each entry looks like:

```toml
[architecture]
number = 1
module = "my_figures.fig1_architecture"
layout = "CF01"
```

- **slug** — short identifier (used in CLI filters)
- **number** — composite figure number (e.g. 1 → CF01)
- **module** — Python module path, importable from the project root
- **layout** — basename of the FigureFit spec in `figures/layouts/`

## Layout Solving with FigureFit

FigureFit is a dynamic-programming layout solver that arranges panels into
publication-ready composite figures. Layouts are defined as TOML specs:

```toml
[layout]
width = 160
height = 100

[[groups]]
kind = "flexible"
min_panels = 3

  [[groups.alternatives]]
  [groups.alternatives.A]
  aspect = [1.5, 1.0]

  [[groups.alternatives]]
  [groups.alternatives.A]
  aspect = [1.0, 1.0]
  [groups.alternatives.B]
  aspect = [1.0, 1.0]
  [groups.alternatives.C]
  aspect = [1.0, 1.0]
```

Run the solver:

```console
anx layout solve               # all layouts
anx layout solve CF01          # single figure
```

The solver writes `CF01_report.toml` alongside the spec, containing placed
panel positions and dimensions in millimetres.

## Panel Generation (Python)

Figure panels are matplotlib-based drawing functions. Each panel is a function
`draw(ax: plt.Axes) -> None` that draws into a pre-sized axes. The canonical
module entry point is `export_panels()`:

```python
# my_figures/fig1_architecture.py
from anx_plot.palette import BLUE, RED

def export_panels(output_dir, prefix="CF", **kwargs):
    panel_fns = {
        "A": _draw_overview,
        "B": _draw_detail,
    }
    return _export(panel_fns, output_dir, prefix=prefix)
```

The `anx figure panels` subcommand imports the module and exports each panel
at its solver-determined print size as SVG + PNG.

### anx-plot Library

The Python library provides:

- **`sizing`** — `FIGWIDTH_IN`, font sizes, DPI, `generate_latex_fonts()`
- **`palette`** — Tol Bright colour scheme (colorblind-safe)
- **`helpers`** — `diagram_box()`, `diagram_arrow()`, `bottom_legend()`, label
  margin solvers
- **`layout`** — `export_panels()`, `read_solver_report()`, `apply_style()`
- **`standard`** — `finish_axes()`, `finish_exact_panel()`, `finish_heatmap()`,
  collision-aware annotation placement
- **`export`** — `export_fig()` with SVG/inkscape pipeline, boundary guard
- **`significance`** — p-value formatting, correction, brackets
- **`line_style`** — compact multi-series line chart helpers

## Composite Assembly

After panels are exported, `anx figure composites` assembles individual panel
SVGs into the final composite figure image based on the solver report's
placement data.

## TikZ Compilation

TikZ panels (`.tex` files in `figures/layouts/`) are compiled via `lualatex`
to SVG. This step handles diagram-style panels that benefit from LaTeX
typesetting and the `synbox`/`synarr`/`synlbl` TikZ styles defined in
`tikz/fonts.tex`.

## Size Synchronisation

Sizing constants live in `anx_plot.sizing` (Python) as the single source of
truth. Run `anx sizes sync` to regenerate:

- **`tikz/fonts.tex`** — `\synSmall`, `\synBase`, `\synLabel`, `\synTitle` macros
  and TikZ styles matching Python font sizes
- **`figure_sizes.tex`** — `\linewidth`, `\maxfigheight`, and `\setkeys{Gin}`
  defaults so LaTeX includes figures at native resolution with zero scaling

## LaTeX Compilation

`anx build compile` runs `latexmk -lualatex` on the manuscript. `anx build
rebuild` runs the full pipeline: sync → solve → figures → compile.

## Plugin Architecture

Plugins extend anx with custom behaviour. A plugin is a binary named
`anx-plugin-<name>` on `$PATH`, invoked with `--plugin-context <json>`. See
[Plugins](plugins.md) for details.
