#!/usr/bin/env bash
# Manual local smoke test for the Flow-in-Flow AST disk cache (#736).
# Must run against a freshly rebuilt compiler (bootstrap regeneration).
set -euo pipefail

repo="$(cd "$(dirname "$0")/../.." && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/flow-ast-cache.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
mkdir -m 700 "$tmp/home"

subject="$repo/examples/basics/hello_world.flow"
cache="$tmp/home/.cache/flow/ast"
salt="cache-security-$$-initial"

run_subject() {
    HOME="$tmp/home" FLOW_CACHE_SALT="$salt" \
        "$repo/flow" run "$subject" >/dev/null
}

mode() {
    if stat -c '%a' "$1" >/dev/null 2>&1; then
        stat -c '%a' "$1"
    else
        stat -f '%Lp' "$1"
    fi
}

run_subject
test -d "$cache"
test "$(mode "$tmp/home/.cache/flow")" = 700
test "$(mode "$cache")" = 700

entry="$(find "$cache" -maxdepth 1 -type f -name '*.ast' -print -quit)"
test -n "$entry"
test "$(mode "$entry")" = 600
run_subject

# Corrupt the cached header: parser must treat the entry as a miss, not
# execute or trust arbitrary contents of the binary AST snapshot.
printf 'bad!' | dd of="$entry" bs=1 count=4 conv=notrunc 2>/dev/null
run_subject

# A different salt would ordinarily create a new snapshot. An insecure
# cache directory must instead cause safe parse-without-cache fallback.
before="$(find "$cache" -maxdepth 1 -type f -name '*.ast' | wc -l | tr -d ' ')"
chmod 755 "$cache"
salt="cache-security-$$-other"
run_subject
after="$(find "$cache" -maxdepth 1 -type f -name '*.ast' | wc -l | tr -d ' ')"
test "$before" = "$after"

# A symlink at a cache parent is never an acceptable trusted cache.
chmod 700 "$cache"
mv "$cache" "$tmp/saved-ast"
ln -s "$tmp/saved-ast" "$cache"
run_subject
test -L "$cache"

echo "PASS: private cache modes, malformed header fallback and symlink refusal"
