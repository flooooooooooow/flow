{
  description = "Flow: a statically typed, compiled systems language with a C backend";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      # The package itself is packaging/nix/default.nix.
      packages = forAllSystems (pkgs: rec {
        flow = pkgs.callPackage ./packaging/nix/default.nix { src = ./.; };
        default = flow;
      });

      apps = forAllSystems (pkgs: {
        default = {
          type = "app";
          program = "${self.packages.${pkgs.system}.default}/bin/flow";
        };
      });

      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = [ pkgs.stdenv.cc ];
        };
      });
    };
}
