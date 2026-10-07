# The Flow package for Nix. The root flake.nix and packaging/nix/flake.nix
# both call this file, so there is one package definition.
{ pkgs ? import <nixpkgs> {}, src ? ../.. }:

let
  version = pkgs.lib.removeSuffix "\n" (builtins.readFile "${src}/VERSION");
  # `flow` shells out to cc, find and the coreutils at run time.
  runtimePath = pkgs.lib.makeBinPath [ pkgs.stdenv.cc pkgs.coreutils pkgs.findutils ];
in
pkgs.stdenv.mkDerivation {
  pname = "flow";
  inherit version src;

  nativeBuildInputs = [ pkgs.makeWrapper ];

  dontConfigure = true;

  # The `flow` command is a Flow program (tools/flow_cli). Build the
  # bootstrap compiler from the checked-in C, then build the CLI into the
  # layout the `flow` stub expects ($root/build/cli/flow). Store mtimes are
  # all epoch 1, so the stub's `find -newer` checks never ask for a rebuild.
  buildPhase = ''
    runHook preBuild
    mkdir -p compiler/build build/cli
    cc -O2 -w -o compiler/build/flowc_bootstrap compiler/bootstrap/flowc_stage_a.c -lm
    FLOWC_BUNDLE=1 FLOWC_DIR=. FLOWC_TYPECHECK=1 \
      FLOWC_IN=tools/flow_cli/main.flow \
      FLOWC_OUT=build/cli/flow.c \
      ./compiler/build/flowc_bootstrap > /dev/null
    cc -O1 -w -o build/cli/flow build/cli/flow.c -lm
    rm build/cli/flow.c
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    mkdir -p "$out/lib/flow" "$out/bin"
    cp -R compiler lib runtime tools scripts registry build flow flow-lsp flow.toml VERSION "$out/lib/flow/"
    chmod +x "$out/lib/flow/flow" "$out/lib/flow/flow-lsp"
    patchShebangs "$out/lib/flow/flow" "$out/lib/flow/flow-lsp"

    # The store is read-only: point the stub at the prebuilt CLI and
    # bootstrap compiler instead of its user-cache fallback.
    substituteInPlace "$out/lib/flow/flow" \
      --replace-fail '[ -w "$root" ] || cache=''${XDG_CACHE_HOME:-$HOME/.cache}/flow' "" \
      --replace-fail '[ -w "$root" ] || boot=$cache/flowc_bootstrap' ""

    # Compiled programs go to the user cache (FLOW_BUILD_ROOT stays
    # overridable); tool binaries and the runtime archive fall back there
    # on their own when the install is read-only.
    for exe in flow flow-lsp; do
      makeWrapper "$out/lib/flow/$exe" "$out/bin/$exe" \
        --prefix PATH : ${runtimePath} \
        --run 'export FLOW_BUILD_ROOT=''${FLOW_BUILD_ROOT:-''${XDG_CACHE_HOME:-$HOME/.cache}/flow/build}'
    done
    runHook postInstall
  '';

  doInstallCheck = true;
  installCheckPhase = ''
    runHook preInstallCheck
    export HOME=$TMPDIR
    $out/bin/flow version
    printf 'function main() -> i32 {\n    println("nix ok")\n    return 0\n}\n' > $TMPDIR/hello.flow
    $out/bin/flow run $TMPDIR/hello.flow | grep -q "nix ok"
    runHook postInstallCheck
  '';

  meta = with pkgs.lib; {
    description = "Statically typed compiled systems language with algebraic effects and a C backend";
    homepage = "https://github.com/flooooooooooow/flow";
    license = licenses.mit;
    platforms = platforms.unix;
    mainProgram = "flow";
  };
}
