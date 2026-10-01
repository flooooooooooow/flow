#!/usr/bin/env bash
# Compile Flow or LLVM IR to a freestanding wasm32 module (no libc, no
# Emscripten).
#
#   scripts/wasm32_target.sh IN.flow|IN.ll -o OUT.wasm [--export NAME ...]
#       [-O O0|O1|O2|O3|Os|Oz]
#
# The compiler is the Flow program in scripts/tools/llvm_target, built with
# the Stage-A compiler on first use. `flow wasm32` runs this. Flow sources reach
# LLVM IR through `flow flow-to-llvm`.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
BIN="$("$ROOT/scripts/tools/build_tool.sh" llvm_target)"
[[ "$BIN" == /* ]] || BIN="$ROOT/$BIN"
FLOW_REPO_ROOT="$ROOT" exec "$BIN" wasm32 "$@"
