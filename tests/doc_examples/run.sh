#!/usr/bin/env bash
# Goldens for the documentation example checker (tools/doc_examples).
#
# Each case is tests/doc_examples/cases/<name>/ with:
#
#   root/        a documentation tree; *.md.in files become *.md in a
#                scratch copy, so the fixtures are not documentation of this
#                repository and the real checks never see them
#   cmd.N        the arguments of one run of scripts/check_doc_examples.sh,
#                with --root root added
#   out.N        expected stdout
#   err.N        expected stderr
#   rc.N         expected exit status
#   ledger.N     expected ledger after a --write-ledger run ("generated"
#                reads DATE)
#
# The goldens were recorded from the Python checker (scripts/
# check_doc_examples.py and friends) before it was deleted. The cases where
# the Flow checker differs on purpose are listed in KNOWN_DIFFERENCES.md.
#
# Python and python3 are stubbed out on PATH: the checker must not need them.
# The lessons command also runs on the real tutorials, with the structural
# checks the Python unit test made.
#
# Usage: tests/doc_examples/run.sh [case...]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-doc-examples-tests.XXXXXX")"
trap 'rm -rf "$work"' EXIT

stub="$work/bin"
mkdir -p "$stub"
for name in python python3; do
    printf '#!/bin/sh\necho "%s $*" >> "%s/python-calls.log"\nexit 127\n' "$name" "$work" > "$stub/$name"
    chmod +x "$stub/$name"
done
export PATH="$stub:$PATH"

cases=()
if [[ $# -gt 0 ]]; then
    for n in "$@"; do cases+=("tests/doc_examples/cases/$n"); done
else
    for d in tests/doc_examples/cases/*/; do cases+=("${d%/}"); done
fi

pass=0
fail=0
report_fail() {
    echo "FAIL $1"
    fail=$((fail + 1))
}

for case in "${cases[@]}"; do
    name="$(basename "$case")"
    for cmdf in "$case"/cmd.*; do
        n="${cmdf##*.}"
        run="$work/$name.$n"
        mkdir -p "$run"
        cp -R "$case/root" "$run/root"
        while IFS= read -r f; do
            mv "$f" "${f%.in}"
        done < <(find "$run/root" -name '*.md.in')
        read -r -a args < "$cmdf"
        set +e
        (cd "$run" && "$ROOT/scripts/check_doc_examples.sh" "${args[@]}" --root root \
            > "$run/stdout" 2> "$run/stderr")
        rc=$?
        set -e
        ok=1
        if [[ "$rc" != "$(cat "$case/rc.$n")" ]]; then
            echo "  $name.$n: exit $rc, expected $(cat "$case/rc.$n")"
            ok=0
        fi
        if ! diff -u "$case/out.$n" "$run/stdout" > "$run/out.diff"; then
            echo "  $name.$n: stdout differs"
            sed 's/^/    /' "$run/out.diff" | head -40
            ok=0
        fi
        if ! diff -u "$case/err.$n" "$run/stderr" > "$run/err.diff"; then
            echo "  $name.$n: stderr differs"
            sed 's/^/    /' "$run/err.diff" | head -20
            ok=0
        fi
        if [[ -f "$case/ledger.$n" ]]; then
            sed 's/"generated": "[0-9-]*"/"generated": "DATE"/' "$run/root/ledger.json" > "$run/ledger"
            if ! diff -u "$case/ledger.$n" "$run/ledger" > "$run/ledger.diff"; then
                echo "  $name.$n: ledger differs"
                sed 's/^/    /' "$run/ledger.diff" | head -40
                ok=0
            fi
        fi
        if [[ "$ok" -eq 1 ]]; then
            pass=$((pass + 1))
        else
            report_fail "$name.$n"
        fi
    done
done

# The tutorial lessons on the real docs: many, all with a main, all from
# docs/tutorials/ and none from its README.
if [[ $# -eq 0 ]]; then
    lessons="$work/lessons.json"
    scripts/check_doc_examples.sh lessons > "$lessons"
    total="$(grep -c '"path": ' "$lessons" || true)"
    tut="$(grep -o '"path": "docs/tutorials/[^"/]*\.md"' "$lessons" | grep -vc 'README.md' || true)"
    mains="$(grep -c 'function main' "$lessons" || true)"
    if [[ "$total" -gt 200 && "$tut" -eq "$total" && "$mains" -eq "$total" ]]; then
        pass=$((pass + 1))
    else
        echo "  lessons: $total lessons, $tut from docs/tutorials, $mains with a main"
        report_fail lessons
    fi
fi

if [[ -s "$work/python-calls.log" ]]; then
    echo "FAIL python was called:"
    cat "$work/python-calls.log"
    fail=$((fail + 1))
fi

echo "doc_examples: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
