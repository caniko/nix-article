# Configuration

The `article.toml` file is the project manifest. It is searched upward from the
current directory.

## `[article]` Section

```toml
[article]
name = "my-article"
tex-main = "manuscript.tex"
```

| Key        | Default            | Description                        |
| ---------- | ------------------ | ---------------------------------- |
| `name`     | `"article"`        | Project name                       |
| `tex-main` | `"manuscript.tex"` | Path to the main LaTeX file        |

## `[figures]` Section

```toml
[figures]
registry = "figures.toml"
layouts = "figures/layouts"
panels = "figures/panels"
composites = "figures/composites"
```

| Key          | Default               | Description                            |
| ------------ | --------------------- | -------------------------------------- |
| `registry`   | `"figures.toml"`      | Figure registry file                   |
| `layouts`    | `"figures/layouts"`   | Directory for FigureFit layout TOMLs   |
| `panels`     | `"figures/panels"`    | Output directory for generated panels  |
| `composites` | `"figures/composites"`| Output directory for composites        |

## `[tools]` Section

```toml
[tools]
figurefit = "figurefit"
python = "uv run python"
latexmk = "latexmk"
lualatex = "lualatex"
```

| Key         | Default             | Description                         |
| ----------- | ------------------- | ----------------------------------- |
| `figurefit` | `"figurefit"`       | FigureFit binary path or name       |
| `python`    | `"uv run python"`   | Python interpreter command          |
| `latexmk`   | `"latexmk"`         | latexmk command                     |
| `lualatex`  | `"lualatex"`        | lualatex command                    |

## `[sizing]` Section

```toml
[sizing]
page-width-mm = 210
page-height-mm = 297
margin-mm = 25
font-main = "Latin Modern Roman"
font-sans = "Latin Modern Sans"
font-mono = "Latin Modern Mono"
font-small = 7.0
font-base = 8.0
font-label-axis = 9.0
font-big = 10.0
font-panel = 14.0
```

| Key               | Default                | Description                      |
| ----------------- | ---------------------- | -------------------------------- |
| `page-width-mm`   | `210`                  | Page width in mm                 |
| `page-height-mm`  | `297`                  | Page height in mm                |
| `margin-mm`       | `25`                   | Margin in mm                     |
| `font-main`       | `"Latin Modern Roman"` | Serif font family                |
| `font-sans`       | `"Latin Modern Sans"`  | Sans-serif font family           |
| `font-mono`       | `"Latin Modern Mono"`  | Monospace font family            |
| `font-small`      | `7.0`                  | Small font size (pt)             |
| `font-base`       | `8.0`                  | Base font size (pt)              |
| `font-label-axis` | `9.0`                  | Axis label font size (pt)        |
| `font-big`        | `10.0`                 | Title/large font size (pt)       |
| `font-panel`      | `14.0`                 | Panel letter font size (pt)      |

These values match the constants in `anx_plot.sizing` and are the single source
of truth. Run `anx sizes sync` to regenerate `tikz/fonts.tex` and
`figure_sizes.tex` from these settings.

## `[plugins]` Section

```toml
[plugins]
enabled = ["zenodo", "pandoc"]
```

| Key       | Default | Description                       |
| --------- | ------- | --------------------------------- |
| `enabled` | `[]`    | List of plugin names to activate  |

Each name must correspond to an `anx-plugin-<name>` binary on `$PATH`. See
[Plugins](plugins.md) for details.

## Example

Minimal complete configuration:

```toml
[article]
name = "my-article"
tex-main = "manuscript.tex"

[figures]
registry = "figures.toml"
layouts = "figures/layouts"
panels = "figures/panels"
composites = "figures/composites"

[tools]
figurefit = "figurefit"
python = "uv run python"
latexmk = "latexmk"
lualatex = "lualatex"
```

All sections are optional — missing values fall back to the defaults shown
above.
