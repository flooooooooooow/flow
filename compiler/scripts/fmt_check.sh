#!/usr/bin/env bash
# Formatter gate for flowc's `fmt` backend (compiler/src/fmt.flow).
#
# For every tracked .flow file that flowc parses, formats it once and
# checks three things:
#
#   preservation  the token and comment stream is unchanged
#                 (FLOWC_BACKEND=tokens on the source and on the result);
#   idempotence   formatting the result again changes nothing;
#   semantics     when the source compiles to C on flowc (bundle mode,
#                 FLOWC_DIR = the file's directory), the formatted file
#                 compiles to the same C, byte for byte.
#
#   ./compiler/scripts/fmt_check.sh                 # report
#   ./compiler/scripts/fmt_check.sh --check         # fail on any miss
#   ./compiler/scripts/fmt_check.sh --update-floor  # record the counts
#   ./compiler/scripts/fmt_check.sh --failures      # also list each miss
#
# --check fails when a file misses preservation, idempotence or semantics
# and is not listed in compiler/fmt_check/exceptions.txt, or when fewer
# files are checked than compiler/fmt_check/floor.txt records.
#
# FLOWC=path selects the binary; by default the checked-in bootstrap C is
# compiled to compiler/build/flowc_bootstrap. FMT_CHECK_JOBS sets the
# number of parallel workers (default 8).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DATA=compiler/fmt_check
FLOOR_FILE="$DATA/floor.txt"
EXCEPTIONS="$DATA/exceptions.txt"

# One file: print `<parse>\t<tokens>\t<idem>\t<sem>\t<path>`, each field
# ok / fail / skip. Runs inside a worker with its own scratch directory.
check_one() {
    local f="$1" work="$2"
    local d="$work/$$.$RANDOM"
    mkdir -p "$d"
    local base
    base="$(basename "$f")"
    local parse=ok tok=skip idem=skip sem=skip
    if ! FLOWC_BACKEND=fmt FLOWC_IN="$f" FLOWC_OUT="$d/once.flow" "$FLOWC" >/dev/null 2>&1; then
        parse=fail
    else
        FLOWC_BACKEND=tokens FLOWC_IN="$f" FLOWC_OUT="$d/src.tok" "$FLOWC" >/dev/null 2>&1 || true
        FLOWC_BACKEND=tokens FLOWC_IN="$d/once.flow" FLOWC_OUT="$d/once.tok" "$FLOWC" >/dev/null 2>&1 || true
        if [[ -s "$d/src.tok" || ! -s "$f" ]] && cmp -s "$d/src.tok" "$d/once.tok"; then
            tok=ok
        else
            tok=fail
        fi
        if FLOWC_BACKEND=fmt FLOWC_IN="$d/once.flow" FLOWC_OUT="$d/twice.flow" "$FLOWC" >/dev/null 2>&1 \
                && cmp -s "$d/once.flow" "$d/twice.flow"; then
            idem=ok
        else
            idem=fail
        fi
        # Semantics: compile the source and the formatted copy under the
        # same file name, so any path the C mentions is the same.
        local dir
        dir="$(dirname "$f")"
        mkdir -p "$d/a" "$d/b"
        cp "$f" "$d/a/$base"
        cp "$d/once.flow" "$d/b/$base"
        if FLOWC_BUNDLE=1 FLOWC_DIR="$dir" FLOWC_IN="$d/a/$base" FLOWC_OUT="$d/a.c" \
                "$FLOWC" >/dev/null 2>&1 && [[ -s "$d/a.c" ]]; then
            if FLOWC_BUNDLE=1 FLOWC_DIR="$dir" FLOWC_IN="$d/b/$base" FLOWC_OUT="$d/b.c" \
                    "$FLOWC" >/dev/null 2>&1 \
                    && cmp -s <(sed "s#$d/[ab]/##g" "$d/a.c") <(sed "s#$d/[ab]/##g" "$d/b.c"); then
                sem=ok
            else
                sem=fail
            fi
        fi
    fi
    printf '%s\t%s\t%s\t%s\t%s\n' "$parse" "$tok" "$idem" "$sem" "$f"
    rm -rf "$d"
}

if [[ "${1:-}" == "--one" ]]; then
    # Worker entry: --one <work dir> <file>...
    shift
    work="$1"
    shift
    for f in "$@"; do
        check_one "$f" "$work"
    done
    exit 0
fi

mode="${1:-}"
case "$mode" in
    ""|--check|--update-floor|--failures) ;;
    *) echo "usage: $0 [--check | --update-floor | --failures]" >&2; exit 2 ;;
esac

FLOWC="${FLOWC:-}"
if [[ -z "$FLOWC" ]]; then
    mkdir -p compiler/build
    FLOWC=compiler/build/flowc_bootstrap
    if [[ ! -x "$FLOWC" || compiler/bootstrap/flowc_stage_a.c -nt "$FLOWC" ]]; then
        ${CC:-cc} -O2 -w -o "$FLOWC" compiler/bootstrap/flowc_stage_a.c
    fi
fi
case "$FLOWC" in
    /*) ;;
    *) FLOWC="$ROOT/$FLOWC" ;;
esac
export FLOWC

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/work"

# Golden layouts: compiler/fixtures/fmt/<name>.flow formats to
# <name>.expected, and the expected text is already formatted.
golden_fail=0
golden_n=0
for src in compiler/fixtures/fmt/*.flow; do
    [[ -e "$src" ]] || continue
    want="${src%.flow}.expected"
    golden_n=$((golden_n + 1))
    if ! FLOWC_BACKEND=fmt FLOWC_IN="$src" FLOWC_OUT="$tmp/golden.flow" "$FLOWC" >/dev/null 2>&1 \
            || ! cmp -s "$tmp/golden.flow" "$want"; then
        echo "golden FAIL $src (expected $want)"
        diff "$want" "$tmp/golden.flow" | head -20 || true
        golden_fail=1
    fi
    if ! FLOWC_BACKEND=fmt FLOWC_IN="$want" FLOWC_OUT="$tmp/golden2.flow" "$FLOWC" >/dev/null 2>&1 \
            || ! cmp -s "$tmp/golden2.flow" "$want"; then
        echo "golden FAIL $want is not a fixed point"
        golden_fail=1
    fi
done

git ls-files '*.flow' | sort > "$tmp/files"
xargs -P "${FMT_CHECK_JOBS:-8}" -n 16 "$0" --one "$tmp/work" < "$tmp/files" \
    | sort -t $'\t' -k5 > "$tmp/results"

if [[ -f "$EXCEPTIONS" ]]; then
    { grep -v -e '^#' -e '^$' "$EXCEPTIONS" || true; } | sort > "$tmp/exceptions"
else
    : > "$tmp/exceptions"
fi

total=$(wc -l < "$tmp/files" | tr -d ' ')
parsed=$(awk -F'\t' '$1 == "ok"' "$tmp/results" | wc -l | tr -d ' ')
tok_ok=$(awk -F'\t' '$2 == "ok"' "$tmp/results" | wc -l | tr -d ' ')
idem_ok=$(awk -F'\t' '$3 == "ok"' "$tmp/results" | wc -l | tr -d ' ')
sem_n=$(awk -F'\t' '$4 != "skip"' "$tmp/results" | wc -l | tr -d ' ')
sem_ok=$(awk -F'\t' '$4 == "ok"' "$tmp/results" | wc -l | tr -d ' ')

echo "flowc fmt gate over ${total} tracked .flow files (${parsed} parse and were formatted)"
echo "  preservation: ${tok_ok}/${parsed}"
echo "  idempotence:  ${idem_ok}/${parsed}"
echo "  semantics:    ${sem_ok}/${sem_n} (files that compile to C)"
echo "  golden:       ${golden_n} fixture(s), $( ((golden_fail)) && echo FAIL || echo ok)"

awk -F'\t' '$1 == "ok" && ($2 == "fail" || $3 == "fail" || $4 == "fail") {print $5}' \
    "$tmp/results" | sort > "$tmp/misses"
comm -23 "$tmp/misses" "$tmp/exceptions" > "$tmp/new_misses"

if [[ "$mode" == "--failures" || -s "$tmp/new_misses" ]]; then
    if [[ -s "$tmp/misses" ]]; then
        echo
        echo "misses (preservation, idempotence, semantics):"
        awk -F'\t' '$1 == "ok" && ($2 == "fail" || $3 == "fail" || $4 == "fail") {
            printf "  %s  %s %s %s\n", $5, $2, $3, $4 }' "$tmp/results"
    fi
fi

if [[ "$mode" == "--update-floor" ]]; then
    mkdir -p "$DATA"
    printf 'formatted %s\nsemantics %s\n' "$parsed" "$sem_n" > "$FLOOR_FILE"
    echo
    echo "floor set: formatted ${parsed}, semantics ${sem_n}"
fi

if [[ "$mode" == "--check" ]]; then
    rc=0
    if (( golden_fail )); then
        echo "fmt gate: golden layout fixtures differ" >&2
        rc=1
    fi
    if [[ -s "$tmp/new_misses" ]]; then
        echo "fmt gate: files the formatter changes (not in $EXCEPTIONS):" >&2
        sed 's/^/  /' "$tmp/new_misses" >&2
        rc=1
    fi
    if [[ -f "$FLOOR_FILE" ]]; then
        floor_fmt=$(awk '$1 == "formatted" {print $2}' "$FLOOR_FILE")
        floor_sem=$(awk '$1 == "semantics" {print $2}' "$FLOOR_FILE")
        if (( parsed < ${floor_fmt:-0} )); then
            echo "fmt gate: ${parsed} files formatted < floor ${floor_fmt}" >&2
            rc=1
        fi
        if (( sem_n < ${floor_sem:-0} )); then
            echo "fmt gate: ${sem_n} files compared on C < floor ${floor_sem}" >&2
            rc=1
        fi
    fi
    if (( rc == 0 )); then
        echo
        echo "fmt gate OK"
    fi
    exit "$rc"
fi
