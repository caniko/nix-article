{
  lib,
  craneLib,
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
  craneLib.buildPackage (commonArgs
    // {
      inherit cargoArtifacts;
      meta = {
        description = "Article toolchain CLI";
        license = lib.licenses.asl20;
        mainProgram = "anx";
      };
    })
