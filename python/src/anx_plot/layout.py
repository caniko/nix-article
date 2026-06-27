"""Solver-driven panel export for composite figures.

Reads panel dimensions from ``FigureFit`` solver reports
and exports each panel as SVG + PNG at its exact print size.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from collections.abc import Mapping
from typing import Callable

import matplotlib.pyplot as plt
import seaborn as sns

from anx_plot.export import export_fig

_MM_PER_IN = 25.4


def _register_lm_fonts() -> None:
    """Register Latin Modern fonts from TeX Live with matplotlib."""
    import matplotlib.font_manager as fm

    try:
        result = subprocess.run(
            ["kpsewhich", "lmsans10-regular.otf"],
            capture_output=True,
            text=True,
            check=True,
        )
        font_dir = Path(result.stdout.strip()).parent
        for otf in font_dir.glob("*.otf"):
            fm.fontManager.addfont(str(otf))
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass


def apply_style() -> None:
    """Apply consistent styling for manuscript figures.

    Uses Latin Modern Sans to match the manuscript's ``\\setsansfont``.
    """
    from anx_plot.sizing import (
        DPI_DISPLAY,
        DPI_SAVE,
        FONT_AXIS_LABEL,
        FONT_AXIS_TITLE,
        FONT_BASE,
        FONT_LEGEND,
        FONT_SANS,
        FONT_SANS_FALLBACK,
        FONT_TICK,
    )

    _register_lm_fonts()

    sns.set_theme(style="whitegrid", font_scale=1.0)
    plt.rcParams.update(
        {
            "figure.dpi": DPI_DISPLAY,
            "savefig.dpi": DPI_SAVE,
            "font.family": "sans-serif",
            "font.sans-serif": [FONT_SANS, *FONT_SANS_FALLBACK],
            "mathtext.fontset": "custom",
            "mathtext.rm": FONT_SANS,
            "mathtext.sf": FONT_SANS,
            "mathtext.it": f"{FONT_SANS}:italic",
            "mathtext.bf": f"{FONT_SANS}:bold",
            "mathtext.cal": f"{FONT_SANS}:italic",
            "font.size": FONT_BASE,
            "axes.titlesize": FONT_AXIS_TITLE,
            "axes.labelsize": FONT_AXIS_LABEL,
            "xtick.labelsize": FONT_TICK,
            "ytick.labelsize": FONT_TICK,
            "legend.fontsize": FONT_LEGEND,
        }
    )


# ── Solver report ─────────────────────────────────────────────────────


def read_solver_report(report_path: Path) -> dict[str, tuple[float, float, float]]:
    """Parse a FigureFit solver report into panel dimensions (inches).

    Returns ``{id: (width_in, height_in, pad_in)}`` where *pad_in* is the
    per-side content padding (0 when not specified).
    """
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib

    with open(report_path, "rb") as f:
        report = tomllib.load(f)

    return {
        p["id"]: (
            round(p["w_mm"] / _MM_PER_IN, 3),
            round(p["h_mm"] / _MM_PER_IN, 3),
            round(p.get("pad_mm", 0.0) / _MM_PER_IN, 3),
        )
        for p in report.get("placed", [])
    }


# ── Panel export ──────────────────────────────────────────────────────

PanelDrawFn = Callable[[plt.Axes], None]


def export_panels(
    panel_fns: Mapping[str, PanelDrawFn],
    output_dir: Path,
    prefix: str = "CF",
    *,
    report: Path | None = None,
) -> list[Path]:
    """Export each panel as SVG + PNG at solver-determined dimensions.

    Dimensions are read from the solver report, either passed explicitly
    or auto-discovered at ``<output_dir>/../layouts/<prefix>_report.toml``.
    """
    apply_style()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if report is None:
        candidate = output_dir.parent / "layouts" / f"{prefix}_report.toml"
        if candidate.exists():
            report = candidate

    if report is None:
        msg = f"No solver report found for {prefix}"
        raise FileNotFoundError(msg)

    dims = read_solver_report(report)

    saved: list[Path] = []
    for letter in sorted(panel_fns):
        if letter not in dims:
            print(f"  {letter}  skipped (not placed by {report.name})")
            continue
        draw_fn = panel_fns[letter]
        w, h, pad = dims[letter]

        fig_w = max(w - 2 * pad, 0.5)
        fig_h = max(h - 2 * pad, 0.5)
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        draw_fn(ax)

        stem = output_dir / f"{prefix}_{letter}"
        export_fig(fig, stem)
        svg_path = stem.with_suffix(".svg")
        png_path = stem.with_suffix(".png")
        saved.extend([svg_path, png_path])
        pad_note = f"  (pad {pad:.2f})" if pad > 0 else ""
        print(f"  {letter}  {fig_w:.2f}x{fig_h:.2f} in{pad_note}  ->  {svg_path}")
        plt.close(fig)

    return saved
