#!/usr/bin/env bash
# `flow gpu` parity gate: Metal and WGSL shaders for @gpu functions.
#
# Runs `./flow gpu [--wgsl] PROGRAM` for every case in tests/gpu/cases.txt
# with python and python3 stubbed out on PATH, and compares stdout, stderr,
# the exit status and every file written under build/gpu or build/wgsl with
# the goldens in tests/gpu/expected/<case>/. The repository path is replaced
# by @ROOT@ in both, so the goldens hold on any checkout.
#
# The goldens were recorded from the Python generator (src/flow/metal_codegen.py
# and src/flow/wgsl_codegen.py, run by the flow-driver of PARITY_REF):
#
#   tests/gpu/run.sh --record     # needs python3 and git; rewrites the goldens
#
# Where the Flow tool's text differs from Python's by design, the case's
# golden holds the Flow text and tests/gpu/KNOWN_DIFFERENCES.md says why:
# a Python traceback became one `error: ...` line, and parse and import
# errors come from the flowc front end.
#
# Usage: tests/gpu/run.sh [--record]

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
cd "$ROOT" || exit 1
PARITY_REF="${PARITY_REF:-fcd2edfe}"
CASES=tests/gpu/cases.txt
EXP=tests/gpu/expected
record=0
[[ "${1:-}" == "--record" ]] && record=1

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-gpu-gate.XXXXXX")"
work="$(cd "$work" && pwd -P)"
trap 'rm -rf "$work"' EXIT

driver_root="$ROOT"
if [[ "$record" -eq 1 ]]; then
    # The Python generator as it was: that revision's driver and src/flow.
    driver_root="$work/ref"
    mkdir -p "$driver_root"
    git archive "$PARITY_REF" flow flow-driver src lib compiler/scripts compiler/bootstrap | tar -x -C "$driver_root"
else
    stub="$work/bin"
    mkdir -p "$stub"
    for name in python python3; do
        printf '#!/bin/sh\necho "%s $*" >> "%s/python-calls.log"\nexit 127\n' "$name" "$work" > "$stub/$name"
        chmod +x "$stub/$name"
    done
    export PATH="$stub:$PATH"
    # Build the tool first, so no case sees the build messages.
    ./flow gpu tests/gpu/programs/no_gpu.flow >/dev/null 2>&1 || true
fi

normalise() {
    # Absolute paths of this checkout (or the recording tree) become @ROOT@.
    sed -e "s|$driver_root|@ROOT@|g" -e "s|$ROOT|@ROOT@|g"
}

pass=0
fail=0
while read -r lang prog; do
    [[ -z "$lang" || "$lang" == \#* ]] && continue
    tag="$(echo "$prog" | tr '/.' '__')_$lang"
    flag=""
    sub=gpu
    if [[ "$lang" == "wgsl" ]]; then
        flag="--wgsl"
        sub=wgsl
    fi
    rm -rf "$driver_root/build/gpu" "$driver_root/build/wgsl"
    out="$work/out/$tag"
    mkdir -p "$out/files"
    # Keep the program's directory free of the Python resolver's cache.
    ( cd "$ROOT" && NO_COLOR=1 "$driver_root/flow" gpu $flag "$ROOT/$prog" ) \
        > "$out/stdout.raw" 2> "$out/stderr.raw"
    echo $? > "$out/rc"
    normalise < "$out/stdout.raw" > "$out/stdout"
    if [[ "$record" -eq 1 ]]; then
        # A Python traceback is recorded as the one line the Flow tool prints.
        if grep -q '^Traceback' "$out/stderr.raw"; then
            tail -1 "$out/stderr.raw" | sed 's/^flow\.wgsl_codegen\.WgslUnsupported: /error: /' > "$out/stderr"
        else
            normalise < "$out/stderr.raw" > "$out/stderr"
        fi
    else
        normalise < "$out/stderr.raw" > "$out/stderr"
    fi
    if [[ -d "$driver_root/build/$sub" ]]; then
        for f in "$driver_root/build/$sub"/*; do
            [[ -f "$f" ]] || continue
            normalise < "$f" > "$out/files/$(basename "$f")"
        done
    fi
    rm -f "$out/stdout.raw" "$out/stderr.raw"
    if [[ "$record" -eq 1 ]]; then
        if [[ -f "$EXP/$tag/KEEP" ]]; then
            echo "keep  $tag (known difference, golden holds the Flow text)"
            continue
        fi
        rm -rf "$EXP/$tag"
        mkdir -p "$EXP/$tag"
        cp -R "$out/." "$EXP/$tag/"
        echo "rec   $tag"
        continue
    fi
    if diff -r -x KEEP "$EXP/$tag" "$out" > "$work/diff.txt" 2>&1; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL $tag"
        head -20 "$work/diff.txt"
    fi
done < "$CASES"

if [[ "$record" -eq 1 ]]; then
    exit 0
fi
# GPU_GATE_SAVE=DIR keeps this run's outputs, to inspect or to accept a
# known difference.
if [[ -n "${GPU_GATE_SAVE:-}" ]]; then
    mkdir -p "$GPU_GATE_SAVE"
    cp -R "$work/out/." "$GPU_GATE_SAVE/"
fi
if [[ -s "$work/python-calls.log" ]]; then
    echo "gpu gate: python was called:"
    cat "$work/python-calls.log"
    fail=$((fail + 1))
fi
echo "gpu gate: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
