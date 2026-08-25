{
  description = "anx: article toolchain — figure layout, generation, and manuscript building";

  inputs = {
    rs-harbor.url = "git+https://github.com/caniko/rs-harbor.git?ref=trunk&rev=05cc4f162b55fa904b687db1821e2463fa813e50";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    tex-harbor = {
      url = "git+https://github.com/caniko/harbor-tex.git?ref=trunk";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    crane = {
      url = "github:ipetkov/crane";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    plinth = {
      url = "git+https://github.com/caniko/plinth.git";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    figurefit = {
      url = "git+https://github.com/caniko/FigureFit.git";
    };
  };

  outputs = {
    self,
    rs-harbor,
    nixpkgs,
    tex-harbor,
    rust-overlay,
    crane,
    plinth,
    figurefit,
  }: let
    systems = ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin"];

    forAllSystems = f:
      nixpkgs.lib.genAttrs systems (system:
        f {
          inherit system;
          pkgs = import nixpkgs {
            inherit system;
            overlays = [rust-overlay.overlays.default];
          };
          lib = nixpkgs.lib;
        });

    mkCraneLib = {pkgs, ...}:
      (rs-harbor.lib.mkToolchain { inherit pkgs; toolchainProfile = "stable"; }).craneLib;
  in {
    packages = forAllSystems ({
      pkgs,
      lib,
      system,
    }: let
      craneLib = mkCraneLib {inherit pkgs;};
      buildCache = rs-harbor.lib.mkBuildCachePolicy {
        inherit pkgs;
        sccachePackage =
          if builtins.hasAttr system rs-harbor.packages
          then rs-harbor.packages.${system}.sccache
          else pkgs.sccache;
        cacheRoot = null;
        namespaceScope = "canix-rust";
        namespaceGeneration = 5;
      };

      anx = pkgs.callPackage ./nix/rust.nix {
        inherit lib craneLib buildCache;
        figurefit = figurefit.packages.${system}.default;
      };

      anx-plot = pkgs.callPackage ./nix/python.nix {
        inherit lib;
        python3 = pkgs.python314;
      };

      pluginSrc = lib.fileset.toSource {
        root = ./.;
        fileset = lib.fileset.unions [
          ./Cargo.toml
          ./Cargo.lock
          ./plugins/zenodo
        ];
      };

      anx-plugin-zenodo = let
        pcommon = {
          pname = "anx-plugin-zenodo";
          version = "0.1.0";
          src = craneLib.cleanCargoSource pluginSrc;
          strictDeps = true;
          buildInputs = [pkgs.openssl];
          nativeBuildInputs = [pkgs.pkg-config];
          cargoExtraArgs = "--package anx-plugin-zenodo";
        };
        cargoArtifacts = craneLib.buildDepsOnly pcommon;
      in
        buildCache.withRustCache {
          package = craneLib.buildPackage (pcommon
            // {
              inherit cargoArtifacts;
              meta.mainProgram = "anx-plugin-zenodo";
            });
        };

      anx-plugin-pandoc = pkgs.python314.pkgs.buildPythonPackage {
        pname = "anx-plugin-pandoc";
        version = "0.1.0";
        pyproject = true;
        src = ./plugins/pandoc;
        nativeBuildInputs = [pkgs.python314.pkgs.hatchling];
        meta.description = "Pandoc ODT export plugin for anx";
      };
      docs = pkgs.stdenvNoCC.mkDerivation {
        pname = "anx-docs";
        version = "0.1.0";
        src = lib.fileset.toSource {
          root = ./.;
          fileset = lib.fileset.unions [
            ./docs/book.toml
            ./docs/src
          ];
        };
        nativeBuildInputs = [pkgs.mdbook];
        dontUnpack = true;
        buildPhase = ''
          cp -r --no-preserve=mode $src/. .
          chmod -R +w .
          mdbook build docs --dest-dir docs-book
        '';
        installPhase = ''
          mkdir -p $out
          cp -r docs-book/. $out/
        '';
      };

      plinthProject = plinth.packages.${system}.plinth-project;

      projectSite = pkgs.stdenvNoCC.mkDerivation {
        pname = "anx-site";
        version = "0.1.0";
        src = ./website;
        nativeBuildInputs = [plinthProject];
        buildPhase = ''
          plinth-project build --config plinth-project.toml --out public
        '';
        installPhase = ''
          mkdir -p $out
          cp -r public/. $out/
        '';
      };

      site = pkgs.stdenvNoCC.mkDerivation {
        pname = "anx-site";
        version = "0.1.0";
        src = lib.fileset.toSource {
          root = ./.;
          fileset = lib.fileset.unions [
            ./website
            ./docs/book.toml
            ./docs/src
          ];
        };
        nativeBuildInputs = [plinthProject pkgs.mdbook];
        buildPhase = ''
          plinth-project build --config website/plinth-project.toml --out public
          mdbook build docs --dest-dir docs-book
        '';
        installPhase = ''
          mkdir -p $out
          cp -r public/. $out/
          mkdir -p $out/docs
          cp -r docs-book/. $out/docs/
        '';
      };
    in {
      inherit anx anx-plot anx-plugin-zenodo anx-plugin-pandoc docs site projectSite;

      figurefit = figurefit.packages.${system}.default;

      default = pkgs.symlinkJoin {
        name = "anx-toolchain";
        paths = [
          anx
          anx-plot
          figurefit.packages.${system}.default
        ];
        nativeBuildInputs = [pkgs.makeWrapper];
        postBuild = let
          pythonPath = "${anx-plot}/${pkgs.python314.sitePackages}";
        in ''
          wrapProgram $out/bin/anx \
            --set PYTHONPATH "${pythonPath}:$PYTHONPATH"
        '';
      };
    });

    devShells = forAllSystems ({
      pkgs,
      lib,
      system,
    }: let
      craneLib = mkCraneLib {inherit pkgs;};
      anx = self.packages.${system}.anx;
      anx-plot = pkgs.callPackage ./nix/python.nix {
        inherit lib;
        python3 = pkgs.python314;
      };
    in {
      default = pkgs.callPackage ./nix/dev-shell.nix {
        inherit lib pkgs anx anx-plot tex-harbor;
        figurefit = figurefit.packages.${system}.default;
        plinthProject = plinth.packages.${system}.plinth-project;
      };
    });

    lib = forAllSystems ({
      pkgs,
      lib,
      system,
    }: rec {
      figurefitPkg = figurefit.packages.${system}.default;

      mkArticleDevShell = {extraPkgs ? [], ...}:
        pkgs.callPackage ./nix/dev-shell.nix {
          inherit lib pkgs tex-harbor extraPkgs;
          anx = self.packages.${system}.anx;
          anx-plot = pkgs.callPackage ./nix/python.nix {
            inherit lib;
            python3 = pkgs.python314;
          };
          figurefit = figurefitPkg;
        };
    });

    checks = forAllSystems ({
      pkgs,
      lib,
      system,
    }: let
      craneLib = mkCraneLib {inherit pkgs;};

      commonArgs = {
        src = craneLib.cleanCargoSource ./.;
        strictDeps = true;
        buildInputs = [];
        nativeBuildInputs = [];
      };

      cargoArtifacts = craneLib.buildDepsOnly commonArgs;
    in {
      rust-fmt = craneLib.cargoFmt {
        src = craneLib.cleanCargoSource ./.;
      };

      rust-clippy = craneLib.cargoClippy (commonArgs
        // {
          inherit cargoArtifacts;
          cargoClippyExtraArgs = "--package anx -- --deny warnings";
        });

      rust-doc = craneLib.cargoDoc (commonArgs
        // {
          inherit cargoArtifacts;
          cargoDocExtraArgs = "--no-deps --package anx";
        });

      python-test =
        pkgs.runCommand "anx-plot-test" {
          buildInputs = [
            (pkgs.callPackage ./nix/python.nix {
              inherit lib;
              python3 = pkgs.python314;
            })
            pkgs.python314
          ];
        } ''
          python -c "import anx_plot; print('anx-plot import OK')"
          touch $out
        '';

      pandoc-plugin-test =
        pkgs.runCommand "pandoc-plugin-test" {
          buildInputs = [self.packages.${system}.anx-plugin-pandoc];
        } ''
          python -c "from anx_plugin_pandoc import main; print('import OK')"
          touch $out
        '';
    });

    apps = forAllSystems ({
      pkgs,
      lib,
      system,
    }: {
      deploy-pages = plinth.lib.${system}.mkDeployPagesApp {
        domain = "nix-article.tartanoglu.com";
      };
    });
  };
}
