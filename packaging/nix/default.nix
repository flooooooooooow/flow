{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation rec {
  pname = "flow";
  version = "1.0.2";

  src = pkgs.fetchFromGitHub {
    owner = "flooooooooooow";
    repo = "flow";
    rev = "v${version}";
    sha256 = "0000000000000000000000000000000000000000000000000000000000000000";
  };

  nativeBuildInputs = [
    pkgs.clang
    pkgs.python3
  ];

  buildInputs = [
    pkgs.zlib
  ];

  installPhase = ''
    runHook preInstall
    mkdir -p $out/bin $out/lib/flow
    cp -r src lib runtime compiler $out/lib/flow/
    cp flow $out/bin/flow
    chmod +x $out/bin/flow
    runHook postInstall
  '';

  meta = with pkgs.lib; {
    description = "Flow programming language toolchain and runtime";
    homepage = "https://github.com/flooooooooooow/flow";
    license = licenses.mit;
    platforms = platforms.all;
    mainProgram = "flow";
  };
}
