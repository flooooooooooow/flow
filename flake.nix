{
  description = "Flow: a statically typed language for systems that evolve through time";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgsFor = system: nixpkgs.legacyPackages.${system};
    in
    {
      packages = forAllSystems (system:
        let
          pkgs = pkgsFor system;
          flow = pkgs.callPackage ./packaging/nix/default.nix { };
        in {
          default = flow;
          flow = flow;
        }
      );

      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/flow";
        };
        flow = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/flow";
        };
      });

      devShells = forAllSystems (system:
        let
          pkgs = pkgsFor system;
        in {
          default = pkgs.mkShell {
            packages = [
              self.packages.${system}.default
              pkgs.python3
              pkgs.python3Packages.numpy
              pkgs.python3Packages.pytest
            ];
          };
        }
      );
    };
}
