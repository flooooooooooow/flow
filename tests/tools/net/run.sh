#!/usr/bin/env bash
# Exchange tests for the two network tools written in Flow:
#
#   scripts/tools/playground_server  (scripts/playground_compile_server.sh)
#   scripts/tools/ws_echo_relay      (scripts/ws_echo_relay.sh)
#
# Each server is started on a free high port, driven with real requests,
# and stopped by PID. Replies are compared with goldens in
# tests/tools/net/expected, recorded from the Python servers these tools
# replaced, by pointing this script at them through NET_TEST_PLAYGROUND and
# NET_TEST_RELAY (a command line each; the script adds --port and the rest) with
# --update, before the Python was deleted.
#
# Playground replies are compared as status line, headers and body. Before
# the comparison the Server and Date headers are dropped (they name the
# implementation and the time), Content-Length is checked against the body
# and dropped, the generated C in "c_preview" is replaced by a marker, and
# the per-request temp directory is normalised. Raw requests (HTTP/0.9, bad
# request lines, header edge cases) go over bash's /dev/tcp.
#
# The relay is driven by tests/tools/net/ws_client.js, a raw-socket client
# (masked frames, every payload length form, ping, pong, close, split
# frames, two clients at once, plain TCP echo). It needs node; without node
# the relay half is skipped with a message.
#
# Usage:
#   tests/tools/net/run.sh            check
#   tests/tools/net/run.sh --update   rewrite the goldens
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
HERE=tests/tools/net
EXP="$HERE/expected"
UPDATE=0
[ "${1:-}" = "--update" ] && UPDATE=1

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-net-tests.XXXXXX")"
pids=()
cleanup() {
    local p
    for p in ${pids[@]+"${pids[@]}"}; do
        kill "$p" 2>/dev/null || true
        wait "$p" 2>/dev/null || true
    done
    rm -rf "$work"
}
trap cleanup EXIT

if [ -n "${NET_TEST_PLAYGROUND:-}" ]; then
    read -r -a playground_cmd <<< "$NET_TEST_PLAYGROUND"
else
    playground_cmd=("$ROOT/$(scripts/tools/build_tool.sh playground_server)")
fi
if [ -n "${NET_TEST_RELAY:-}" ]; then
    read -r -a relay_cmd <<< "$NET_TEST_RELAY"
else
    relay_cmd=("$ROOT/$(scripts/tools/build_tool.sh ws_echo_relay)")
fi
export FLOW_REPO_ROOT="$ROOT"

pass=0
fail=0
check() {
    local name="$1" expected="$2" actual="$3"
    if [ "$UPDATE" -eq 1 ]; then
        cp "$actual" "$expected"
        echo "updated $name"
        pass=$((pass + 1))
    elif cmp -s "$expected" "$actual"; then
        echo "PASS $name"
        pass=$((pass + 1))
    else
        echo "FAIL $name"
        diff -u "$expected" "$actual" | head -40 | cut -c1-300 || true
        fail=$((fail + 1))
    fi
}

# Start "$@" with a random free port substituted for PORT (and PORT2), and
# wait for its banner line matching $banner. Sets started_pid, port, port2.
start_server() {
    local banner="$1" log="$2"
    shift 2
    local try args a
    for try in 1 2 3 4 5 6 7 8; do
        port=$((20000 + RANDOM % 40000))
        port2=$((port + 1))
        args=()
        for a in "$@"; do
            a="${a//PORT2/$port2}"
            args+=("${a//PORT/$port}")
        done
        "${args[@]}" > "$log" 2> "$log.err" &
        started_pid=$!
        local waited=0
        while [ "$waited" -lt 100 ]; do
            if grep -q "$banner" "$log" 2>/dev/null; then
                pids+=("$started_pid")
                return 0
            fi
            if ! kill -0 "$started_pid" 2>/dev/null; then
                break
            fi
            sleep 0.1
            waited=$((waited + 1))
        done
        kill "$started_pid" 2>/dev/null || true
        wait "$started_pid" 2>/dev/null || true
    done
    echo "FAIL could not start: $*" >&2
    cat "$log.err" >&2 || true
    exit 1
}

# ---------------------------------------------------------------------------
# Playground compile server
# ---------------------------------------------------------------------------

# Normalise one raw HTTP reply (headers and body) on stdin.
normalise() {
    local LC_ALL=C raw head body declared
    raw="$(cat; printf x)"
    raw="${raw%x}"
    # Check Content-Length against the body when the reply has headers.
    if [[ "$raw" == *$'\r\n\r\n'* ]]; then
        head="${raw%%$'\r\n\r\n'*}"
        body="${raw#*$'\r\n\r\n'}"
        declared="$(printf '%s\n' "$head" | sed -n 's/^Content-Length: \([0-9]*\)\r*$/\1/p' | head -n 1)"
        # 204 and HEAD replies carry a length and no body.
        if [ -n "$declared" ] && [ -n "$body" ] && [ "$declared" -ne "${#body}" ]; then
            printf 'CONTENT-LENGTH MISMATCH declared=%s body=%s\n' "$declared" "${#body}"
        fi
        # A served file is checked against the file, then replaced by its name.
        if [ -n "${SERVED_FILE:-}" ]; then
            local want
            want="$(cat "$SERVED_FILE"; printf x)"
            if [ "$body" = "${want%x}" ]; then
                raw="$head"$'\r\n\r\n'"<$SERVED_FILE>"
            else
                raw="$head"$'\r\n\r\n'"<body differs from $SERVED_FILE>"
            fi
        fi
    fi
    printf '%s' "$raw" \
        | { grep -v -e '^Server: ' -e '^Date: ' -e '^Content-Length: ' || true; } \
        | sed -E \
            -e 's#"c_preview": "([^"\\]|\\.)*"#"c_preview": "<C>"#' \
            -e 's#(/[^/" \\]+)*/flow-playground-[A-Za-z0-9_]{8}#TMP/flow-playground-X#g' \
            -e 's#(main\.flow:[0-9]+:[0-9]+: )[^"]*#\1<flowc message>#'
}

# curl a request; the reply (headers and body) goes through normalise.
http_case() {
    local name="$1"
    shift
    curl -s -i --max-time 120 "$@" > "$work/pg_$name.raw" || true
    normalise < "$work/pg_$name.raw" > "$work/pg_$name.txt"
    check "playground/$name" "$EXP/playground_$name.txt" "$work/pg_$name.txt"
}

# Send raw bytes (printf format) over /dev/tcp and keep the whole reply.
raw_case() {
    local name="$1" fmt="$2"
    (
        exec 3<>"/dev/tcp/127.0.0.1/$port"
        # shellcheck disable=SC2059 # the format is the request
        printf "$fmt" >&3
        cat <&3
    ) > "$work/pg_$name.raw" 2>/dev/null || true
    normalise < "$work/pg_$name.raw" > "$work/pg_$name.txt"
    check "playground/$name" "$EXP/playground_$name.txt" "$work/pg_$name.txt"
}

start_server "compile API on" "$work/playground.log" \
    "${playground_cmd[@]}" --port PORT --run-timeout 1.5 --transpile-timeout=60
U="http://127.0.0.1:$port"
printf 'FLOW playground compile API on http://127.0.0.1:PORT/compile\n' > "$work/banner"
sed -n '1p' "$work/playground.log" | sed "s/:$port\//:PORT\//" > "$work/banner.got"
check "playground/banner" "$work/banner" "$work/banner.got"

HELLO='{"source":"function main() -> i32 {\n    println(\"hi é\")\n    return 3\n}\n"}'
LOOP='{"source":"function main() -> i32 {\n    let mut i: i64 = 0\n    while true {\n        i = i + 1\n    }\n    return 0\n}\n"}'

http_case health "$U/health"
http_case root "$U/?x=1"
http_case origin_local -H 'Origin: http://localhost:4000' "$U/health"
http_case origin_other -H 'Origin: http://evil.com' "$U/health"
http_case origin_null -H 'Origin: null' "$U/health"
http_case options -X OPTIONS "$U/compile"
http_case get_404 "$U/nope"
http_case flow_src_dotdot --path-as-is "$U/flow-src/../x"
http_case flow_src_missing "$U/flow-src/lexer.py"
SERVED_FILE=docs/playground/pyodide.html http_case pyodide "$U/pyodide"
http_case post_404 -X POST -d '{}' "$U/other"
http_case post_query -X POST -d '{"source":"x"}' "$U/compile?x=1"
http_case post_empty -X POST -H 'Content-Length: 0' "$U/compile"
http_case post_bad_json -X POST -d 'not json' "$U/compile"
http_case post_no_source -X POST -d '{"target":"c"}' "$U/compile"
http_case post_blank_source -X POST -d '{"source":"   \n"}' "$U/compile"
http_case post_target_c -X POST -d '{"source":"function main() -> i32 {\n    println(\"hi\")\n    return 0\n}\n","target":"c"}' "$U/compile/"
http_case post_native_exit3 -X POST -d "$HELLO" "$U/compile"
http_case post_transpile_error -X POST -d '{"source":"function main( {"}' "$U/compile"
http_case post_target_number -X POST -d '{"source":"function main() -> i32 {\n    return 0\n}\n","target":5}' "$U/compile"
http_case post_crash -X POST -d '{"source":"extern {\n    function abort() -> void\n}\nfunction main() -> i32 {\n    abort()\n    return 0\n}\n"}' "$U/compile"
http_case post_not_object -X POST -d '[1,2]' "$U/compile"
http_case post_bad_length -X POST -H 'Content-Length: abc' -d 'x' "$U/compile"
printf '{"source":"' > "$work/big.json"
head -c 65600 /dev/zero | tr '\0' 'a' >> "$work/big.json"
printf '"}' >> "$work/big.json"
head -c 70000 /dev/zero | tr '\0' 'a' > "$work/big.src"
http_case post_body_too_large -X POST --data-binary @"$work/big.src" "$U/compile"
http_case post_source_too_large -X POST --data-binary @"$work/big.json" "$U/compile"
http_case put -X PUT -d x "$U/compile"

# A program that never ends is killed at --run-timeout, and /health answers
# while it runs.
curl -s -i --max-time 60 -X POST -d "$LOOP" "$U/compile" > "$work/pg_run_timeout.raw" &
loop_pid=$!
sleep 0.5
t0=$SECONDS
http_case health_during_run "$U/health"
if [ $((SECONDS - t0)) -gt 1 ]; then
    echo "FAIL playground/concurrent: /health waited for the running program"
    fail=$((fail + 1))
fi
wait "$loop_pid" || true
normalise < "$work/pg_run_timeout.raw" > "$work/pg_run_timeout.txt"
check "playground/run_timeout" "$EXP/playground_run_timeout.txt" "$work/pg_run_timeout.txt"

raw_case garbage 'GARBAGE\r\n\r\n'
raw_case http09_get 'GET /health\r\n\r\n'
raw_case http09_post 'POST /compile\r\n\r\n'
raw_case bad_version 'GET / FOO/1.0\r\n\r\n'
raw_case bad_version_digits 'GET / HTTP/1.x\r\n\r\n'
raw_case http2 'GET / HTTP/2.0\r\n\r\n'
raw_case four_words 'GET / x HTTP/1.1\r\n\r\n'
raw_case head 'HEAD / HTTP/1.1\r\n\r\n'
raw_case lf_only 'GET /health HTTP/1.0\nOrigin: http://localhost:9\n\n'
raw_case slash_slash 'GET //health HTTP/1.0\r\n\r\n'
raw_case origin_spaces 'GET /health HTTP/1.0\r\norigin:   http://127.0.0.1:1234  \r\n\r\n'
raw_case origin_userinfo 'GET /health HTTP/1.0\r\nOrigin: http://evil.com@localhost:80\r\n\r\n'
raw_case origin_no_scheme 'GET /health HTTP/1.0\r\nOrigin: localhost:80\r\n\r\n'
raw_case origin_upper 'GET /health HTTP/1.0\r\nOrigin: HTTP://LOCALHOST:80\r\n\r\n'
raw_case post_negative_length 'POST /compile HTTP/1.0\r\nContent-Length: -5\r\n\r\n'
raw_case post_bad_utf8 'POST /compile HTTP/1.0\r\nContent-Length: 14\r\n\r\n{"source":"\xff"}'
raw_case get_fragment 'GET /health#x HTTP/1.0\r\n\r\n'

# ---------------------------------------------------------------------------
# WebSocket echo relay
# ---------------------------------------------------------------------------

if command -v node >/dev/null 2>&1; then
    start_server "WebSocket echo relay on" "$work/relay.log" \
        "${relay_cmd[@]}" --port PORT --tcp-port PORT2
    printf 'TCP echo relay on 127.0.0.1:PORT2\nWebSocket echo relay on 127.0.0.1:PORT\n' > "$work/relay_banner"
    sed -e "s/:$port2\$/:PORT2/" -e "s/:$port\$/:PORT/" "$work/relay.log" > "$work/relay_banner.got"
    check "relay/banner" "$work/relay_banner" "$work/relay_banner.got"
    node "$HERE/ws_client.js" "$port" "$port2" > "$work/relay.txt" 2>&1 || true
    check "relay/transcript" "$EXP/relay.txt" "$work/relay.txt"
else
    echo "SKIP relay: node is not on PATH"
fi

echo "net tools: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
