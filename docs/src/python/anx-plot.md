# `anx-plot` — Figure generation infrastructure

`anx-plot` provides figure generation infrastructure for the anx article
toolchain. It ships a shared colour palette (Tol Bright, colourblind-safe),
sizing constants (single source of truth between Python and LaTeX), drawing
primitives, solver-driven panel export, and CLI commands.

## Submodules

| Module | Description |
|---|---|
| [`anx_plot.sizing`](sizing.md) | Figure dimensions, font sizes, resolution |
| [`anx_plot.palette`](palette.md) | Paul Tol colour palette and neutrals |
| [`anx_plot.helpers`](helpers.md) | Drawing primitives and layout solvers |
| [`anx_plot.layout`](layout.md) | Solver-driven panel export |
| [`anx_plot.standard`](standard.md) | High-level export framework |
| [`anx_plot.export`](export.md) | SVG+PNG export pipeline |
| [`anx_plot.line_style`](line_style.md) | Compact line panel style defaults |
| [`anx_plot.significance`](significance.md) | Statistical annotation primitives |
| [`anx_plot.cli`](cli.md) | CLI entry points (Typer app) |

## CLI

```text
anx-plot panels     Export matplotlib panels at solver-determined dimensions
anx-plot composites Assemble composite figures from individual panels
anx-plot sync-sizes Regenerate LaTeX size/font constants from Python sizing
```
