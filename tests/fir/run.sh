#!/usr/bin/env bash
# Parity gate for `flow fir-g` (tools/fir), with no Python.
#
# Builds tools/fir/main.flow with the flowc of the checked-in bootstrap C,
# runs every case in tests/fir/cases.txt and compares stdout, the exit code,
# stderr (all of it, its last line, or not at all, as the case says) and,
# for --calibrate, the thresholds file written, against the goldens in
# tests/fir/golden. The goldens came from src/flow/fir_cli.py run with NumPy
# and MLX unavailable, which is the machine the Flow tool is: bulk analysis
# never runs, so everything compared is deterministic.
#
# Masked before comparing: the host tag in calibration output (uname), and
# the --bench timings. One deliberate change from the Python text: the
# calibration note reads "(bulk never beat CPU in sweep; auto stays on
# cpu)" where the Python text had a dash.
#
# python and python3 are stubs that fail and log; any call fails the gate.
# The last cases run through ./flow fir-g to check the launcher too.
#
#   tests/fir/run.sh

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" || exit 1

OUT=build/fir-gate
rm -rf "$OUT"
mkdir -p "$OUT/bin"
log="$OUT/python-calls.log"
: > "$log"
for name in python python3; do
    cat > "$OUT/bin/$name" <<EOF
#!/bin/sh
echo "$name \$*" >> "$ROOT/$log"
exit 127
EOF
    chmod +x "$OUT/bin/$name"
done
export PATH="$ROOT/$OUT/bin:$PATH"

CC="${CC:-cc}"
FLOWC="$OUT/flowc"
"$CC" -O1 -w -o "$FLOWC" compiler/bootstrap/flowc_stage_a.c -lm || exit 1
if ! FLOWC_BUNDLE=1 FLOWC_DIR=. FLOWC_TYPECHECK=1 FLOWC_IN=tools/fir/main.flow \
        FLOWC_OUT="$OUT/fir.c" "$FLOWC" > "$OUT/flowc.log" 2>&1; then
    cat "$OUT/flowc.log"
    echo "fir gate: flowc could not build tools/fir/main.flow"
    exit 1
fi
"$CC" -O2 -w -o "$OUT/flow-fir" "$OUT/fir.c" -lm || exit 1

mask() {
    sed -E \
        -e 's/"host": "[^"]*"/"host": "HOST"/' \
        -e 's/bench: cpu=[0-9.]+ ms/bench: cpu=T ms/' \
        -e 's/"bench_cpu_ms": [-0-9.e]+/"bench_cpu_ms": T/'
}

pass=0
fail=0
while IFS=$'\t' read -r name check args; do
    [[ -z "$name" || "$name" == \#* ]] && continue
    # shellcheck disable=SC2086
    FLOW_ROOT="$ROOT" "$OUT/flow-fir" $args > "$OUT/$name.out" 2> "$OUT/$name.err"
    rc=$?
    ok=1
    why=""
    if [[ "$rc" != "$(cat "tests/fir/golden/$name.rc")" ]]; then
        ok=0; why="exit $rc, want $(cat "tests/fir/golden/$name.rc")"
    fi
    if ! mask < "$OUT/$name.out" | cmp -s - "tests/fir/golden/$name.out"; then
        ok=0; why="$why stdout"
    fi
    case "$check" in
        full)
            cmp -s "$OUT/$name.err" "tests/fir/golden/$name.err" || { ok=0; why="$why stderr"; } ;;
        last)
            [[ "$(tail -n 1 "$OUT/$name.err")" == "$(cat "tests/fir/golden/$name.err")" ]] \
                || { ok=0; why="$why stderr"; } ;;
    esac
    if [[ -f "tests/fir/golden/$name.file" ]]; then
        written="$(sed -nE 's/.*--thresholds ([^ ]+).*/\1/p' <<< "$args")"
        if ! mask < "$written" | cmp -s - "tests/fir/golden/$name.file"; then
            ok=0; why="$why thresholds-file"
        fi
    fi
    if [[ $ok -eq 1 ]]; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL $name:$why"
        mask < "$OUT/$name.out" | diff "tests/fir/golden/$name.out" - | head -10
    fi
done < tests/fir/cases.txt

# The launcher: ./flow fir-g builds and runs the same tool.
for name in basics_fib_opts forms_json; do
    args="$(awk -F'\t' -v n="$name" '$1 == n { print $3 }' tests/fir/cases.txt)"
    # shellcheck disable=SC2086
    if ./flow fir-g $args 2> "$OUT/launcher.err" | cmp -s - "tests/fir/golden/$name.out"; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL launcher $name"
        cat "$OUT/launcher.err"
    fi
done

if [[ -s "$log" ]]; then
    echo "FAIL python was called:"
    cat "$log"
    fail=$((fail + 1))
fi

echo "fir gate: $pass passed, $fail failed"
[[ $fail -eq 0 ]]
