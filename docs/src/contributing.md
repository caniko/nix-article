# Contributing

## Development Setup

```bash
git clone https://github.com/caniko/nix-article.git
cd nix-article
```

### Nix (recommended)

```bash
nix develop
```

This provides Rust toolchain, Python with `uv`, TeX Live, Inkscape, and `figurefit`.

### Without Nix

```bash
# Rust CLI
cargo build --package anx

# Python package
cd python
uv sync
```

## Project Structure

```
nix-article/
├── src/                     # Rust CLI (anx)
├── python/                  # Python package (anx-plot)
│   └── src/anx_plot/
├── nix/                     # Nix build expressions
│   ├── rust.nix
│   ├── python.nix
│   └── dev-shell.nix
├── plugins/                 # anx-plugin-* packages
│   ├── zenodo/              # anx-plugin-zenodo (Rust)
│   └── pandoc/              # anx-plugin-pandoc (Python)
├── tikz/                    # Shared TikZ infrastructure
├── fixtures/demo-article/   # Testable demo project
├── docs/                    # mdBook documentation
└── flake.nix                # Flake entry point
```

## Testing

```bash
# Rust tests
cargo test --package anx

# Python tests
cd python && uv run pytest

# All checks (Nix)
nix flake check
```

## Code Style

- Rust: `cargo fmt` + `cargo clippy -- --deny warnings`
- Python: `ruff format` + `ruff check`
- Nix: `nix fmt`

## Pull Requests

1. Ensure `nix flake check` passes
2. Add tests for new functionality
3. Update documentation for API changes
4. Keep commits atomic and well-described
