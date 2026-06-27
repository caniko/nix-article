# `anx layout` — Figure layout solving and validation

## `anx layout solve [figure]`

Runs the FigureFit binary on the TOML layout specs under
`figures/layouts/`.

### Output

For each layout spec `<prefix>.toml`, generates:

- `<prefix>_report.toml` — solver results and panel dimensions
- `<prefix>_layout.tex` — TikZ code for the composite figure

### Optional figure argument

If a `figure` name is given, only the layout spec matching that figure is
solved. When omitted, all layout specs are solved.

```bash
# Solve all figures
anx layout solve

# Solve only figure-3
anx layout solve figure-3
```

## `anx layout check`

Validates the figure registry in `figures.toml`.

### Checks performed

- Every figure referenced in `figures.toml` has a corresponding layout
  spec in `figures/layouts/`.
- Every layout spec has a generated `_report.toml` from a prior solve.

Exits with a non-zero status and lists all problems found.
