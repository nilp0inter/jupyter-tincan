{
  description = "Jupyter TinCan Kernel";
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    flake-utils,
    nixpkgs,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      lib = nixpkgs.lib;
    in {
      formatter = pkgs.alejandra;

      devShells.default = pkgs.mkShell rec {
        packages = [
          pkgs.poetry
          pkgs.nodejs
        ];
        shellHook = ''
          export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath packages}:$LD_LIBRARY_PATH"
          export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib.outPath}/lib:$LD_LIBRARY_PATH"
        '';
      };
    });
}
