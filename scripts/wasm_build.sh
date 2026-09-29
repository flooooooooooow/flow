#!/usr/bin/env bash
# Compile one Flow program to a runnable WebAssembly page.
#
#   scripts/wasm_build.sh examples/games/snake_gfx.flow --out site/wasm/snake
#   scripts/wasm_build.sh examples/wasm/hello_wasm.flow --backend=mlir
#   scripts/wasm_build.sh examples/wasm/hello_wasm.flow --backend=mlir \
#       --preload /tmp/data@/data --link runtime/flow_rt_support.c
#
# The builder is the Flow program in scripts/tools/wasm_build, built with the
# Stage-A compiler on first use. `./flow wasm` runs this. See
# docs/language/wasm.md.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
# shellcheck source=scripts/tools/wasm_build/env.sh
# shellcheck disable=SC1091 # shared env, checked on its own
source "$ROOT/scripts/tools/wasm_build/env.sh"
exec "$WASM_BUILD_BIN" build "$@"
