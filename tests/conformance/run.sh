#!/usr/bin/env bash
# Stable conformance corpus (see README.md).
#
#   tests/conformance/run.sh
#
# Each positive fixture NN_*.flow must compile with flowc, build with cc and
# exit 42. Each negative fixture negative/NN_*.flow.txt must be rejected by
# flowc --strict. Every fixture starts with a `# spec:` line naming the
# docs/LANGUAGE_SPEC.md section it covers. The release rule is zero failures.
#
# Negative fixtures do not end in `.flow`, because `./flow test --tier2`
# treats every tracked `.flow` file as a program that must compile.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(cd "$HERE/../.." && pwd -P)"
cd "$ROOT" || exit 1

if [[ -z "${FLOWC_BIN:-}" ]]; then
    FLOWC_BIN="$ROOT/$(./compiler/scripts/ensure_flowc.sh)" || exit 1
    export FLOWC_BIN
fi
WORK="$(mktemp -d "${TMPDIR:-/tmp}/flow-conformance.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

pass=0
fail=0
bad() { echo "FAIL $1: $2"; fail=$((fail + 1)); }

spec_marker() {
    local first
    first="$(grep -m1 -v '^[[:space:]]*$' "$1" | sed 's/^[[:space:]]*//')"
    [[ "$first" == "# spec:"* ]]
}

positives=("$HERE"/[0-9][0-9]_*.flow)
negatives=("$HERE"/negative/[0-9][0-9]_*.flow.txt)
[[ -f "${positives[0]}" && -f "${negatives[0]}" ]] || { echo "FAIL corpus is empty"; exit 1; }

for f in "${positives[@]}"; do
    name="$(basename "$f" .flow)"
    spec_marker "$f" || { bad "$name" "no '# spec:' marker"; continue; }
    if ! ./compiler/scripts/flowc_emit.sh "$f" "$WORK/$name.c" >"$WORK/$name.log" 2>&1; then
        bad "$name" "flowc failed"; sed 's/^/  | /' "$WORK/$name.log" | head -5; continue
    fi
    if ! "${CC:-cc}" -O0 -o "$WORK/$name" "$WORK/$name.c" -lm >"$WORK/$name.cc" 2>&1; then
        bad "$name" "the C flowc emitted did not compile"; head -5 "$WORK/$name.cc"; continue
    fi
    "$WORK/$name" >/dev/null 2>&1
    rc=$?
    [[ $rc -eq 42 ]] || { bad "$name" "expected exit 42, got $rc"; continue; }
    pass=$((pass + 1))
done

for f in "${negatives[@]}"; do
    name="negative/$(basename "$f" .flow.txt)"
    spec_marker "$f" || { bad "$name" "no '# spec:' marker"; continue; }
    cp "$f" "$WORK/neg.flow"
    if ./compiler/scripts/flowc_emit.sh --strict "$WORK/neg.flow" "$WORK/neg.c" >"$WORK/neg.log" 2>&1; then
        bad "$name" "flowc --strict accepts it"; continue
    fi
    pass=$((pass + 1))
done

echo "conformance: pass=$pass fail=$fail"
[[ $fail -eq 0 ]]
