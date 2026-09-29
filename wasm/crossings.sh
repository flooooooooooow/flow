#!/usr/bin/env bash
# Build the WASM crossing demos and pages under site/wasm-crossings.
#
#   wasm/crossings.sh all                 every crossing, then the index
#   wasm/crossings.sh index               index page only
#   wasm/crossings.sh threads [program.flow] [--workers N] [--no-build]
#   wasm/crossings.sh sockets [program.flow] [--port 9505] [--no-build]
#   wasm/crossings.sh python  [program.flow] [--no-build]
#   wasm/crossings.sh fs [program.flow] [--fs memfs|idbfs] [--preload DIR@/MOUNT]
#   wasm/crossings.sh gpu [program.flow] [-n COUNT] [--no-build]   the GPU crossing
#
# The builder is the Flow program in scripts/tools/wasm_crossings, built with
# the Stage-A compiler on first use. See docs/language/wasm-crossings.md.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
BIN="$("$ROOT/scripts/tools/build_tool.sh" wasm_crossings)"
FLOW_REPO_ROOT="$ROOT" exec "$ROOT/$BIN" "$@"
