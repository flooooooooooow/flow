#!/usr/bin/env bash
# Build the Stage-A flowc driver from the checked-in bootstrap C.
# Needs a C compiler and nothing else: no Python, no pip, no network.
#
#   ./compiler/scripts/bootstrap_from_c.sh           # build compiler/build/flowc_bootstrap
#   ./compiler/scripts/bootstrap_from_c.sh --verify  # + check the C still matches compiler/src
#   ./compiler/scripts/bootstrap_from_c.sh --regen   # rewrite the checked-in C from compiler/src
#
# --regen needs no Python. The binary built from the checked-in C compiles
# compiler/src/main.flow; the result compiles it again, and so on until two
# consecutive generations emit the same C (a fixed point, usually the second
# generation). That C replaces the checked-in file, so --verify then holds.
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
$CC $CFLAGS -o "$BOOT_BIN" "$BOOT_C" -lm

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

# Emit compiler/src/main.flow in bundle mode with the flowc binary $1 into $2.
emit_main() {
    FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src \
    FLOWC_IN=compiler/src/main.flow FLOWC_OUT="$2" \
        "$1"
    [[ -s "$2" ]]
}

if [[ "$mode" == "--regen" ]]; then
    emitter="$BOOT_BIN"
    prev=""
    gen=1
    while (( gen <= 4 )); do
        out="compiler/build/bootstrap_regen_gen${gen}.c"
        echo "=== regen gen${gen}: ${emitter} compiles compiler/src ==="
        emit_main "$emitter" "$out"
        if [[ -n "$prev" ]] && cmp -s "$prev" "$out"; then
            cp "$out" "$BOOT_C"
            echo "FIXED POINT at gen${gen}"
            echo "REGEN ${BOOT_C} ($(wc -c <"$BOOT_C") bytes)"
            # The checked-in binary beside it, and the local build.
            $CC $CFLAGS -o compiler/bootstrap/flowc_stage_a "$BOOT_C" -lm
            $CC $CFLAGS -o "$BOOT_BIN" "$BOOT_C" -lm
            exit 0
        fi
        $CC $CFLAGS -o "compiler/build/bootstrap_regen_gen${gen}" "$out" -lm
        emitter="compiler/build/bootstrap_regen_gen${gen}"
        prev="$out"
        gen=$(( gen + 1 ))
    done
    echo "FAIL regen: no fixed point after 4 generations" >&2
    exit 1
fi

if [[ "$mode" == "--verify" ]]; then
    emitter="$BOOT_BIN"
    echo "=== verify against ${emitter} emit of compiler/src ==="
    emit_main "$emitter" compiler/build/bootstrap_regen.c
    if ! cmp -s "$BOOT_C" compiler/build/bootstrap_regen.c; then
        echo "FAIL bootstrap drift: ${BOOT_C} != flowc emit of compiler/src" >&2
        echo "  regenerate with: ./compiler/scripts/bootstrap_from_c.sh --regen" >&2
        exit 1
    fi
    echo "PASS bootstrap C matches compiler/src (self-reproducing)"
fi

echo "ALL PASS bootstrap_from_c (${BOOT_BIN})"
