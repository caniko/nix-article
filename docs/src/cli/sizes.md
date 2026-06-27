# `anx sizes` — Font and figure-size TeX regeneration

## `anx sizes sync`

Regenerates the `fonts.tex` and `figure_sizes.tex` files from Python
sizing constants.

### Source of truth

All font dimensions and figure size constants are defined in Python
modules. `anx sizes sync` reads these Python values and emits
corresponding LaTeX `\def` macros so the manuscript typesetting matches
the sizing used during figure generation.

### Generated files

| File | Contents |
|------|----------|
| `fonts.tex` | Font size macros (text, footnotes, captions, etc.) |
| `figure_sizes.tex` | Figure dimensions (panel widths, heights, gaps) |

### When to run

Run after changing any sizing constant in Python. This is done
automatically as part of `anx build rebuild`.

```bash
anx sizes sync
```
