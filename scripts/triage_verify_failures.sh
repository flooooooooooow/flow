#!/usr/bin/env bash
# Triage parser failures under the `flow-verify` proof corpus (examples/verify/).
#
# The logic is the Flow program in scripts/tools/triage_verify_failures. It
# runs flowc (compiler/scripts/flowc_emit.flow) per file, in parallel through
# xargs -P, and prints failures bucketed by error and by suspected missing
# feature.
#
# Usage (from anywhere):
#   ./scripts/triage_verify_failures.sh
#   ./scripts/triage_verify_failures.sh --roots examples/verify --sample 5
#   ./scripts/triage_verify_failures.sh --json triage.json
#
# flowc is resolved once here and passed to every worker in FLOWC_BIN.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"

if [[ -z "${FLOWC_BIN:-}" ]]; then
    FLOWC_BIN="$("$ROOT/flow" tool "$ROOT/compiler/scripts/ensure_flowc.flow")"
    [[ "$FLOWC_BIN" == /* ]] || FLOWC_BIN="$ROOT/$FLOWC_BIN"
    export FLOWC_BIN
fi

BIN="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" triage_verify_failures)"
VERIFY_ROOT="$ROOT" exec "$BIN" "$@"
