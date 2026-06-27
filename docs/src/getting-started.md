# Getting Started

## Installation

### Nix Flake (recommended)

```console
nix develop github:caniko/nix-article
```

This provides `anx`, `anx-plot`, `figurefit`, `latexmk`, `inkscape`, and all
Python/LaTeX dependencies in a single shell.

To use anx in an existing article project's `flake.nix`:

```nix
{
  inputs = {
    nix-article.url = "github:caniko/nix-article";
  };

  outputs = { nix-article, ... }: {
    devShells.x86_64-linux.default =
      nix-article.lib.x86_64-linux.mkArticleDevShell { };
  };
}
```

### Cargo

```console
cargo install anx
```

The CLI binary is installed as `anx`. You will also need `anx-plot` (Python),
`figurefit`, `latexmk`, and `lualatex` available separately.

### Python (anx-plot library only)

```console
uv add anx-plot
```

Installs the `anx_plot` Python package with drawing primitives, sizing,
colour palette, and export helpers.

## Quick Start

Scaffold a new article project:

```console
anx init my-article
cd my-article
```

This creates:

```
my-article/
  article.toml         # Project configuration
  figures.toml         # Figure registry
  figures/
    layouts/            # FigureFit layout specs
    panels/             # Generated panel SVGs/PNGs
```

Build everything:

```console
anx build rebuild
```

This runs the full pipeline:
1. `anx sizes sync` — generate `fonts.tex` and `figure_sizes.tex` from Python
   sizing constants
2. `anx layout solve` — run FigureFit on all layout TOMLs
3. `anx figure all` — export matplotlib panels, compile TikZ, assemble composites
4. `anx build compile` — compile the LaTeX manuscript

## Next Steps

- Read the [Concepts](concepts.md) guide for the article lifecycle
- See [Configuration](configuration.md) for the `article.toml` schema
- Browse the [anx CLI Reference](cli/anx.md) for subcommands
