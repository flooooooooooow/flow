#!/usr/bin/env bash
# Transcript test for the native language server (`flow lsp`,
# tools/lsp/main.flow).
#
# Each session in tests/tools/lsp/sessions/<case>.lsp is a list of
# JSON-RPC messages. The script frames them with Content-Length headers,
# pipes them into the server, splits the reply stream back into one JSON
# body per line and compares it with:
#
#   <case>.expected      the native server's output (exact bytes)
#   <case>.python        what the retired Python server (src/flow/lsp_server.py)
#                        answered to the same session, recorded before it was
#                        deleted
#   <case>.accepted.diff `diff` of the two after the normalization below; every
#                        hunk is explained in tests/tools/lsp/ACCEPTED.md
#
# A case passes when the native output equals <case>.expected and the diff
# against the Python recording equals <case>.accepted.diff, so the native
# server can only differ from the Python one in the ways that were reviewed.
#
# Session syntax, one item per line:
#   # comment                       ignored
#   @sleep                          wait until every request sent so far is
#                                   answered, then 0.5 s (lets a debounced
#                                   publish land)
#   @open <uri> <file>              didOpen with the file's text
#   @change <uri> <file> <version>  didChange (full text) with the file's text
#   {...}                           any other message, sent as written
# In every item, @ROOT@ stands for the repository root, and <file> is a path
# relative to it.
#
# Usage:
#   tests/tools/lsp/run.sh              check (needs no Python)
#   tests/tools/lsp/run.sh --update     rewrite <case>.expected and
#                                       <case>.accepted.diff from the current
#                                       native output
#   FLOW_LSP_CMD="..." tests/tools/lsp/run.sh --record <suffix>
#                                       run the sessions through another
#                                       server command and save <case>.<suffix>
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
cd "$ROOT"
HERE="tests/tools/lsp"
MODE="check"
SUFFIX=""
case "${1:-}" in
    --update) MODE="update" ;;
    --record) MODE="record"; SUFFIX="${2:?--record needs a suffix}" ;;
    "") ;;
    *) echo "usage: $0 [--update | --record <suffix>]" >&2; exit 2 ;;
esac

command -v jq >/dev/null || { echo "tests/tools/lsp: jq is required" >&2; exit 2; }

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-lsp-tests.XXXXXX")"
trap 'rm -rf "$work"' EXIT

# Server under test. The native server is built once, up front, so its
# build chatter stays out of the timing of the first session.
if [ -n "${FLOW_LSP_CMD:-}" ]; then
    SERVER=(bash -c "$FLOW_LSP_CMD")
else
    ./flow lsp --build >/dev/null
    SERVER=(./flow lsp)
fi

frame() {
    local body="$1"
    local n
    n="$(printf '%s' "$body" | LC_ALL=C wc -c | tr -d ' ')"
    printf 'Content-Length: %s\r\n\r\n%s' "$n" "$body"
}

# Wait until the reply stream in $1 answers request id $2 (JSON form).
await_reply() {
    local replies="$1" id="$2" tries=0
    [ -n "$id" ] || return 0
    while ! grep -Fq "\"id\": $id, " "$replies" 2>/dev/null; do
        tries=$((tries + 1))
        [ "$tries" -gt 1200 ] && return 0
        sleep 0.05
    done
}

# Session file -> framed JSON-RPC stream on stdout. Runs as the writer end
# of the pipe so @sleep pauses the client, as an editor would. $2 is the
# file receiving the server's replies.
feed() {
    local session="$1" replies="$2" line uri file version body last_id=""
    while IFS= read -r line || [ -n "$line" ]; do
        line="${line//@ROOT@/$ROOT}"
        case "$line" in
            ""|"#"*) continue ;;
            "@sleep") await_reply "$replies" "$last_id"; sleep 0.5; continue ;;
            "@open "*)
                read -r _ uri file <<<"$line"
                body="$(jq -cn --arg uri "$uri" --rawfile text "$file" \
                    '{jsonrpc: "2.0", method: "textDocument/didOpen",
                      params: {textDocument: {uri: $uri, languageId: "flow",
                                              version: 1, text: $text}}}')"
                ;;
            "@change "*)
                read -r _ uri file version <<<"$line"
                body="$(jq -cn --arg uri "$uri" --rawfile text "$file" \
                    --argjson v "$version" \
                    '{jsonrpc: "2.0", method: "textDocument/didChange",
                      params: {textDocument: {uri: $uri, version: $v},
                               contentChanges: [{text: $text}]}}')"
                ;;
            *)
                body="$line"
                if [ "$(jq -r 'has("id") and has("method")' <<<"$body")" = "true" ]; then
                    last_id="$(jq -c '.id' <<<"$body")"
                fi
                ;;
        esac
        frame "$body"
        # Hold `exit` until everything before it is answered.
        case "$body" in
            *'"method":"shutdown"'*) await_reply "$replies" "$last_id" ;;
        esac
    done < "$session"
}

# Framed reply stream -> one JSON body per line. Checks that every
# Content-Length matches its body.
deframe() {
    tr -d '\r' | LC_ALL=C awk '
        function take(s) {
            if (s ~ /^Content-Length: [0-9]+$/) { want = substr(s, 17) + 0; return }
            if (s != "") { print "FRAMING ERROR: " s; bad = 1 }
        }
        BEGIN { want = -1 }
        {
            line = $0
            if (want < 0) { take(line); next }
            if (line == "") next
            body = substr(line, 1, want)
            if (length(body) != want) { print "FRAMING ERROR: short body"; bad = 1 }
            print body
            rest = substr(line, length(body) + 1)
            want = -1
            take(rest)
        }
        END { exit bad }'
}

run_session() {
    local session="$1" out="$2"
    : > "$out.framed"
    feed "$session" "$out.framed" | "${SERVER[@]}" > "$out.framed" 2>"$out.err" || true
    deframe < "$out.framed" > "$out.raw" || true
    sed "s#$ROOT#@ROOT@#g" "$out.raw" > "$out"
}

pass=0
fail=0
for session in "$HERE"/sessions/${FLOW_LSP_ONLY:-*}.lsp; do
    name="$(basename "$session" .lsp)"
    base="$HERE/$name"
    out="$work/$name.out"
    run_session "$session" "$out"
    if [ -n "${FLOW_LSP_KEEP:-}" ]; then
        mkdir -p "$FLOW_LSP_KEEP"
        cp "$out" "$out.err" "$FLOW_LSP_KEEP/"
    fi
    if [ "$MODE" = "record" ]; then
        cp "$out" "$base.$SUFFIX"
        echo "recorded $name.$SUFFIX"
        continue
    fi
    # Python wrote U+2014 in its hover prose; the Flow catalogs use a plain
    # hyphen. Normalize that one spelling before diffing (ACCEPTED.md).
    accepted="$work/$name.accepted"
    if [ -f "$base.python" ]; then
        sed 's/ \\u2014 / - /g; s/\\u2014/-/g' "$base.python" > "$work/$name.py"
        diff "$work/$name.py" "$out" > "$accepted" || true
    fi
    if [ "$MODE" = "update" ]; then
        cp "$out" "$base.expected"
        [ -f "$base.python" ] && cp "$accepted" "$base.accepted.diff"
        echo "updated $name"
        pass=$((pass + 1))
        continue
    fi
    ok=1
    if ! cmp -s "$base.expected" "$out"; then
        echo "FAIL $name: output differs from $name.expected"
        diff "$base.expected" "$out" | head -40 || true
        head -20 "$out.err" || true
        ok=0
    fi
    if [ -f "$base.python" ] && ! cmp -s "$base.accepted.diff" "$accepted"; then
        echo "FAIL $name: difference from the Python recording changed"
        diff "$base.accepted.diff" "$accepted" | head -40 || true
        ok=0
    fi
    if [ "$ok" -eq 1 ]; then
        echo "PASS $name"
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
    fi
done

[ "$MODE" = "record" ] && exit 0
echo "lsp transcripts: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
