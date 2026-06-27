"""CLI entry points for anx-plot Python figure infrastructure."""

from __future__ import annotations

from pathlib import Path

import typer

from anx_plot.sizing import generate_latex_fonts, generate_latex_sizes

app = typer.Typer(name="anx-plot")


@app.command()
def panels(
    prefix: str = typer.Option("CF", help="Figure prefix"),
    output_dir: str = typer.Option("figures/panels", help="Output directory"),
    report: str | None = typer.Option(None, help="Solver report path"),
) -> None:
    """Export matplotlib panels at solver-determined dimensions."""
    from anx_plot.layout import export_panels

    output_path = Path(output_dir)
    report_path = Path(report) if report else None
    # The caller must provide panel_fns; this CLI is typically invoked
    # by the `anx` orchestrator with a Python expression or script.
    typer.echo(f"panels: prefix={prefix}, output={output_dir}")
    if report_path:
        typer.echo(f"  report={report_path}")


@app.command()
def composites(
    prefix: str = typer.Option("CF", help="Figure prefix"),
    output_dir: str = typer.Option("figures/composites", help="Output directory"),
) -> None:
    """Assemble composite figures from individual panels."""
    typer.echo(f"composites: prefix={prefix}, output={output_dir}")


@app.command()
def sync_sizes(
    project_dir: str = typer.Argument(
        ".", help="Project root directory (containing article.toml)"
    ),
) -> None:
    """Regenerate LaTeX size/font constants from Python sizing module."""
    root = Path(project_dir).resolve()

    tikz_dir = root / "tikz"
    tikz_dir.mkdir(parents=True, exist_ok=True)

    fonts_path = tikz_dir / "fonts.tex"
    generate_latex_fonts(fonts_path)
    typer.echo(f"wrote {fonts_path}")

    sizes_path = root / "figure_sizes.tex"
    generate_latex_sizes(sizes_path)
    typer.echo(f"wrote {sizes_path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
