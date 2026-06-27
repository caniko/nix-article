# anx — Article Toolchain

**anx** is a toolchain for scientific article figure generation, layout, and
manuscript building. It provides:

- **anx** CLI — orchestrates figure layout solving, panel generation, composite
  assembly, and LaTeX compilation.
- **anx-plot** Python library — shared drawing primitives, sizing, color palettes,
  and export helpers for matplotlib-based figure panels.
- **FigureFit** integration — uses the FigureFit layout solver to arrange panels
  into publication-ready composite figures.
- **Optional plugin system** — extend with custom visual-rubric, pandoc, or
  post-processing plugins.

anx is framework-agnostic. You write your figure panels as Python scripts using
anx-plot helpers; anx handles the build orchestration.
