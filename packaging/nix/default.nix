{ pkgs ? import <nixpkgs> {}, src ? ../.. }:

let
  version = pkgs.lib.removeSuffix "\n" (builtins.readFile "${src}/VERSION");
  runtimePath = pkgs.lib.makeBinPath [ pkgs.clang pkgs.coreutils pkgs.findutils ];
in
pkgs.stdenvNoCC.mkDerivation {
  pname = "flow";
  inherit version src;

  dontBuild = true;

  installPhase = ''
    runHook preInstall

    mkdir -p "$out/lib/flow" "$out/bin"
    cp -R compiler lib runtime tools scripts registry flow flow.toml VERSION "$out/lib/flow/"
    chmod +x "$out/lib/flow/flow"
    patchShebangs "$out/lib/flow/flow"

    cat > "$out/bin/flow" <<EOF
#!${pkgs.runtimeShell}
export PATH="${runtimePath}:\$PATH"
exec "$out/lib/flow/flow" "\$@"
EOF
    chmod +x "$out/bin/flow"

    runHook postInstall
  '';

  meta = with pkgs.lib; {
    description = "Flow programming language toolchain and runtime";
    homepage = "https://github.com/flooooooooooow/flow";
    license = licenses.mit;
    platforms = platforms.unix;
    mainProgram = "flow";
  };
}
