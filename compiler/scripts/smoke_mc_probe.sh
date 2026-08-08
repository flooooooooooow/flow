#!/usr/bin/env bash
# Smoke: flowc_mathematical_case_condition (and the flow_strcat runtime) through
# the Stage-A pipeline — bundle typecheck → emit → cc → run. The fixture lives
# in compiler/fixtures but imports `.math_prose` / `.claim_address`, so the
# bundle search dir must be compiler/src.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
OUT="${1:-compiler/build/stage_a_mc_probe.c}"
BIN="compiler/build/stage_a_mc_probe"
mkdir -p compiler/build

# Emit via a Stage-A driver when one exists; else compile flowc through the
# Python host (same fallback chain as roundtrip.sh's stage_a_emit).
if [[ -x compiler/build/stage_a_driver_flow ]]; then
    FLOWC_IN="$ROOT/compiler/fixtures/stage_a_mc_probe.flow" \
        FLOWC_OUT="$OUT" FLOWC_BUNDLE=1 FLOWC_DIR="$ROOT/compiler/src" \
        ./compiler/build/stage_a_driver_flow
elif [[ -x compiler/build/stage_a_driver ]]; then
    FLOWC_IN="$ROOT/compiler/fixtures/stage_a_mc_probe.flow" \
        FLOWC_OUT="$OUT" FLOWC_BUNDLE=1 FLOWC_DIR="$ROOT/compiler/src" \
        ./compiler/build/stage_a_driver
else
    # Compile flowc itself through the Python host, then run its emit mode.
    FLOW_HOST=python FLOWC_IN="$ROOT/compiler/fixtures/stage_a_mc_probe.flow" \
        FLOWC_OUT="$OUT" FLOWC_BUNDLE=1 FLOWC_DIR="$ROOT/compiler/src" \
        ./flow run compiler/src/main.flow
fi

cc -O0 -o "$BIN" "$OUT"
"$BIN"
echo "PASS stage_a_mc_probe (flowc bundle emit → cc → run)"
exit 0
