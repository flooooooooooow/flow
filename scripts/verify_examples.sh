#!/usr/bin/env bash
# Verify that every .flow file under examples/ (and apps/, benchmarks/)
# compiles, and regenerate the status table in examples/STATUS.md.
#
# The logic is the Flow program in scripts/tools/verify_examples. It runs
# flowc (compiler/scripts/flowc_emit.sh) and clang per file, in parallel
# through xargs -P.
#
# Usage (from anywhere):
#   ./scripts/verify_examples.sh                 # sweep + rewrite examples/STATUS.md
#   ./scripts/verify_examples.sh --roots examples
#   ./scripts/verify_examples.sh --json out.json --no-write
#
# flowc is resolved once here and passed to every worker in FLOWC_BIN.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"

if [[ -z "${FLOWC_BIN:-}" ]]; then
    FLOWC_BIN="$(bash "$ROOT/compiler/scripts/ensure_flowc.sh")"
    [[ "$FLOWC_BIN" == /* ]] || FLOWC_BIN="$ROOT/$FLOWC_BIN"
    export FLOWC_BIN
fi

BIN="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" verify_examples)"
VERIFY_ROOT="$ROOT" exec "$BIN" "$@"
