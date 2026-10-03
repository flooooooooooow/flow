{
  description = "Flow: a statically typed, compiled systems language with a C backend";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAllSystems (pkgs:
        let
          version = builtins.head (pkgs.lib.strings.splitString "\n" (builtins.readFile ./VERSION));
        in
        {
          default = pkgs.stdenv.mkDerivation {
            pname = "flow";
            inherit version;
            src = ./.;

            nativeBuildInputs = [ pkgs.makeWrapper ];

            dontConfigure = true;

            # The `flow` command is a Flow program (tools/flow_cli). Build the
            # bootstrap compiler from the checked-in C, then build the CLI into
            # the layout the `flow` stub expects ($root/build/cli/flow). Nix
            # store mtimes are all epoch 1, so the stub's `find -newer` checks
            # never trigger a rebuild once these artifacts are in place.
            buildPhase = ''
              runHook preBuild
              mkdir -p compiler/build build/cli
              ${pkgs.stdenv.cc}/bin/cc -O2 -w \
                -o compiler/build/flowc_bootstrap \
                compiler/bootstrap/flowc_stage_a.c -lm
              FLOWC_BUNDLE=1 FLOWC_DIR=. FLOWC_TYPECHECK=1 \
                FLOWC_IN=tools/flow_cli/main.flow \
                FLOWC_OUT=build/cli/flow.c \
                ./compiler/build/flowc_bootstrap
              ${pkgs.stdenv.cc}/bin/cc -O1 -w -o build/cli/flow build/cli/flow.c -lm
              runHook postBuild
            '';

            installPhase = ''
              runHook preInstall
              mkdir -p $out/libexec/flow
              cp flow flow-lsp VERSION $out/libexec/flow/
              cp -R lib runtime compiler tools $out/libexec/flow/
              cp -R examples $out/libexec/flow/ || true
              cp -R build $out/libexec/flow/
              chmod +x $out/libexec/flow/flow $out/libexec/flow/flow-lsp

              # The store is read-only, so pin the stub's cache paths at the
              # prebuilt artifacts instead of the user cache fallback.
              substituteInPlace $out/libexec/flow/flow \
                --replace-fail '\[ -w "$root" \] || cache=''${XDG_CACHE_HOME:-$HOME/.cache}/flow' \
                               'cache=$root/build' \
                --replace-fail '\[ -w "$root" \] || boot=$cache/flowc_bootstrap' \
                               'boot=$root/compiler/build/flowc_bootstrap'

              mkdir -p $out/bin
              # `flow run` and friends build into $root/build, which is
              # read-only in the store. Redirect the build root to the user
              # cache; FLOW_BUILD_ROOT stays overridable.
              makeWrapper $out/libexec/flow/flow $out/bin/flow \
                --prefix PATH : ${pkgs.lib.makeBinPath [
                  pkgs.stdenv.cc
                  pkgs.coreutils
                  pkgs.findutils
                ]} \
                --run 'export FLOW_BUILD_ROOT=''${FLOW_BUILD_ROOT:-''${XDG_CACHE_HOME:-$HOME/.cache}/flow/build}'
              # flow-lsp is exec "$SCRIPT_DIR/flow" lsp; wrap the flow stub
              # directly with `lsp` appended so the editor-facing entry point
              # gets the same PATH and build-root fixes.
              makeWrapper $out/libexec/flow/flow $out/bin/flow-lsp \
                --add-flags lsp \
                --prefix PATH : ${pkgs.lib.makeBinPath [
                  pkgs.stdenv.cc
                  pkgs.coreutils
                  pkgs.findutils
                ]} \
                --run 'export FLOW_BUILD_ROOT=''${FLOW_BUILD_ROOT:-''${XDG_CACHE_HOME:-$HOME/.cache}/flow/build}'
              runHook postInstall
            '';

            doInstallCheck = true;
            installCheckPhase = ''
              $out/bin/flow version
            '';

            meta = with pkgs.lib; {
              description = "Statically typed compiled systems language with algebraic effects and a C backend";
              homepage = "https://github.com/flooooooooooow/flow";
              license = licenses.mit;
              platforms = platforms.unix;
              mainProgram = "flow";
            };
          };
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
