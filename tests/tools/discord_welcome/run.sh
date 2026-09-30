#!/usr/bin/env bash
# Tests for the Flow welcome bot (tools/discord-welcome).
#
# Welcome logic (the cases of the old test_bot.py): template loading and
# its three errors, {user}/{guild} substitution, seeded determinism, and
# every shipped template formatting cleanly. Then the environment checks
# and their exit codes, and an offline gateway run: gateway.replay is fed
# to --replay and the gateway frames and REST requests it would send are
# compared with gateway.stdout.expected (log lines, timestamps removed,
# with gateway.log.expected). Last, when discord.com is reachable, one
# HTTPS GET of /api/v10/gateway proves TLS and HTTP against the real host.
#
# Usage: tests/tools/discord_welcome/run.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
HERE="tests/tools/discord_welcome"

pass=0
fail=0
ok() { echo "PASS $1"; pass=$((pass + 1)); }
bad() { echo "FAIL $1"; fail=$((fail + 1)); }

BIN="$(tools/discord-welcome/build.sh)"
MSG="tools/discord-welcome/messages.json"
work="$(mktemp -d "${TMPDIR:-/tmp}/flow-welcome-tests.XXXXXX")"
trap 'rm -rf "$work"' EXIT

# load_messages returns templates, each with {user}.
if "$BIN" --messages "$MSG" --render-all '{user}' Flow > "$work/all" 2>&1 \
    && [ "$(wc -l < "$work/all")" -ge 1 ] && ! grep -v '{user}' "$work/all" >/dev/null; then
    ok "load_messages returns templates with {user}"
else
    bad "load_messages returns templates with {user}"
fi

# Missing file, empty list, bad JSON: each is an error with exit 1.
expect_error() {
    local name="$1" file="$2" pattern="$3"
    set +e
    "$BIN" --messages "$file" --render @a Flow > "$work/out" 2> "$work/err"
    local rc=$?
    set -e
    if [ "$rc" -eq 1 ] && grep -q "$pattern" "$work/err"; then ok "$name"; else bad "$name (exit $rc)"; cat "$work/err"; fi
}
expect_error "load_messages missing file" "$work/nope.json" "No such file or directory"
printf '{"messages": []}' > "$work/empty.json"
expect_error "load_messages empty list" "$work/empty.json" "contains no 'messages' entries"
printf '{not json' > "$work/bad.json"
expect_error "load_messages bad JSON" "$work/bad.json" "invalid JSON"

# pick_welcome substitutes {user} and {guild}.
printf '{"messages": ["Hello {user}, welcome to the {guild} discord server!"]}' > "$work/one.json"
got="$("$BIN" --messages "$work/one.json" --render @alice Flow --seed 0)"
if [ "$got" = "Hello @alice, welcome to the Flow discord server!" ]; then ok "pick_welcome substitutes user and guild"; else bad "pick_welcome substitution: $got"; fi

# Same seed, same pick.
cat > "$work/three.json" <<'EOF'
{"messages": ["Hello {user}, welcome to the {guild} discord server!",
              "Welcome {user} to the {guild} discord server.",
              "{user} just joined the {guild} discord server."]}
EOF
a="$("$BIN" --messages "$work/three.json" --render @bob Flow --seed 42)"
b="$("$BIN" --messages "$work/three.json" --render @bob Flow --seed 42)"
if [ "$a" = "$b" ] && [[ "$a" == *"@bob"* ]] && [[ "$a" == *"Flow"* ]]; then ok "pick_welcome is deterministic with a seed"; else bad "seeded pick: '$a' vs '$b'"; fi

# Every shipped template formats with both fields.
if "$BIN" --messages "$MSG" --render-all @tester Flow > "$work/fmt" 2>&1 \
    && ! grep -v '@tester' "$work/fmt" >/dev/null && ! grep -v 'Flow' "$work/fmt" >/dev/null; then
    ok "every template formats cleanly"
else
    bad "every template formats cleanly"
fi

# Environment: same messages and exit codes as bot.py.
expect_env() {
    local name="$1" pattern="$2"; shift 2
    set +e
    env -i PATH="$PATH" "$@" "$BIN" --messages "$MSG" --replay /dev/null > /dev/null 2> "$work/err"
    local rc=$?
    set -e
    if [ "$rc" -eq 1 ] && grep -q "ERROR discord-welcome: $pattern" "$work/err"; then ok "$name"; else bad "$name (exit $rc)"; cat "$work/err"; fi
}
expect_env "missing DISCORD_TOKEN" "Missing required env var DISCORD_TOKEN"
expect_env "blank DISCORD_TOKEN" "Missing required env var DISCORD_TOKEN" DISCORD_TOKEN="  "
expect_env "missing WELCOME_CHANNEL_ID" "Missing required env var WELCOME_CHANNEL_ID" DISCORD_TOKEN=x
expect_env "non-integer WELCOME_CHANNEL_ID" "WELCOME_CHANNEL_ID must be an integer, got 'abc'" DISCORD_TOKEN=x WELCOME_CHANNEL_ID=abc

# Offline gateway run.
set +e
DISCORD_TOKEN=secret-token-value WELCOME_CHANNEL_ID=555 "$BIN" --messages "$MSG" \
    --replay "$HERE/gateway.replay" --seed 7 > "$work/stdout" 2> "$work/stderr"
rc=$?
set -e
sed -E 's/^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9:]{8},[0-9]{3} //' "$work/stderr" > "$work/log"
if [ "$rc" -eq 0 ] && cmp -s "$work/stdout" "$HERE/gateway.stdout.expected"; then
    ok "replay: gateway frames and REST requests"
else
    bad "replay stdout (exit $rc)"
    diff -u "$HERE/gateway.stdout.expected" "$work/stdout" || true
fi
if cmp -s "$work/log" "$HERE/gateway.log.expected"; then ok "replay: log lines"; else bad "replay log"; diff -u "$HERE/gateway.log.expected" "$work/log" || true; fi
if grep -q "secret-token-value" "$work/stdout" "$work/stderr"; then bad "token leaked into output"; else ok "token never printed"; fi

# TLS + HTTP against discord.com, when the network allows it.
if "$BIN" --check-tls > "$work/tls" 2>&1; then
    if head -1 "$work/tls" | grep -q '^HTTP 200' && grep -q '"url"' "$work/tls"; then ok "HTTPS GET discord.com/api/v10/gateway"; else bad "HTTPS GET"; cat "$work/tls"; fi
elif grep -q "getaddrinfo\|could not connect" "$work/tls"; then
    echo "SKIP HTTPS GET discord.com (no network)"
else
    bad "HTTPS GET discord.com"
    cat "$work/tls"
fi

echo "discord-welcome checks: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
