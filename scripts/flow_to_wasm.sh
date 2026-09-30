#!/usr/bin/env bash
# The legacy Flow to WebAssembly converter behind `flow wasm --legacy`.
#
#   scripts/flow_to_wasm.sh <file.flow> [outdir]   one program (default outdir
#                                                  wasm/wasm_examples)
#   scripts/flow_to_wasm.sh --all                  the example list, plus index.html
#
# The converter is the Flow program in scripts/tools/flow_to_wasm, built with
# the Stage-A compiler on first use. The current builder is `flow wasm`
# (scripts/wasm_build.sh). See wasm/README.md.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$("$ROOT/scripts/tools/build_tool.sh" flow_to_wasm)"
FLOW_REPO_ROOT="$ROOT" exec "$ROOT/$BIN" "$@"
