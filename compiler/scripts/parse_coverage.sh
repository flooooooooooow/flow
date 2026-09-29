#!/usr/bin/env bash
# Parse coverage of the self-hosted flowc front end.
#
# Runs flowc's lexer and parser (FLOWC_PARSE_ONLY=1) on every tracked .flow
# file and reports how many parse. Files the Python reference parser also
# rejects are listed in compiler/parse_coverage/python_rejects.txt and are
# left out, so the count measures only the gap between the two parsers.
#
#   ./compiler/scripts/parse_coverage.sh                 # report + histogram
#   ./compiler/scripts/parse_coverage.sh --check         # fail if below the floor
#   ./compiler/scripts/parse_coverage.sh --update-floor  # record the current count
#   ./compiler/scripts/parse_coverage.sh --failures      # also list each failure
#
# FLOWC=path selects the binary. By default the checked-in bootstrap C is
# compiled to compiler/build/flowc_bootstrap, so the gate needs only a C
# compiler.
#
# The reference list is recorded once with the Python parser and checked in.
# To refresh it after adding files, run from the repo root:
#
#   git ls-files '*.flow' | PYTHONPATH=src python3 -c 'import sys
#   from flow.parser import parse_flow_code
#   for f in sys.stdin.read().split():
#       try: parse_flow_code(open(f, encoding="utf-8").read())
#       except BaseException: print(f)' > compiler/parse_coverage/python_rejects.txt
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DATA=compiler/parse_coverage
REJECTS="$DATA/python_rejects.txt"
FLOOR_FILE="$DATA/floor.txt"
mode="${1:-}"

FLOWC="${FLOWC:-}"
if [[ -z "$FLOWC" ]]; then
    mkdir -p compiler/build
    FLOWC=compiler/build/flowc_bootstrap
    if [[ ! -x "$FLOWC" || compiler/bootstrap/flowc_stage_a.c -nt "$FLOWC" ]]; then
        ${CC:-cc} -O2 -w -o "$FLOWC" compiler/bootstrap/flowc_stage_a.c -lm
    fi
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

git ls-files '*.flow' | sort > "$tmp/all"
if [[ -f "$REJECTS" ]]; then
    grep -v '^#' "$REJECTS" | sort > "$tmp/rejects"
else
    : > "$tmp/rejects"
fi
comm -23 "$tmp/all" "$tmp/rejects" > "$tmp/files"

: > "$tmp/results"
while IFS= read -r f; do
    if out="$(FLOWC_IN="$f" FLOWC_PARSE_ONLY=1 "$FLOWC" 2>&1)"; then
        printf 'ok\t%s\n' "$f" >> "$tmp/results"
    else
        line="$(printf '%s\n' "$out" | grep -m1 'parse error:' || true)"
        if [[ -z "$line" ]]; then
            line="$f:0:0: parse error: no diagnostic ($(printf '%s' "$out" | head -1))"
        fi
        printf 'fail\t%s\t%s\n' "$f" "$line" >> "$tmp/results"
    fi
done < "$tmp/files"

group_of() {
    case "$1" in
        examples/verify/*) echo "examples/verify" ;;
        examples/*) echo "examples (other)" ;;
        lib/stdlib/*) echo "lib/stdlib" ;;
        tests/lang/*) echo "tests/lang" ;;
        compiler/*) echo "compiler" ;;
        *) echo "other" ;;
    esac
}

total=$(wc -l < "$tmp/files" | tr -d ' ')
pass=$(grep -c '^ok' "$tmp/results" || true)
fail=$((total - pass))
skipped=$(wc -l < "$tmp/rejects" | tr -d ' ')

echo "flowc parse coverage: ${pass}/${total} parse, ${fail} fail (${skipped} files skipped: Python parser rejects them too)"
echo
echo "by area:"
awk -F'\t' '{print $1 "\t" $2}' "$tmp/results" | while IFS=$'\t' read -r st f; do
    printf '%s\t%s\n' "$(group_of "$f")" "$st"
done | sort | awk -F'\t' '
    { t[$1]++; if ($2 == "ok") p[$1]++ }
    END { for (g in t) printf "  %-18s %5d / %5d\n", g, p[g] + 0, t[g] }' | sort

if (( fail > 0 )); then
    echo
    echo "failing token (count):"
    grep '^fail' "$tmp/results" | cut -f3 \
        | sed -E 's/.*parse error: unexpected ([a-z ]+) (.*) \(byte [0-9]+\)$/\1 \2/' \
        | sed -E "s/^(integer|float|string) .*/\\1 literal/" \
        | sort | uniq -c | sort -rn | head -40
fi

if [[ "$mode" == "--failures" ]]; then
    echo
    echo "failures:"
    grep '^fail' "$tmp/results" | cut -f3 | sed 's/^/  /'
fi

if [[ "$mode" == "--update-floor" ]]; then
    mkdir -p "$DATA"
    echo "$pass" > "$FLOOR_FILE"
    echo
    echo "floor set to $pass"
fi

if [[ "$mode" == "--check" ]]; then
    floor=0
    if [[ -f "$FLOOR_FILE" ]]; then
        floor=$(tr -d ' \n' < "$FLOOR_FILE")
    fi
    echo
    if (( pass < floor )); then
        echo "parse coverage regressed: ${pass} < floor ${floor}" >&2
        echo "files flowc cannot parse:" >&2
        grep '^fail' "$tmp/results" | cut -f3 | sed 's/^/  /' >&2
        echo "If files were deleted rather than broken, lower the floor with" >&2
        echo "./compiler/scripts/parse_coverage.sh --update-floor" >&2
        exit 1
    fi
    echo "parse coverage OK: ${pass} >= floor ${floor}"
    if (( pass > floor )); then
        echo "(run ./compiler/scripts/parse_coverage.sh --update-floor to raise the floor)"
    fi
fi
