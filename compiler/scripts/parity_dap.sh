#!/usr/bin/env bash
# Parity gate for `flow dap`, the Debug Adapter Protocol server in
# tools/dap/main.flow (it was src/flow/dap_server.py).
#
# Each session feeds scripted client messages to the server, one every
# half second so the order of replies is fixed, and records the bytes the
# server wrote to the client and its exit code. Sessions that reach
# lldb-dap run a fake one (a shell script) that logs every message it gets
# and answers each with a canned reply holding non-ASCII text and floats,
# so the log shows the launch rewrite and both directions show the
# re-serialisation. Results are compared with tests/dap/golden/.
#
#   ./compiler/scripts/parity_dap.sh
#       the Flow server, with python and python3 stubbed out on PATH.
#
#   ./compiler/scripts/parity_dap.sh --write-golden <rev>
#       rewrite the goldens from the Python server at git revision <rev>
#       (the last one is e6a7f046), with _find_lldb_dap patched to the fake
#       (or to None) and REPO set to this checkout.
#
# Normalised: the checkout and work directory paths.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
cd "$ROOT"

GOLD="$ROOT/tests/dap/golden"
WORK="$ROOT/compiler/build/parity_dap"
mode="${1:-}"
rev="${2:-}"
export LC_ALL=C

rm -rf "$WORK"
mkdir -p "$WORK"

# ---------------------------------------------------------------- fake lldb-dap
FAKE="$WORK/fake-lldb-dap"
cat > "$FAKE" <<'EOF'
#!/bin/sh
# Logs each DAP message it reads to $FAKE_LOG and answers it.
export LC_ALL=C
send() {
    n=$(printf '%s' "$1" | wc -c | tr -d ' ')
    printf 'Content-Length: %s\r\n\r\n%s' "$n" "$1"
}
send '{"seq":1,"type":"event","event":"output","body":{"category":"console","output":"fake lldb-dap ready\n"}}'
count=1
while :; do
    len=""
    got=0
    while IFS= read -r line; do
        got=1
        line=$(printf '%s' "$line" | tr -d '\r')
        [ -z "$line" ] && break
        case "$line" in
            Content-Length:*) len=$(printf '%s' "${line#Content-Length:}" | tr -d ' ') ;;
        esac
    done
    [ "$got" = 1 ] && [ -n "$len" ] || exit 0
    body=$(dd bs=1 count="$len" 2>/dev/null)
    printf 'Content-Length: %s\r\n\r\n%s' "$len" "$body" >> "$FAKE_LOG"
    printf '\n' >> "$FAKE_LOG"
    count=$((count + 1))
    send '{"seq":'"$count"',"type":"response","success":true,"body":{"text":"café é 😀 tab\t","nums":[1,2.50,-0,1e20,1.5e-7,3.0E2,0.0001,123456789012345678],"ok":false,"none":null,"nested":{"a":[]}}}'
done
EOF
chmod +x "$FAKE"

# ---------------------------------------------------------------- fixtures
# A program that does not build. A parse error stops flowc under the
# lenient checking `flow debug` uses; an unbound name is only a C error there.
BROKEN="$WORK/broken.flow"
cat > "$BROKEN" <<'EOF'
function main() -> i32 {
    let x: i32 = 1 +
    return x
}
EOF

frame() {
    local n
    n=$(printf '%s' "$1" | wc -c | tr -d ' ')
    printf 'Content-Length: %s\r\n\r\n%s' "$n" "$1"
}

# Client messages, one per line. A SLEEP line waits 4 s after a launch that
# builds, so every reply lands before the next message goes out.
session_fallback='{"seq":1,"type":"request","command":"initialize","arguments":{"clientID":"vscode","clientName":"Zed é","linesStartAt1":true}}
{"seq":2,"type":"request","command":"threads"}
{"seq":3,"type":"request"}
{"seq":4,"type":"request","command":"launch","arguments":{"flowFile":"examples/basics/hello_world.flow"}}
{"seq":5,"type":"request","command":"threads"}'

session_eof='{"seq":7,"type":"request","command":"initialize"}
{"type":"request","command":"setBreakpoints","arguments":{"lines":[1,2]}}'

session_lldb='{"seq":1,"type":"request","command":"initialize","arguments":{"clientName":"Zed é","ratio":1.50,"big":1e20,"neg":-0,"lines":[[1,2],[]],"empty":{}}}
{"seq":2,"type":"request","command":"launch","arguments":{"stopOnEntry":true,"flowFile":"examples/basics/hello_world.flow","env":{"A":"1"}}}
SLEEP
{"seq":3,"type":"request","command":"launch","arguments":{"stopOnEntry":false}}
{"seq":4,"type":"request","command":"launch"}
{"seq":5,"type":"request","command":"launch","arguments":{"program":"'"$BROKEN"'","cwd":"/tmp"}}
SLEEP
{"seq":6,"type":"request","command":"launch","arguments":{"flowFile":"","program":"basics/hello_world.flow","cwd":"'"$ROOT"'/examples","args":["x"]}}
SLEEP
{"seq":7,"command":"launch","type":"request","arguments":{"source":"examples/nope/missing.flow","cwd":null}}
SLEEP
{"seq":8,"type":"event","command":"launch","arguments":{"flowFile":"x.flow"}}
{"seq":9,"type":"request","command":"setBreakpoints","arguments":{"source":{"path":"/a/b.flow"},"breakpoints":[{"line":3}],"x":"\u0001\"\\/"}}
{"seq":10,"type":"request","command":"disconnect","arguments":{"terminateDebuggee":true}}'

feed() {
    local line
    while IFS= read -r line; do
        [[ -n "$line" ]] || continue
        if [[ "$line" == SLEEP ]]; then
            sleep 4
            continue
        fi
        frame "$line"
        sleep 0.5
    done <<< "$1"
    sleep 1
}

# ---------------------------------------------------------------- runner
stub_dir="$WORK/stubbin"
mkdir -p "$stub_dir"
for name in python python3; do
    cat > "$stub_dir/$name" <<EOF
#!/bin/sh
echo "$name \$*" >> "$WORK/python-calls.log"
exit 127
EOF
    chmod +x "$stub_dir/$name"
done

pysrc=""
if [[ "$mode" == "--write-golden" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --write-golden <rev>" >&2; exit 2; }
    pysrc="$WORK/pysrc"
    mkdir -p "$pysrc"
    git archive "$rev" src/flow | tar -x -C "$pysrc"
    mkdir -p "$GOLD"
fi

normalise() {
    sed -e "s#$WORK#<WORK>#g" -e "s#$ROOT#<ROOT>#g"
}

# What the comparison ignores: Content-Length values (they count the real
# paths, so they depend on where the checkout lives) and the build log a
# failed `flow debug` launch carries (flow-driver's messages, which differ
# by host and by flowc version). The message itself must still be there.
canon() {
    sed -E -e 's/Content-Length: [0-9]+/Content-Length: N/g' \
        -e 's/(flow debug --no-launch failed:)[^"]*"/\1 <BUILD LOG>"/g'
}

run_session() {
    local name="$1" lldb="$2" script="$3"
    local out="$WORK/out/$name"
    mkdir -p "$out"
    : > "$out/lldb.log"
    local rc=0
    if [[ -n "$pysrc" ]]; then
        local find="None"
        [[ "$lldb" == fake ]] && find="'$FAKE'"
        feed "$script" | FAKE_LOG="$out/lldb.log" python3 -c "
import sys
sys.path.insert(0, '$pysrc/src')
from pathlib import Path
import flow.dap_server as m
m.REPO = Path('$ROOT')
m._find_lldb_dap = lambda: $find
sys.exit(m.run_ide_adapter())
" >"$out/stdout" 2>"$out/stderr" || rc=$?
    else
        local forced="-"
        [[ "$lldb" == fake ]] && forced="$FAKE"
        feed "$script" | PATH="$stub_dir:$PATH" FAKE_LOG="$out/lldb.log" \
            FLOW_LLDB_DAP="$forced" "$ROOT/flow" dap examples/basics/hello_world.flow \
            >"$out/stdout" 2>"$out/stderr" || rc=$?
    fi
    {
        echo "exit=$rc"
        echo "--- to client"
        normalise < "$out/stdout"
        echo
        echo "--- to lldb-dap"
        normalise < "$out/lldb.log"
    } > "$out/result"
}

# Build the debug binary, flowc and the server outside the sessions.
"$ROOT/flow" debug examples/basics/hello_world.flow --no-launch >/dev/null 2>&1 || true
"$ROOT/flow" debug "$BROKEN" --no-launch >/dev/null 2>&1 || true
if [[ -z "$pysrc" ]]; then
    (echo | PATH="$stub_dir:$PATH" FLOW_LLDB_DAP=- "$ROOT/flow" dap examples/basics/hello_world.flow >/dev/null 2>&1) || true
fi

pass=0
fail=0
for spec in "fallback:none:session_fallback" "eof:none:session_eof" "lldb:fake:session_lldb"; do
    IFS=: read -r name lldb var <<< "$spec"
    run_session "$name" "$lldb" "${!var}"
    if [[ -n "$pysrc" ]]; then
        cp "$WORK/out/$name/result" "$GOLD/$name.txt"
        echo "wrote $name"
    elif cmp -s <(canon < "$WORK/out/$name/result") <(canon < "$GOLD/$name.txt"); then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL $name"
        diff -u <(canon < "$GOLD/$name.txt") <(canon < "$WORK/out/$name/result") | head -60 || true
    fi
done

if [[ -n "$pysrc" ]]; then
    exit 0
fi
if [[ -s "$WORK/python-calls.log" ]]; then
    echo "FAIL python was called:" >&2
    cat "$WORK/python-calls.log" >&2
    exit 1
fi
echo "parity_dap: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
