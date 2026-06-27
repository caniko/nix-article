{
  lib,
  pkgs,
  anx,
  anx-plot,
  figurefit,
}:
pkgs.mkShell {
  packages = with pkgs; [
    anx
    anx-plot
    figurefit

    # Python tooling
    uv
    ruff

    # LaTeX for manuscript compilation
    (texlive.combine {
      inherit
        (texlive)
        scheme-medium
        biblatex
        biber
        amsmath
        amsfonts
        mathtools
        xcolor
        booktabs
        lm
        lm-math
        hyperref
        bookmark
        xurl
        microtype
        etoolbox
        latexmk
        placeins
        cleveref
        standalone
        svg
        trimspaces
        transparent
        catchfile
        ;
    })

    # Image processing
    inkscape
    imagemagick

    # Cairo for pycairo
    cairo

    # Documentation
    mdbook
  ];

  env = {
    # Make libstdc++ and cairo available for native extensions.
    LD_LIBRARY_PATH = lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.cairo
    ];
  };

  shellHook = ''
    unset PYTHONPATH
    if command -v uv >/dev/null 2>&1 && [ -f pyproject.toml ]; then
      uv sync --frozen 2>/dev/null || uv sync
    fi
    echo "anx article toolchain"
    echo "  anx --help     — CLI help"
    echo "  latexmk        — LaTeX compilation"
    echo "  figurefit      — layout solver"
    echo "  inkscape       — SVG rasterisation"
  '';
}
