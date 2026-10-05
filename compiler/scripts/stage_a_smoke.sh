#!/usr/bin/env bash
# Minimal Stage-A round-trip smoke: emit one fixture → cc → run → check exit.
# Uses the Python host to run compiler/src/main.flow (does NOT replace the host).
# Optional: FLOWC_USE_DRIVER=1 prefers a prebuilt stage_a_driver(_flow) if present.
# Full suite: ./compiler/scripts/roundtrip.sh
#
# Usage (from repo root):
#   ./compiler/scripts/stage_a_smoke.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build

# Avoid ./flow hanging on `brew --prefix llvm` when Homebrew is busy/locked.
if [[ -z "${LLVM_PATH:-}" ]]; then
    for candidate in /opt/homebrew/opt/llvm/bin /usr/local/opt/llvm/bin; do
        if [[ -d "$candidate" ]]; then
            export LLVM_PATH="$candidate"
            break
        fi
    done
fi

FIXTURE="compiler/fixtures/stage_a_sum.flow"
C_OUT="compiler/build/stage_a_smoke_sum.c"
BIN="compiler/build/stage_a_smoke_sum"
EXPECT=45

stage_a_emit() {
    local src="$1"
    local c_out="$2"
    if [[ "${FLOWC_USE_DRIVER:-}" == "1" ]]; then
        if [[ -x compiler/build/stage_a_driver_flow ]]; then
            ./compiler/build/stage_a_driver_flow "$src" "$c_out"
            return
        fi
        if [[ -x compiler/build/stage_a_driver ]]; then
            ./compiler/build/stage_a_driver "$src" "$c_out"
            return
        fi
        echo "FAIL stage_a_smoke: FLOWC_USE_DRIVER=1 but no stage_a_driver*" >&2
        return 1
    fi
    if [[ ! -f compiler/src/main.flow ]]; then
        echo "FAIL stage_a_smoke: missing compiler/src/main.flow" >&2
        return 1
    fi
    # Host emit: picks up latest Stage-A sources; no stale driver binary.
    export FLOWC_IN="$src"
    export FLOWC_OUT="$c_out"
    ./flow run compiler/src/main.flow
}

echo "=== stage_a_smoke (${FIXTURE} → exit ${EXPECT}) ==="
stage_a_emit "$FIXTURE" "$C_OUT"
if [[ ! -f "$C_OUT" ]]; then
    echo "FAIL stage_a_smoke: emit did not write ${C_OUT}" >&2
    exit 1
fi
cc -O0 -o "$BIN" "$C_OUT"
set +e
"./$BIN"
code=$?
set -e
echo "exit=$code"
if [[ "$code" -ne "$EXPECT" ]]; then
    echo "FAIL stage_a_smoke: expected exit ${EXPECT}, got ${code}" >&2
    exit 1
fi
echo "PASS stage_a_smoke"
