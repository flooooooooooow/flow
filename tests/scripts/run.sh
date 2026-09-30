#!/usr/bin/env bash
# Shell tests that drive ./flow, the Flow tools behind scripts/*.sh and the
# checked-in docs as subprocesses. They replaced the last subprocess-only
# pytest files. Each tests/scripts/<name>.sh prints one PASS, FAIL or SKIP
# line per check; a check skips when a tool it needs (clang, node, emcc,
# mlir-opt, strip) is missing.
#
# python and python3 are stubbed out on PATH: nothing here may need them.
#
# Usage: tests/scripts/run.sh [name...]
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

stub="$(mktemp -d "${TMPDIR:-/tmp}/flow-script-tests-nopy.XXXXXX")"
trap 'rm -rf "$stub"' EXIT
for name in python python3; do
    printf '#!/bin/sh\necho "%s $*" >> "%s/python-calls.log"\nexit 127\n' "$name" "$stub" > "$stub/$name"
    chmod +x "$stub/$name"
done
export PATH="$stub:$PATH"

failed=()
for test in tests/scripts/*.sh; do
    name="$(basename "$test" .sh)"
    [[ "$name" == run || "$name" == lib ]] && continue
    if [[ $# -gt 0 ]] && [[ " $* " != *" $name "* ]]; then
        continue
    fi
    bash "$test" || failed+=("$name")
done

if [[ -s "$stub/python-calls.log" ]]; then
    echo "FAIL python was called:"
    sed 's/^/    /' "$stub/python-calls.log"
    failed+=("python-calls")
fi

if [[ "${#failed[@]}" -gt 0 ]]; then
    echo "tests/scripts: failures in ${failed[*]}"
    exit 1
fi
echo "tests/scripts: all files passed"
