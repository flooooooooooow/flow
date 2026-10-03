{ lib
, stdenv
, python3
, makeWrapper
}:

stdenv.mkDerivation rec {
  pname = "flow";
  version = "1.0.2";

  src = lib.cleanSource ../..;

  nativeBuildInputs = [ makeWrapper ];

  buildInputs = [
    (python3.withPackages (ps: with ps; [ numpy ]))
  ];

  buildPhase = ''
    runHook preBuild
    mkdir -p compiler/build
    $CC -O2 -o compiler/build/flowc compiler/bootstrap/flowc_stage_a.c
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    mkdir -p $out/libexec/flow $out/bin

    cp -r flow flow-driver src lib runtime compiler $out/libexec/flow/
    if [ -f flow-lsp ]; then
      cp flow-lsp $out/libexec/flow/
    fi
    for dir in tools wasm examples pyproject.toml requirements.txt; do
      if [ -e "$dir" ]; then
        cp -r "$dir" $out/libexec/flow/
      fi
    done

    chmod 0755 $out/libexec/flow/flow
    chmod 0755 $out/libexec/flow/flow-driver
    if [ -f $out/libexec/flow/flow-lsp ]; then
      chmod 0755 $out/libexec/flow/flow-lsp
    fi

    makeWrapper $out/libexec/flow/flow $out/bin/flow \
      --prefix PATH : ${lib.makeBinPath [ (python3.withPackages (ps: with ps; [ numpy ])) stdenv.cc ]} \
      --set PYTHONPATH "$out/libexec/flow/src"

    if [ -f $out/libexec/flow/flow-lsp ]; then
      makeWrapper $out/libexec/flow/flow-lsp $out/bin/flow-lsp \
        --prefix PATH : ${lib.makeBinPath [ (python3.withPackages (ps: with ps; [ numpy ])) stdenv.cc ]} \
        --set PYTHONPATH "$out/libexec/flow/src"
    fi

    runHook postInstall
  '';

  meta = with lib; {
    description = "Statically typed programming language for systems that evolve through time";
    homepage = "https://flooooooooooow.github.io/flow/";
    license = licenses.mit;
    platforms = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
    mainProgram = "flow";
  };
}
