# `anx init` — Scaffold a new article project

## Usage

```bash
anx init [dir]
```

Creates a new nix-article project in `dir` (defaults to the current
directory).

## What it creates

```
dir/
├── article.toml          # Article metadata and build config
├── figures.toml          # Figure registry
└── figures/
    ├── layouts/          # TOML layout specs for FigureFit
    └── panels/           # Matplotlib panel scripts
```

## Defaults

Every config option is populated with a sensible default so the project
compiles out of the box. Edit `article.toml` and `figures.toml` to match
your content.

## Idempotency

`anx init` will **not** overwrite existing files. If `article.toml`
already exists, it is left untouched. Only missing files are created.

## Examples

Scaffold in the current directory:

```bash
anx init
```

Scaffold in a named directory:

```bash
anx init my-paper
```
