{
  lib,
  python3,
  ...
}: let
  py = python3.override {
    packageOverrides = self: super: {
      anx-plot = self.buildPythonPackage rec {
        pname = "anx-plot";
        version = "0.1.0";
        pyproject = true;
        src = lib.fileset.toSource {
          root = ../.;
          fileset = lib.fileset.unions [
            ../pyproject.toml
            ../python/src
          ];
        };

        nativeBuildInputs = [
          super.hatchling
        ];

        propagatedBuildInputs = with super; [
          matplotlib
          seaborn
          numpy
          typer
          pydantic
          pycairo
          scipy
        ];

        meta = {
          description = "Figure generation infrastructure for anx article toolchain";
          license = lib.licenses.asl20;
        };
      };
    };
  };
in
  py.pkgs.anx-plot
