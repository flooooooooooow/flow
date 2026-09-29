#!/usr/bin/env bash
# Parity test for `flow analyze` (tools/analyze/main.flow).
#
# Each line of tests/tools/analyze/cases.txt is a case name and the
# arguments to `flow analyze`. The goldens in tests/tools/analyze/expected
# were recorded from the Python commands this tool replaced,
# src/flow/wcet_analysis.py and src/flow/misra_scan.py, before they were
# deleted:
#
#   <case>.stdout stdout, exact bytes
#   <case>.rc    exit code
#   <case>.err   stderr, exact bytes, where Python printed a message
#                (argparse usage errors, "not found", BUDGET EXCEEDED).
#                Cases where Python died with a traceback (a parse error,
#                a directory, a missing C file) check the exit code only.
#
# One recording detail: the Python WCET analysis kept each function's
# callees in a set, so when two callees tied for the deepest chain the
# printed chain depended on the string hash seed. The goldens were recorded
# with the callees in first-call order, which is what the Flow tool does.
#
# The same comparison over every .flow file under examples/ and tests/lang
# (1685 files: 1514 analyzed, 171 rejected by both) matched byte for byte
# when the Python version was removed.
#
# python and python3 are stubbed out on PATH, so a pass also shows the
# command needs no Python.
#
# Usage:
#   tests/tools/analyze/run.sh            check
#   tests/tools/analyze/run.sh --update   rewrite the goldens from the Flow tool
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
HERE=tests/tools/analyze
UPDATE=0
[ "${1:-}" = "--update" ] && UPDATE=1

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-analyze-tests.XXXXXX")"
trap 'rm -rf "$work"' EXIT

mkdir -p "$work/bin"
for name in python python3; do
    cat > "$work/bin/$name" <<EOF
#!/bin/sh
echo "$name \$*" >> "$work/python-calls.log"
exit 127
EOF
    chmod +x "$work/bin/$name"
done
export PATH="$work/bin:$PATH"
unset COLUMNS

# Build the tool once so its build output stays out of the cases.
if ! ./flow analyze --help > "$work/build.log" 2>&1; then
    cat "$work/build.log"
    echo "tests/tools/analyze: could not build flow analyze" >&2
    exit 1
fi

pass=0
fail=0
while IFS= read -r line; do
    case "$line" in ''|'#'*) continue ;; esac
    read -r -a words <<< "$line"
    name="${words[0]}"
    args=()
    stdin=/dev/null
    i=1
    while [ "$i" -lt "${#words[@]}" ]; do
        if [ "${words[$i]}" = "<" ]; then
            stdin="${words[$((i + 1))]}"
            i=$((i + 2))
            continue
        fi
        args+=("${words[$i]}")
        i=$((i + 1))
    done
    out="$work/$name.out"
    err="$work/$name.err"
    rc=0
    ./flow analyze "${args[@]}" < "$stdin" > "$out" 2> "$err" || rc=$?
    exp="$HERE/expected/$name"
    if [ "$UPDATE" -eq 1 ]; then
        cp "$out" "$exp.stdout"
        echo "$rc" > "$exp.rc"
        [ -f "$exp.err" ] && cp "$err" "$exp.err"
        pass=$((pass + 1))
        continue
    fi
    ok=1
    if ! cmp -s "$exp.stdout" "$out"; then
        ok=0
        echo "FAIL $name: stdout"
        diff -u "$exp.stdout" "$out" | head -40 || true
    fi
    if [ "$(cat "$exp.rc")" != "$rc" ]; then
        ok=0
        echo "FAIL $name: exit $rc, expected $(cat "$exp.rc")"
    fi
    if [ -f "$exp.err" ] && ! cmp -s "$exp.err" "$err"; then
        ok=0
        echo "FAIL $name: stderr"
        diff -u "$exp.err" "$err" | head -20 || true
    fi
    if [ "$ok" -eq 1 ]; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
    fi
done < "$HERE/cases.txt"

if [ -s "$work/python-calls.log" ]; then
    echo "FAIL: flow analyze ran Python:"
    cat "$work/python-calls.log"
    fail=$((fail + 1))
fi

echo "flow analyze: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
