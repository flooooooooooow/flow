#!/usr/bin/env bash
# Transcript tests for the native host tools (flow repl, flow lsp).
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
    ./flow repl < "$input" > "$out" 2>&1
    check "$name" "${input%.in}.expected" "$out"
done

# LSP sessions: tests/tools/lsp/<case>.jsonl -> <case>.expected.
# Each input line is one JSON-RPC message; the framing script adds the
# Content-Length headers and the expected file holds the framed replies
# with one message per line.
for input in tests/tools/lsp/*.jsonl; do
    [ -e "$input" ] || continue
    name="lsp/$(basename "$input" .jsonl)"
    out="$work/$(basename "$input" .jsonl).out"
    FLOW_LSP_ROOT_URI="file://$ROOT" bash tests/tools/lsp_session.sh "$input" > "$out" 2>/dev/null
    check "$name" "${input%.jsonl}.expected" "$out"
done

echo "tool transcripts: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
