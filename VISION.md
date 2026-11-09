# anx (nix-article) vision

anx is a toolchain for scientific article figures and manuscript building. The
`anx` CLI orchestrates a four-stage pipeline — sizing, layout, figure generation,
and compilation — from a project's `article.toml`, a figure registry, and
Python panel scripts. A companion Python library, `anx-plot`, supplies sizing,
palettes, line styles, significance annotations, and export helpers for
matplotlib panels, and plugins extend the pipeline for formats such as ODT and
deposits such as Zenodo.

## Problem

A paper's figures are produced by a chain nobody owns: a plotting script, a
layout decision made by hand in Illustrator or by trial and error in LaTeX,
journal size rules applied inconsistently, and a build step glued with shell.
The chain is not reproducible, and changing one panel means redoing the
composition. Manuscript builds add their own toolchain assumptions on top.

## Principles

- **One project file describes the article.** `article.toml` declares the LaTeX
  entry point, figure paths, tool binaries, sizing constants, and plugin
  configuration; the CLI finds it by searching upward.
- **The pipeline has named stages.** Sizing, layout, figures, and compilation are
  separate steps, so a failure points at a stage rather than at "the build".
- **Panels are ordinary Python.** `anx-plot` is a library of primitives, not a
  framework; authors keep writing matplotlib scripts and let anx orchestrate.
- **Layout is solved, not eyeballed.** FigureFit integration arranges panels into
  composite figures according to a layout spec from the registry.
- **Extensions are plugins.** Visual-rubric, pandoc, and post-processing plugins
  plug in rather than being patched into the core.

## Scope

- `anx` CLI: project discovery, stage orchestration, composite assembly, LaTeX
  compilation
- `anx-plot`: sizing, palettes, line styles, significance markers, export helpers
- FigureFit layout integration
- `plugins/zenodo` and `plugins/pandoc`
- mdBook documentation and the project website
- fixture articles and CLI integration tests

## Place in the fleet

Canix's fleet Simit updater covers the repository with both its `anx` and
`anx-plugin-zenodo` Cargo folders, refreshing generated flake and CI
infrastructure with the rest of the fleet, and Atlas maintenance declares cache
targets for those build paths.
