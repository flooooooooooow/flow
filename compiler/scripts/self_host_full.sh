#!/usr/bin/env bash
# Whole-compiler self-host: flowc bundle-compiles all of compiler/src/ into one
# C translation unit, and three consecutive generations agree byte for byte.
#
#   gen1 = <bootstrap driver> compiles compiler/src/main.flow
#   gen2 = gen1 compiles compiler/src/main.flow
#   gen3 = gen2 compiles compiler/src/main.flow
#
# Each generation is a complete flowc: run it with no FLOWC_IN and it executes
# the front-end self-test suite; run it with FLOWC_IN/FLOWC_OUT/FLOWC_BUNDLE and
# it emits C. The fixed point is checked on the emitted C and on the object.
#
# This is success metric #1 of docs/project/self-hosting.md and the Phase-B
# exit evidence for issue #151: compiler/src builds under flowc with no
# FLOWC_TYPECHECK=0 opt-out.
#
#   ./compiler/scripts/self_host_full.sh
#
# Env:
#   FLOWC_BOOTSTRAP=<path>  use this binary as the gen0 emitter
#   FLOWC_KEEP=1            keep intermediate C for inspection (default: kept)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build

ENTRY=compiler/src/main.flow
SRCDIR=compiler/src

# --- pick the gen0 emitter -------------------------------------------------
BOOT="${FLOWC_BOOTSTRAP:-}"
if [[ -z "$BOOT" ]]; then
    for cand in \
        compiler/build/stage_a_driver_flow_self \
        compiler/build/stage_a_driver_flow \
        compiler/build/stage_a_driver \
        compiler/build/flowc_bootstrap; do
        if [[ -x "$cand" ]]; then
            BOOT="$cand"
            break
        fi
    done
fi
if [[ -z "$BOOT" ]]; then
    echo "self_host_full: no Stage-A driver in compiler/build" >&2
    echo "  run ./compiler/scripts/roundtrip.sh first (or set FLOWC_BOOTSTRAP)" >&2
    exit 1
fi
echo "=== gen0 emitter: ${BOOT} ==="

# Emit the whole compiler with `bin` (a Stage-A driver or a previous
# generation of flowc) into `out`.
emit_compiler() {
    local bin="$1"
    local out="$2"
    rm -f "$out"
    # driver.flow binaries prefer argv, main.flow binaries read the env — pass
    # both so any generation works without knowing which shape it is.
    FLOWC_BUNDLE=1 FLOWC_DIR="$SRCDIR" FLOWC_IN="$ENTRY" FLOWC_OUT="$out" \
        "$bin" "$ENTRY" "$out"
    if [[ ! -s "$out" ]]; then
        echo "FAIL emit: ${bin} wrote no C to ${out}" >&2
        exit 1
    fi
}

# A generation is only real if it passes flowc's own self-tests and can still
# compile an ordinary Stage-A program.
check_generation() {
    local gen="$1"
    local bin="compiler/build/flowc_${gen}"
    local log="compiler/build/flowc_${gen}_selftest.log"

    set +e
    env -u FLOWC_IN -u FLOWC_OUT -u FLOWC_BUNDLE -u FLOWC_DIR "$bin" >"$log" 2>&1
    local code=$?
    set -e
    if [[ "$code" -ne 0 ]]; then
        echo "FAIL ${gen}: self-tests exited ${code}" >&2
        tail -20 "$log" >&2
        exit 1
    fi
    if ! grep -Fq 'flowc: PASS' "$log"; then
        echo "FAIL ${gen}: self-tests did not print 'flowc: PASS'" >&2
        tail -20 "$log" >&2
        exit 1
    fi
    echo "PASS ${gen} self-tests (flowc: PASS)"

    # Ordinary user program through this generation: stage_a_sum → exit 45.
    FLOWC_IN=compiler/fixtures/stage_a_sum.flow \
    FLOWC_OUT="compiler/build/${gen}_stage_a_sum.c" \
        env -u FLOWC_BUNDLE -u FLOWC_DIR "$bin" >/dev/null
    cc -O0 -o "compiler/build/${gen}_stage_a_sum" "compiler/build/${gen}_stage_a_sum.c"
    set +e
    "./compiler/build/${gen}_stage_a_sum"
    local sum_code=$?
    set -e
    if [[ "$sum_code" -ne 45 ]]; then
        echo "FAIL ${gen}: stage_a_sum exit ${sum_code} (want 45)" >&2
        exit 1
    fi
    echo "PASS ${gen} compiles stage_a_sum (exit 45)"
}

# --- gen1 ------------------------------------------------------------------
echo "=== gen1: bootstrap driver compiles all of compiler/src ==="
emit_compiler "$BOOT" compiler/build/flowc_gen1.c
cc -O0 -o compiler/build/flowc_gen1 compiler/build/flowc_gen1.c
echo "gen1 C: $(wc -c <compiler/build/flowc_gen1.c) bytes"
check_generation gen1

# --- gen2 ------------------------------------------------------------------
echo "=== gen2: gen1 compiles all of compiler/src ==="
emit_compiler compiler/build/flowc_gen1 compiler/build/flowc_gen2.c
if ! cmp -s compiler/build/flowc_gen1.c compiler/build/flowc_gen2.c; then
    echo "FAIL fixed point: gen1.c != gen2.c" >&2
    diff <(head -400 compiler/build/flowc_gen1.c) \
         <(head -400 compiler/build/flowc_gen2.c) | head -40 >&2
    exit 1
fi
echo "PASS fixed point: gen1.c == gen2.c"
cc -O0 -o compiler/build/flowc_gen2 compiler/build/flowc_gen2.c
check_generation gen2

# --- gen3 ------------------------------------------------------------------
echo "=== gen3: gen2 compiles all of compiler/src ==="
emit_compiler compiler/build/flowc_gen2 compiler/build/flowc_gen3.c
if ! cmp -s compiler/build/flowc_gen2.c compiler/build/flowc_gen3.c; then
    echo "FAIL fixed point: gen2.c != gen3.c" >&2
    exit 1
fi
echo "PASS fixed point: gen2.c == gen3.c"
cc -O0 -o compiler/build/flowc_gen3 compiler/build/flowc_gen3.c
check_generation gen3

# Object bytes: linked binaries carry a build UUID, objects do not.
# Object bytes: linked binaries carry a build UUID, objects do not. But the
# C compiler may embed the source path, so giving the two generations
# different filenames can make identical C produce different objects (as seen
# on Ubuntu's GCC). Compile both from a single common source path so no
# filename-dependent bytes can leak into the object.
cp compiler/build/flowc_gen2.c compiler/build/fixedpoint_src.c
cc -O0 -c compiler/build/fixedpoint_src.c -o compiler/build/flowc_gen2.o
cp compiler/build/flowc_gen3.c compiler/build/fixedpoint_src.c
cc -O0 -c compiler/build/fixedpoint_src.c -o compiler/build/flowc_gen3.o
if ! cmp -s compiler/build/flowc_gen2.o compiler/build/flowc_gen3.o; then
    echo "FAIL fixed point: gen2.o != gen3.o" >&2
    echo "  md5: gen2=$(md5sum < compiler/build/flowc_gen2.o 2>/dev/null || md5 < compiler/build/flowc_gen2.o) gen3=$(md5sum < compiler/build/flowc_gen3.o 2>/dev/null || md5 < compiler/build/flowc_gen3.o)" >&2
    cmp -l compiler/build/flowc_gen2.o compiler/build/flowc_gen3.o 2>/dev/null | head -5 >&2
    exit 1
fi
echo "PASS fixed point: gen2.o == gen3.o"

echo "ALL PASS self_host_full (three consecutive generations, byte-identical)"
