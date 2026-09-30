#!/bin/bash
# Cross-dimensional benchmark harness over benchmarks/cross_harness.
# The harness is the Flow program in scripts/tools/bench_harness. It runs the
# CPython twins in benchmarks/baselines/python/cross_harness when python3 is
# available and skips them otherwise.
#
#   benchmarks/run_benchmarks.sh [--smoke] [--baseline OLD.json] [--out OUT.json] [--cleanup]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
BIN="$("$ROOT/scripts/tools/build_tool.sh" bench_harness)"
FLOW_REPO_ROOT="$ROOT" exec "$ROOT/$BIN" "$@"
