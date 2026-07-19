{
  lib,
  pkgs,
  anx,
  anx-plot,
  figurefit,
  tex-harbor,
  plinthProject ? null,
  extraPkgs ? [],
}:
tex-harbor.lib.mkTexDevShell {
  inherit pkgs;
  profile = "article";
  extraPackages = with pkgs;
    [
      anx
      anx-plot
      figurefit

      # Python tooling
      uv
      ruff

      # Image processing
      inkscape
      imagemagick

      # Cairo for pycairo
      cairo

      # Documentation
      mdbook
      plinthProject
    ]
    ++ extraPkgs;

  shellArgs = {
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
  };
}
