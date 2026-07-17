{
  lib,
  craneLib,
  buildCache,
  figurefit,
  ...
}: let
  commonArgs = {
    pname = "anx";
    version = "0.1.0";
    src = lib.fileset.toSource {
      root = ../.;
      fileset = lib.fileset.unions [
        ../Cargo.toml
        ../Cargo.lock
        ../src
        ../plugins/zenodo
      ];
    };
    strictDeps = true;
    buildInputs = [];
    nativeBuildInputs = [];
    cargoExtraArgs = "--package anx";

    postInstall = ''
      mkdir -p $out/bin
    '';
  };

  cargoArtifacts = craneLib.buildDepsOnly commonArgs;
in
  buildCache.withRustCache {
    package = craneLib.buildPackage (commonArgs
      // {
        inherit cargoArtifacts;
        meta = {
          description = "Article toolchain CLI";
          license = lib.licenses.asl20;
          mainProgram = "anx";
        };
      });
  }
