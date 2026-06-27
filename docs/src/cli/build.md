# `anx build` — LaTeX compilation

## `anx build compile`

Incremental LaTeX compilation via `latexmk`.

Runs `latexmk` with the project's primary `.tex` file, automatically
resolving bibliography, cross-references, and index passes. Only
recompiles what has changed since the last run.

## `anx build rebuild`

Full pipeline from scratch. Runs the following steps in order:

1. **`anx sizes sync`** — regenerate font and figure-size TeX files
2. **`anx layout solve`** — solve all figure layouts
3. **`anx figure all`** — export panels, compile TikZ, assemble composites
4. **`anx build compile`** — final LaTeX compilation

```bash
# Incremental compile
anx build compile

# Full rebuild from scratch
anx build rebuild
```

Use `compile` during active writing and `rebuild` when layout or figure
definitions have changed.
