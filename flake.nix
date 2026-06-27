{
  description = "anx: article toolchain — figure layout, generation, and manuscript building";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    crane = {
      url = "github:ipetkov/crane";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    figurefit = {
      url = "git+https://codeberg.org/caniko/FigureFit.git";
    };
  };

  outputs = {
    self,
    nixpkgs,
    rust-overlay,
    crane,
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

    mkCraneLib = {pkgs, ...}: let
      rustToolchain = pkgs.rust-bin.stable.latest.default.override {
        extensions = ["rust-src" "rustfmt" "clippy"];
      };
    in
      (crane.mkLib pkgs).overrideToolchain rustToolchain;
  in {
    packages = forAllSystems ({pkgs, lib, system}: let
      craneLib = mkCraneLib {inherit pkgs;};

      anx = pkgs.callPackage ./nix/rust.nix {
        inherit lib craneLib;
        figurefit = figurefit.packages.${system}.default;
      };

      anx-plot = pkgs.callPackage ./nix/python.nix {
        inherit lib;
        python3 = pkgs.python314;
      };
    in {
      inherit anx anx-plot;

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

    devShells = forAllSystems ({pkgs, lib, system}: let
      craneLib = mkCraneLib {inherit pkgs;};
      anx = self.packages.${system}.anx;
      anx-plot = pkgs.callPackage ./nix/python.nix {
        inherit lib;
        python3 = pkgs.python314;
      };
    in {
      default = pkgs.callPackage ./nix/dev-shell.nix {
        inherit lib pkgs anx anx-plot;
        figurefit = figurefit.packages.${system}.default;
      };
    });

    lib = forAllSystems ({pkgs, lib, system}: rec {
      figurefitPkg = figurefit.packages.${system}.default;

      mkArticleDevShell = {
        extraPkgs ? [],
        ...
      }:
        pkgs.callPackage ./nix/dev-shell.nix {
          inherit lib pkgs;
          anx = self.packages.${system}.anx;
          anx-plot = pkgs.callPackage ./nix/python.nix {
            inherit lib;
            python3 = pkgs.python314;
          };
          figurefit = figurefitPkg;
        };
    });

    checks = forAllSystems ({pkgs, lib, system}: let
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

      rust-clippy = craneLib.cargoClippy (commonArgs // {
        inherit cargoArtifacts;
        cargoClippyExtraArgs = "--package anx -- --deny warnings";
      });

      rust-doc = craneLib.cargoDoc (commonArgs // {
        inherit cargoArtifacts;
        cargoDocExtraArgs = "--no-deps --package anx";
      });

      python-test = pkgs.runCommand "anx-plot-test" {
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
    });
  };
}
