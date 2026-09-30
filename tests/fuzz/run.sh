#!/usr/bin/env bash
# Fuzz and crash-regression gate for flowc.
#
#   tests/fuzz/run.sh                         pins, deep nesting, 30s of mutation
#   tests/fuzz/run.sh --seconds 60 --seed 7   longer mutation run
#   tests/fuzz/run.sh --pins-only             crash pins and deep nesting only
#
# flowc must never crash. Each input goes through compiler/scripts/flowc_emit.sh
# (parse, resolve, type check, C emission). A crash is a signal (exit 128 and
# up) or no answer within 20 seconds; any other exit is flowc refusing the
# input. Pins and deep inputs must also say where: exit 0, or exit 1 with a
# `file:line:col:` diagnostic.
#
# Three kinds of input:
#
#   pins      tests/fuzz/crashes/*.flow, inputs that once crashed the retired
#             Python front end (known_crashes.json says how)
#   deep      nesting generated at 1000 and 20000 levels: parentheses,
#             unary minus, blocks, types and unclosed parentheses. flowc
#             stops at FLOWC_PARSE_MAX_DEPTH (compiler/src/parser.flow)
#             with a parse error; before that limit it overflowed its stack
#   mutation  tracked .flow files with lines deleted, duplicated or swapped,
#             cut at a byte, or given a stray token, seeded and repeatable
#
# This replaces tests/fuzz/run_fuzz.py and the pytest crash replays, which
# drove the Python parser in process. A crash leaves its input in the work
# directory and is printed with the command that reproduces it.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
cd "$ROOT" || exit 1

seconds="${FLOW_FUZZ_SECONDS:-30}"
seed=1234
pins_only=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --seconds) seconds="$2"; shift 2 ;;
        --seed) seed="$2"; shift 2 ;;
        --pins-only) pins_only=1; shift ;;
        *) echo "usage: $0 [--seconds N] [--seed N] [--pins-only]" >&2; exit 2 ;;
    esac
done

if [[ -z "${FLOWC_BIN:-}" ]]; then
    FLOWC_BIN="$ROOT/$(./compiler/scripts/ensure_flowc.sh)" || exit 1
    export FLOWC_BIN
fi

WORK="$(mktemp -d "${TMPDIR:-/tmp}/flow-fuzz.XXXXXX")"
keep=0
trap '[[ $keep -eq 1 ]] || rm -rf "$WORK"' EXIT

runs=0
crashes=0

# check NAME FILE [located]: run flowc on FILE and classify the result.
check() {
    local name="$1" f="$2" located="${3:-0}" rc
    runs=$((runs + 1))
    perl -e 'alarm shift; exec @ARGV' 20 \
        ./compiler/scripts/flowc_emit.sh "$f" "$WORK/out.c" >"$WORK/log" 2>&1
    rc=$?
    if [[ $rc -eq 0 ]]; then
        return 0
    fi
    if [[ $rc -lt 128 && $located -eq 0 ]]; then
        return 0
    fi
    if [[ $rc -eq 1 ]] && grep -qE '^[^:]+:[0-9]+:[0-9]+: ' "$WORK/log"; then
        return 0
    fi
    crashes=$((crashes + 1))
    keep=1
    local why="exit $rc"
    [[ $rc -eq 142 ]] && why="no answer in 20s"
    [[ $rc -gt 128 && $rc -ne 142 ]] && why="signal $((rc - 128))"
    [[ $rc -eq 1 ]] && why="exit 1 with no located diagnostic"
    echo "CRASH $name: $why"
    echo "  input: $f"
    echo "  rerun: compiler/scripts/flowc_emit.sh $f /tmp/out.c"
    sed -n '1,5s/^/  | /p' "$WORK/log"
    return 1
}

# Pins.
for f in tests/fuzz/crashes/*.flow; do
    check "pin $(basename "$f")" "$f" 1
done

# Deep nesting. gen N OPEN CORE CLOSE PREFIX SUFFIX writes one program.
gen() {
    G_N="$1" G_OPEN="$2" G_CORE="$3" G_CLOSE="$4" G_PRE="$5" G_POST="$6" awk 'BEGIN {
        n = ENVIRON["G_N"] + 0
        s = ENVIRON["G_PRE"]
        for (i = 0; i < n; i++) s = s ENVIRON["G_OPEN"]
        s = s ENVIRON["G_CORE"]
        for (i = 0; i < n; i++) s = s ENVIRON["G_CLOSE"]
        print s ENVIRON["G_POST"]
    }'
}
for n in 1000 20000; do
    gen "$n" "(" "1" ")" 'function main() -> i32 {
    let x: i32 = ' '
    return 0
}' > "$WORK/deep_paren_$n.flow"
    gen "$n" "-" "1" "" 'function main() -> i32 {
    let x: i32 = ' '
    return 0
}' > "$WORK/deep_neg_$n.flow"
    gen "$n" "if true {
" "let y: i32 = 1
" "}
" 'function main() -> i32 {
' 'return 0
}' > "$WORK/deep_if_$n.flow"
    gen "$n" "ptr<" "i32" ">" 'function f(p: ' ') {
}
function main() -> i32 {
    return 0
}' > "$WORK/deep_type_$n.flow"
    gen "$n" "(" "1" "" 'function main() -> i32 {
    let x: i32 = ' '
    return 0
}' > "$WORK/deep_unclosed_$n.flow"
done
for f in "$WORK"/deep_*.flow; do
    check "deep $(basename "$f" .flow)" "$f" 1
done

if [[ $pins_only -eq 0 ]]; then
    git ls-files 'tests/lang/*.flow' 'examples/*.flow' 'lib/stdlib/*.flow' > "$WORK/corpus.txt"
    ncorpus=$(wc -l < "$WORK/corpus.txt")
    deadline=$((SECONDS + seconds))
    i=0
    while [[ $SECONDS -lt $deadline ]]; do
        s=$((seed + i))
        pick=$(( (s * 2654435761) % ncorpus + 1 ))
        src="$(sed -n "${pick}p" "$WORK/corpus.txt")"
        out="$WORK/mut_$s.flow"
        awk -v seed="$s" '
            BEGIN { srand(seed); n = 0 }
            { line[++n] = $0 }
            END {
                if (n == 0) { print "("; exit }
                op = int(rand() * 5)
                a = int(rand() * n) + 1
                b = int(rand() * n) + 1
                split("( ) { } [ ] < > , ; : = . -> |> let fn function return if match @ \" 0 0.0", tok, " ")
                for (k = 1; k <= n; k++) {
                    if (op == 0 && k == a) continue
                    if (op == 1 && k == a) print line[k]
                    if (op == 2 && k == a) { print line[b]; continue }
                    if (op == 2 && k == b) { print line[a]; continue }
                    if (op == 3 && k == a) { print substr(line[k], 1, int(rand() * (length(line[k]) + 1))); exit }
                    if (op == 4 && k == a) {
                        c = int(rand() * (length(line[k]) + 1))
                        print substr(line[k], 1, c) tok[int(rand() * 21) + 1] substr(line[k], c + 1)
                        continue
                    }
                    print line[k]
                }
            }' "$src" > "$out"
        if check "mutation seed $s of $src" "$out"; then
            rm -f "$out"
        fi
        i=$((i + 1))
    done
fi

echo "fuzz: runs=$runs crashes=$crashes"
[[ $crashes -eq 0 ]]
