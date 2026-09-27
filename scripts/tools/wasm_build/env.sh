# Sourced by scripts/wasm_build.sh and scripts/build_wasm_gallery.sh with
# ROOT set. Builds the Flow tool and exports what it reads.

WASM_BUILD_BIN="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" wasm_build)"

# Homebrew's emscripten ships a config pointing LLVM_ROOT at Xcode clang (no
# wasm backend) and a launcher that picks a python too old to parse its own
# sources. Point both at emscripten's own copies unless the caller already has.
if [[ -z "${EMSDK_PYTHON:-}" && -e /opt/homebrew/bin/python3.14 ]]; then
  export EMSDK_PYTHON=/opt/homebrew/bin/python3.14
fi
if [[ -z "${EM_LLVM_ROOT:-}" && -e /opt/homebrew/opt/emscripten/libexec/llvm/bin ]]; then
  export EM_LLVM_ROOT=/opt/homebrew/opt/emscripten/libexec/llvm/bin
fi
if [[ -z "${EM_BINARYEN_ROOT:-}" && -e /opt/homebrew/opt/emscripten/libexec/binaryen ]]; then
  export EM_BINARYEN_ROOT=/opt/homebrew/opt/emscripten/libexec/binaryen
fi

export FLOW_REPO_ROOT="$ROOT"
export WASM_BUILD_BIN
# The transpiler still runs under Python (python3 -m flow.transpiler).
WASM_BUILD_PYTHON="$(command -v python3 || echo python3)"
export WASM_BUILD_PYTHON
