#!/usr/bin/env bash
# Parity gate for the constructs flowc lowers that were parse-only (#996):
# match or-patterns / guards / nested patterns, ui layout blocks, pipeline
# fork and choose blocks, declarative sort, [T; N], expr?, <a, b> vector
# literals, module blocks, and the unit / distinct declarations.
#
# Every file in compiler/parity_lowering/corpus.txt is built on flowc
# (bundle emit, cc) and, when it links, run with a timeout. The result is
# held to the Python host's, recorded as goldens in
# compiler/parity_lowering/expected.tsv:
#
#   file  status  exit  stdout-md5  diagnostic
#
# status is `accept` (the C compiles) or `reject`. exit and stdout-md5 are
# `-` when the program did not link or run on the Python host, or is listed
# in compiler/parity_lowering/norun.txt (timing output, GUI, long runs). For
# a rejected file, the diagnostic is the Python host's message, which the
# flowc output must contain; `-` skips that check.
#
#   ./compiler/scripts/parity_lowering.sh
#       flowc vs the goldens. Needs only a C compiler.
#
#   ./compiler/scripts/parity_lowering.sh --python <rev>
#       also build every corpus file with the Python host from git
#       revision <rev> and require the same results live. Needs python3.
#
#   ./compiler/scripts/parity_lowering.sh --write-golden <rev>
#       rewrite the goldens from the Python host at <rev>.
#
# The goldens were written from ff99639e (origin/main when the lowering
# landed; the Python host still carried all of these paths). The unit
# fixtures (compiler/fixtures/units_*.flow, #1008) were added from 5f36fc60.
# A Python type error is recorded as its first `✗` line, whole.
#
# Env: FLOWC_BIN=<path> tests that binary instead of building
# compiler/build/flowc_bootstrap from the checked-in bootstrap C.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DATA=compiler/parity_lowering
WORK=compiler/build/parity_lowering
mode="${1:-}"
rev="${2:-}"
rm -rf "$WORK"
mkdir -p "$WORK/flowc" "$WORK/python"

if [[ -n "${FLOWC_BIN:-}" ]]; then
    BIN="$FLOWC_BIN"
else
    BIN=compiler/build/flowc_bootstrap
    "${CC:-cc}" -O2 -w -o "$BIN" compiler/bootstrap/flowc_stage_a.c -lm
fi
echo "=== parity_lowering: flowc = ${BIN} ==="

grep -v '^#' "$DATA/corpus.txt" | sed '/^$/d' > "$WORK/corpus"
grep -v '^#' "$DATA/norun.txt" | sed '/^$/d' | cut -f1 > "$WORK/norun" || true
grep -v '^#' "$DATA/divergent.txt" | sed '/^$/d' | cut -f1 > "$WORK/divergent" || true

# hash_file <path>: md5 of a file, with md5sum or macOS md5.
hash_file() {
    if command -v md5sum >/dev/null 2>&1; then
        md5sum < "$1" | cut -c1-32
    else
        md5 -q "$1"
    fi
}

# timed <seconds> cmd...: run with an alarm so a hang is a failure.
timed() {
    local s="$1"
    shift
    perl -e 'alarm shift; exec @ARGV' "$s" "$@"
}

# result <host> <file> <log> <c-file> <out-dir>: print one TSV row.
result() {
    local host="$1" f="$2" log="$3" c="$4" dir="$5"
    local key="${f//\//__}"
    local status=reject exit_code=- md5=- diag=-
    if [[ -s "$c" ]] && "${CC:-cc}" -w -c -o "$dir/$key.o" "$c" -I"$(dirname "$f")" -Itests/lang 2>/dev/null; then
        status=accept
        if ! grep -qxF "$f" "$WORK/norun" \
            && "${CC:-cc}" -w -o "$dir/$key.bin" "$c" -I"$(dirname "$f")" -Itests/lang -lm 2>/dev/null; then
            set +e
            timed 20 "$dir/$key.bin" > "$dir/$key.out" 2>/dev/null </dev/null
            exit_code=$?
            set -e
            md5="$(hash_file "$dir/$key.out")"
            if [[ "$exit_code" -eq 142 ]]; then
                exit_code=timeout
                md5=-
            fi
        fi
    else
        if [[ "$host" == python ]]; then
            # A type error prints as `  ✗ message`; take the first one whole.
            diag="$(grep -m1 '✗ ' "$log" | sed -e 's/^.*✗ //' | cut -c1-200 || true)"
            if [[ -z "$diag" ]]; then
                diag="$(grep -m1 -E 'Error|error' "$log" | sed -e 's/^.*Error: //' -e 's/^.*error: //' | cut -c1-200 || true)"
            fi
            [[ -n "$diag" ]] || diag=-
        fi
    fi
    printf '%s\t%s\t%s\t%s\t%s\n' "$f" "$status" "$exit_code" "$md5" "$diag"
}

run_flowc() {
    : > "$WORK/flowc.tsv"
    while IFS= read -r f; do
        local key="${f//\//__}"
        set +e
        FLOWC_BUNDLE=1 FLOWC_DIR="$(dirname "$f")" FLOWC_IN="$f" FLOWC_OUT="$WORK/flowc/$key.c" \
            timed 60 "$BIN" > "$WORK/flowc/$key.log" 2>&1
        local code=$?
        if [[ "$code" -ne 0 ]]; then
            # Imports spelled from the repo root (tests/lang does this).
            FLOWC_BUNDLE=1 FLOWC_DIR=. FLOWC_IN="$f" FLOWC_OUT="$WORK/flowc/$key.c" \
                timed 60 "$BIN" >> "$WORK/flowc/$key.log" 2>&1
            code=$?
        fi
        set -e
        [[ "$code" -eq 0 ]] || rm -f "$WORK/flowc/$key.c"
        result flowc "$f" "$WORK/flowc/$key.log" "$WORK/flowc/$key.c" "$WORK/flowc" >> "$WORK/flowc.tsv"
    done < "$WORK/corpus"
}

run_python() {
    local r="$1"
    mkdir -p "$WORK/pyref"
    git archive "$r" src/flow | tar -x -C "$WORK/pyref"
    : > "$WORK/python.tsv"
    while IFS= read -r f; do
        local key="${f//\//__}"
        set +e
        PYTHONPATH="$WORK/pyref/src" timed 120 python3 -m flow.transpiler "$f" --c \
            -o "$WORK/python/$key.c" > "$WORK/python/$key.log" 2>&1
        local code=$?
        set -e
        [[ "$code" -eq 0 ]] || rm -f "$WORK/python/$key.c"
        result python "$f" "$WORK/python/$key.log" "$WORK/python/$key.c" "$WORK/python" >> "$WORK/python.tsv"
    done < "$WORK/corpus"
}

# compare <want.tsv> <label>: hold flowc.tsv to want.tsv.
compare() {
    local want="$1" label="$2"
    local n=0 same_status=0 same_run=0 same_diag=0 known=0 fail=0
    while IFS=$'\t' read -r f status exit_code md5 diag; do
        n=$((n + 1))
        if grep -qxF "$f" "$WORK/divergent"; then
            known=$((known + 1))
            continue
        fi
        local got
        got="$(grep -F "$f	" "$WORK/flowc.tsv" | head -1)"
        local g_status g_exit g_md5
        g_status="$(printf '%s' "$got" | cut -f2)"
        g_exit="$(printf '%s' "$got" | cut -f3)"
        g_md5="$(printf '%s' "$got" | cut -f4)"
        if [[ "$g_status" != "$status" ]]; then
            fail=$((fail + 1))
            echo "FAIL $f: $label $status, flowc $g_status" >&2
            continue
        fi
        same_status=$((same_status + 1))
        if [[ "$status" == reject ]]; then
            if [[ "$diag" != - ]] && ! grep -qF -- "$diag" "$WORK/flowc/${f//\//__}.log"; then
                fail=$((fail + 1))
                echo "FAIL $f: flowc diagnostic lacks: $diag" >&2
                continue
            fi
            same_diag=$((same_diag + 1))
            continue
        fi
        if [[ "$exit_code" == - || "$exit_code" == timeout ]]; then
            continue
        fi
        if [[ "$g_exit" != "$exit_code" || "$g_md5" != "$md5" ]]; then
            fail=$((fail + 1))
            echo "FAIL $f: $label exit $exit_code, flowc exit $g_exit (stdout $([[ "$g_md5" == "$md5" ]] && echo same || echo differs))" >&2
            continue
        fi
        same_run=$((same_run + 1))
    done < "$want"
    echo "$label: files=$n accept/reject=$same_status run=$same_run diagnostics=$same_diag known-divergent=$known fail=$fail"
    return "$fail"
}

if [[ "$mode" == "--write-golden" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --write-golden <rev>" >&2; exit 2; }
    run_python "$rev"
    {
        echo "# file	status	exit	stdout-md5	diagnostic (Python host at $rev)"
        cat "$WORK/python.tsv"
    } > "$DATA/expected.tsv"
    echo "wrote $(wc -l < "$WORK/python.tsv" | tr -d ' ') goldens from $rev"
    exit 0
fi

run_flowc
fail=0
grep -v '^#' "$DATA/expected.tsv" > "$WORK/expected"
compare "$WORK/expected" golden || fail=$((fail + $?))

if [[ "$mode" == "--python" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --python <rev>" >&2; exit 2; }
    run_python "$rev"
    compare "$WORK/python.tsv" "python@$rev" || fail=$((fail + $?))
fi

if [[ "$fail" -ne 0 ]]; then
    echo "parity_lowering: FAIL ($fail)"
    exit 1
fi
echo "parity_lowering: PASS"
