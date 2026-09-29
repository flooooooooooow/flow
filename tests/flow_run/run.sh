#!/usr/bin/env bash
# Goldens for the one-process runner (tools/run): `./flow run --json`,
# `--keep`, `--predict` and friends.
#
# Each line of tests/flow_run/cases.txt is `name|arguments`. The runner's
# stdout, stderr and exit status must equal tests/flow_run/expected/name.*
# after two normalisations: timing values read T, and the scratch directory
# reads TMP. The goldens were recorded from the Python runner
# (python3 -m flow.run, and flow.cost_model for --predict) before it was
# deleted. A `--keep DIR` case also checks that DIR holds the C and the
# binary.
#
# python and python3 are stubbed out on PATH: the runner must not need them.
#
# Usage: tests/flow_run/run.sh [name...]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-run-tests.XXXXXX")"
trap 'rm -rf "$work" build/flow-run-tests' EXIT
stub="$work/bin"
mkdir -p "$stub"
for name in python python3; do
    printf '#!/bin/sh\necho "%s $*" >> "%s/python-calls.log"\nexit 127\n' "$name" "$work" > "$stub/$name"
    chmod +x "$stub/$name"
done
export PATH="$stub:$PATH"
unset FLOW_RUN_PYTHON FLOW_RUN_DIRECT

normalise() {
    sed -E -e 's/"(transpile|compile|run|total)_s": [0-9.]+/"\1_s": T/' \
        -e 's#/[^ "]*/flow_run_[A-Za-z0-9_]+/#TMP/#g'
}

pass=0
fail=0
while IFS='|' read -r name args; do
    [[ -z "$name" || "$name" == \#* ]] && continue
    if [[ $# -gt 0 ]] && [[ " $* " != *" $name "* ]]; then
        continue
    fi
    read -r -a argv <<< "$args"
    set +e
    # Without one of the runner's own flags `flow run` is the driver's
    # runner; FLOW_RUN_DIRECT=1 asks for this one.
    direct=1
    case " $args " in
        *" --json "*|*" --keep "*|*" --predict "*|*" --extra-cflags="*) direct=0 ;;
    esac
    if [[ "$direct" -eq 1 ]]; then
        FLOW_RUN_DIRECT=1 ./flow run "${argv[@]}" > "$work/$name.out" 2> "$work/$name.err"
    else
        ./flow run "${argv[@]}" > "$work/$name.out" 2> "$work/$name.err"
    fi
    rc=$?
    set -e
    ok=1
    exp="tests/flow_run/expected/$name"
    if [[ "$rc" != "$(cat "$exp.rc")" ]]; then
        echo "  $name: exit $rc, expected $(cat "$exp.rc")"
        ok=0
    fi
    if ! diff -u <(normalise < "$exp.out") <(normalise < "$work/$name.out") > "$work/$name.diff"; then
        echo "  $name: stdout differs"
        sed 's/^/    /' "$work/$name.diff" | head -20
        ok=0
    fi
    if ! diff -u <(normalise < "$exp.err") <(normalise < "$work/$name.err") > "$work/$name.ediff"; then
        echo "  $name: stderr differs"
        sed 's/^/    /' "$work/$name.ediff" | head -20
        ok=0
    fi
    for keep in $(printf '%s\n' "$args" | sed -n 's/.*--keep \([^ ]*\).*/\1/p'); do
        prog="$(basename "${argv[0]}" .flow)"
        if [[ "$rc" -eq 0 && ( ! -f "$keep/$prog.c" || ! -x "$keep/$prog" ) ]]; then
            echo "  $name: $keep lacks $prog.c or $prog"
            ok=0
        fi
    done
    if [[ "$ok" -eq 1 ]]; then
        pass=$((pass + 1))
    else
        echo "FAIL $name"
        fail=$((fail + 1))
    fi
done < tests/flow_run/cases.txt

if [[ -s "$work/python-calls.log" ]]; then
    echo "FAIL python was called:"
    cat "$work/python-calls.log"
    fail=$((fail + 1))
fi
echo "flow_run: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
