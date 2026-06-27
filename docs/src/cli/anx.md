# `anx` — nix-article CLI

## Usage

```
anx [global flags] <command> [arguments...]
```

## Commands

| Command | Description |
|---------|-------------|
| [`anx init`](./init.md) | Scaffold a new article project |
| [`anx layout`](./layout.md) | Figure layout solving and validation |
| [`anx figure`](./figure.md) | Figure generation and assembly |
| [`anx build`](./build.md) | LaTeX compilation |
| [`anx sizes`](./sizes.md) | Font and size TeX file regeneration |

### `anx init`

Scaffold a new article project with default config files and directory structure.

```bash
anx init [dir]
```

See [init reference](./init.md).

### `anx layout`

Solve figure layouts with FigureFit or validate the figure registry.

```bash
anx layout solve [figure]
anx layout check
```

See [layout reference](./layout.md).

### `anx figure`

Export matplotlib panels, compile TikZ to SVG, and assemble composite figures.

```bash
anx figure panels [figure]
anx figure tikz [figure]
anx figure composites [figure]
anx figure all [figure]
```

See [figure reference](./figure.md).

### `anx build`

Compile the LaTeX manuscript or run the full rebuild pipeline.

```bash
anx build compile
anx build rebuild
```

See [build reference](./build.md).

### `anx sizes`

Regenerate font and figure-size TeX files from Python sizing constants.

```bash
anx sizes sync
```

See [sizes reference](./sizes.md).

## Global flags

| Flag | Description |
|------|-------------|
| `-C <dir>`, `--project-dir <dir>` | Run as if started in `<dir>` |
| `--help` | Print help information |
| `--version` | Print version information |
