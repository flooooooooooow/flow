#!/usr/bin/env bash
# Regenerate baseline_results.md and baseline_results.json.
# The runner is the Flow program in scripts/tools/bench_baselines.
# Flow sources reach C through flowc (compiler/scripts/flowc_emit.flow).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
BIN="$("$ROOT/scripts/tools/build_tool.sh" bench_baselines)"
FLOW_REPO_ROOT="$ROOT" exec "$ROOT/$BIN" "$@"
