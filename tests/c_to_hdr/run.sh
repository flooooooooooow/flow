#!/usr/bin/env bash
# Golden check for scripts/tools/c_to_hdr, the header derivation that
# compiler/scripts/roundtrip.sh runs on each Stage-A module.
#
# Each NAME.c here has NAME.h.expect, the header the retired
# compiler/scripts/flowc_c_to_hdr.py wrote for it. token_flowc.c and
# overload_table_flowc.c are real roundtrip emits; the others cover CRLF
# input, a missing final newline, an empty file, Unicode line breaks and the
# edge cases of the three patterns. Also checks the usage error (exit 2) and
# an unreadable input (exit 1). Runs with python and python3 stubbed out.
#
# Usage: tests/c_to_hdr/run.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

work="$(mktemp -d "${TMPDIR:-/tmp}/c_to_hdr.XXXXXX")"
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/bin"
for name in python python3; do
    printf '#!/bin/sh\necho "%s called: $*" >&2\nexit 127\n' "$name" > "$work/bin/$name"
    chmod +x "$work/bin/$name"
done
export PATH="$work/bin:$PATH"

tool="$(scripts/tools/build_tool.sh c_to_hdr)"

pass=0
fail=0
for src in tests/c_to_hdr/*.c; do
    name="$(basename "$src" .c)"
    if "$tool" "$src" "$work/$name.h" && cmp -s "$work/$name.h" "tests/c_to_hdr/$name.h.expect"; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL $name"
        diff "tests/c_to_hdr/$name.h.expect" "$work/$name.h" | head -20 || true
    fi
done

rc=0
"$tool" only_one_arg >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 2 ]]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL usage exit $rc (want 2)"; fi

rc=0
"$tool" "$work/missing.c" "$work/missing.h" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 1 && ! -e "$work/missing.h" ]]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL missing input exit $rc (want 1)"; fi

echo "c_to_hdr: pass=$pass fail=$fail"
[[ "$fail" -eq 0 ]]
