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

    # figurefit is a runtime dependency, not a build one
    postInstall = ''
      mkdir -p $out/bin
      # The anx binary is already installed by cargo
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
