#!/usr/bin/env bash
# Smoke: the math_prose rewrite family (flow_expr_to_mathematical_english /
# flow_expr_to_latex ports) through the Stage-A pipeline — bundle typecheck →
# emit → cc → run. The fixture lives in compiler/fixtures but imports
# `.math_prose` / `.claim_address`, so the bundle search dir must be
# compiler/src.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
OUT="${1:-compiler/build/stage_a_mp_probe.c}"
BIN="compiler/build/stage_a_mp_probe"
mkdir -p compiler/build

# Emit via the Python host: mp_probe exercises the newest cgen features
# (mixed and/or operand parens, flow_strcat), so a stale stage_a_driver_flow
# binary from a prior roundtrip would emit without them. The host path
# compiles flowc from the latest compiler/src sources.
FLOW_HOST=python FLOWC_IN="$ROOT/compiler/fixtures/stage_a_mp_probe.flow" \
    FLOWC_OUT="$OUT" FLOWC_BUNDLE=1 FLOWC_DIR="$ROOT/compiler/src" \
    ./flow run compiler/src/main.flow

cc -O0 -o "$BIN" "$OUT"
"$BIN"
echo "PASS stage_a_mp_probe (flowc bundle emit → cc → run)"
exit 0
