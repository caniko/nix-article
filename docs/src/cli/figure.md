# `anx figure` — Figure generation and assembly

## `anx figure panels [figure]`

Export matplotlib panels at the sizes determined by the FigureFit solver.

Each panel script in `figures/panels/` is run with its target dimensions
(width, height) read from the corresponding `_report.toml`. Output files
land in `figures/panels/` alongside the scripts.

## `anx figure tikz [figure]`

Compile TikZ `.tex` panel files to SVG via LuaLaTeX.

Requires LuaLaTeX with `svg` package support. The generated SVGs are
placed in the build output directory for inclusion in the manuscript.

## `anx figure composites [figure]`

Assemble composite figures from individual panels.

Reads the `<prefix>_layout.tex` output from `anx layout solve` and
produces the final multi-panel figure SVGs.

## `anx figure all [figure]`

Run all figure steps in sequence:

1. `panels` — export matplotlib panels
2. `tikz` — compile TikZ to SVG
3. `composites` — assemble composite figures

### Optional figure argument

If a `figure` name is given, only that figure is processed. When omitted,
all figures are processed.

```bash
# Process all figures
anx figure all

# Process only figure-3
anx figure all figure-3
```
