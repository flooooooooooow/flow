#!/usr/bin/env bash
# Triage parser failures under the `flow-verify` proof corpus (examples/verify/).
#
# The logic is the Flow program in scripts/tools/triage_verify_failures. It
# runs the Python transpiler per file, in parallel through xargs -P, and
# prints failures bucketed by parser error and by suspected missing feature.
#
# Usage (from anywhere):
#   ./scripts/triage_verify_failures.sh
#   ./scripts/triage_verify_failures.sh --roots examples/verify --sample 5
#   ./scripts/triage_verify_failures.sh --json triage.json
#
# Set VERIFY_PYTHON to choose the interpreter for the transpiler (default
# python3).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"

BIN="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" triage_verify_failures)"
VERIFY_ROOT="$ROOT" exec "$BIN" "$@"
