#!/usr/bin/env bash
# Transcript tests for the native host tools written in Flow (flow repl,
# flow lsp).
#
# Each case is an input file fed to the tool on stdin and the exact bytes
# the tool is expected to write back. Nothing here needs Python.
#
# Usage: tests/tools/run.sh [--update]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
UPDATE=0
if [ "${1:-}" = "--update" ]; then
    UPDATE=1
fi

pass=0
fail=0
work="$(mktemp -d "${TMPDIR:-/tmp}/flow-tool-tests.XXXXXX")"
trap 'rm -rf "$work"' EXIT

check() {
    local name="$1" expected="$2" actual="$3"
    if [ "$UPDATE" -eq 1 ]; then
        cp "$actual" "$expected"
        echo "updated $name"
        pass=$((pass + 1))
        return
    fi
    if cmp -s "$expected" "$actual"; then
        echo "PASS $name"
        pass=$((pass + 1))
    else
        echo "FAIL $name"
        diff -u "$expected" "$actual" | head -60 || true
        fail=$((fail + 1))
    fi
}

# REPL sessions: tests/tools/repl/<case>.in -> <case>.expected
for input in tests/tools/repl/*.in; do
    [ -e "$input" ] || continue
    name="repl/$(basename "$input" .in)"
    out="$work/$(basename "$input" .in).out"
    # stderr carries one-time build chatter (flowc, the tool itself), so
    # only stdout is compared; stderr is shown when a case fails.
    ./flow repl < "$input" > "$out" 2> "$out.err"
    check "$name" "${input%.in}.expected" "$out"
    if [ "$UPDATE" -eq 0 ] && ! cmp -s "${input%.in}.expected" "$out"; then
        cat "$out.err"
    fi
done

echo "tool transcripts: $pass passed, $fail failed"

# Language server sessions (flow lsp): tests/tools/lsp/run.sh.
lsp_status=0
if [ "$UPDATE" -eq 1 ]; then
    tests/tools/lsp/run.sh --update || lsp_status=$?
else
    tests/tools/lsp/run.sh || lsp_status=$?
fi

[ "$fail" -eq 0 ] && [ "$lsp_status" -eq 0 ]
