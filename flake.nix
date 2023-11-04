{
  description = "A synapse module for creating anonymous class section-specific channels";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    navigate = pkgs.python311Packages.buildPythonPackage {
      pname = "navigate"; # TODO
      version = "0.1.0";
      pyproject = true;
      src = ./.;
      buildInputs = [pkgs.matrix-synapse-unwrapped];
      pythonImportsCheck = ["navigate"];
      doCheck = false;
    };
  in {
    packages.${system}.default = navigate;

    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [navigate];
    };
  };
}
