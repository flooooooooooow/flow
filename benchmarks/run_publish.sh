#!/bin/bash
# Regenerates benchmarks/RESULTS.md. Run from anywhere in the repo.
# The harness is the Flow program in scripts/tools/bench_publish.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
BIN="$("$ROOT/scripts/tools/build_tool.sh" bench_publish)"
FLOW_REPO_ROOT="$ROOT" exec "$ROOT/$BIN" "$@"
