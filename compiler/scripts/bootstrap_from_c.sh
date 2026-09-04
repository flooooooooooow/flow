#!/usr/bin/env bash
# Build the Stage-A flowc driver from the checked-in bootstrap C.
# Needs a C compiler and nothing else — no Python, no pip, no network.
#
#   ./compiler/scripts/bootstrap_from_c.sh           # build compiler/build/flowc_bootstrap
#   ./compiler/scripts/bootstrap_from_c.sh --verify  # + check the C still matches compiler/src
#   ./compiler/scripts/bootstrap_from_c.sh --regen   # rewrite the checked-in C from compiler/src
#
# compiler/bootstrap/flowc_stage_a.c is `main.flow` plus every module it
# imports, emitted by flowc as one translation unit. It is how a user gets a
# working compiler out of this repo without the Python host.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build

BOOT_C=compiler/bootstrap/flowc_stage_a.c
BOOT_BIN=compiler/build/flowc_bootstrap
CC="${CC:-cc}"
CFLAGS="${CFLAGS:--O2}"
mode="${1:-}"

if [[ ! -f "$BOOT_C" ]]; then
    echo "bootstrap_from_c: missing ${BOOT_C}" >&2
    exit 1
fi

echo "=== cc ${BOOT_C} -> ${BOOT_BIN} ==="
$CC $CFLAGS -o "$BOOT_BIN" "$BOOT_C" &
cc_pid=$!
while kill -0 $cc_pid 2>/dev/null; do
    sleep 30
    if kill -0 $cc_pid 2>/dev/null; then
        echo "  ... still compiling ${BOOT_C} ..."
    fi
done
wait $cc_pid

# Smoke: the bootstrap compiler compiles an ordinary Stage-A program.
# Positional argv runs the self-test suite; emit needs FLOWC_IN / FLOWC_OUT.
FLOWC_IN=compiler/fixtures/stage_a_sum.flow \
FLOWC_OUT=compiler/build/bootstrap_sum.c \
    "$BOOT_BIN"
$CC -O0 -o compiler/build/bootstrap_sum compiler/build/bootstrap_sum.c
set +e
./compiler/build/bootstrap_sum
sum_code=$?
set -e
if [[ "$sum_code" -ne 45 ]]; then
    echo "FAIL bootstrap: stage_a_sum exit ${sum_code} (want 45)" >&2
    exit 1
fi
echo "PASS bootstrap compiles stage_a_sum (exit 45)"

# Regenerate with the freshest compiler available, so a cgen change lands in
# the checked-in C in one step rather than converging over several runs.
pick_emitter() {
    local cand
    for cand in \
        compiler/build/stage_a_driver_flow_self \
        compiler/build/stage_a_driver_flow_g2 \
        compiler/build/stage_a_driver_flow \
        "$BOOT_BIN"
    do
        if [[ -x "$cand" ]]; then
            printf '%s\n' "$cand"
            return 0
        fi
    done
    return 1
}

if [[ "$mode" == "--regen" ]]; then
    emitter="$(pick_emitter)"
    echo "=== regen with ${emitter} ==="
    # Checked-in bootstrap C is the main.flow bundle (includes self-tests).
    FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src \
    FLOWC_IN=compiler/src/main.flow FLOWC_OUT="$BOOT_C" \
        "$emitter"
    echo "REGEN ${BOOT_C} ($(wc -c <"$BOOT_C") bytes)"
    exit 0
fi

if [[ "$mode" == "--verify" ]]; then
    emitter="$(pick_emitter)"
    echo "=== verify against ${emitter} emit of compiler/src ==="
    FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src \
    FLOWC_IN=compiler/src/main.flow FLOWC_OUT=compiler/build/bootstrap_regen.c \
        "$emitter"
    if ! cmp -s "$BOOT_C" compiler/build/bootstrap_regen.c; then
        echo "FAIL bootstrap drift: ${BOOT_C} != flowc emit of compiler/src" >&2
        echo "  regenerate with: ./compiler/scripts/bootstrap_from_c.sh --regen" >&2
        exit 1
    fi
    echo "PASS bootstrap C matches compiler/src (self-reproducing)"
fi

echo "ALL PASS bootstrap_from_c (${BOOT_BIN})"
