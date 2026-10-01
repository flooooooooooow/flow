#!/usr/bin/env bash
# One negative program per rule of the type checker (compiler/src/sem_check.flow,
# the port of src/flow/type_checker.py), and the message it must print.
#
#   ./compiler/scripts/typecheck_rules.sh
#
# Each compiler/fixtures/typecheck_rules/NAME.flow starts with
#
#   # expect: <the first error message>     (or `ok`: no type error)
#   # warn: <the first warning message>     (the check passes and warns)
#   # env: VAR=value ...                    (optional: FLOW_PROFILE=safety,
#                                            FLOWC_STRICT_EFFECTS=1,
#                                            FLOWC_WERROR=1)
#
# and is compiled the way `flowc_emit.sh --strict` compiles it, stopping after
# the type check. The expected messages were recorded from the Python checker
# (its em dash and ellipsis spelled ": " and "...", as flowc prints them).
# The warnings are the checker's TypeCheckResult.warnings, which the Python
# host never printed and flowc prints as `FILE:LINE:COL: warning: ...`.
#
# Env: FLOWC_BIN=<path> tests that binary; by default the checked-in
# bootstrap C is compiled to compiler/build/flowc_bootstrap.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
DIR=compiler/fixtures/typecheck_rules
WORK="$ROOT/compiler/build/typecheck_rules"
rm -rf "$WORK"
mkdir -p "$WORK"

if [[ -n "${FLOWC_BIN:-}" ]]; then
    BIN="$FLOWC_BIN"
else
    BIN="$ROOT/compiler/build/flowc_bootstrap"
    "${CC:-cc}" -O2 -w -o "$BIN" compiler/bootstrap/flowc_stage_a.c -lm
fi
[[ "$BIN" == /* ]] || BIN="$ROOT/$BIN"

pass=0
fail=0
for f in "$DIR"/*.flow; do
    name="$(basename "$f" .flow)"
    expect="$(sed -n '1s/^# expect: //p' "$f")"
    envs=()
    envline="$(sed -n '2s/^# env: //p' "$f")"
    if [[ -n "$envline" ]]; then
        read -r -a envs <<< "$envline"
    fi
    log="$WORK/$name.log"
    set +e
    env ${envs[@]+"${envs[@]}"} FLOWC_CHECK_ONLY=1 FLOWC_BIN="$BIN" \
        compiler/scripts/flowc_emit.sh --strict "$f" "$WORK/$name.c" > "$log" 2>&1
    rc=$?
    set -e
    got="$(sed -n -E 's/^.*:[0-9]+:[0-9]+: error: //p' "$log" | head -1)"
    warn="$(sed -n '1s/^# warn: //p' "$f")"
    if [[ -n "$warn" ]]; then
        got_warn="$(sed -n -E 's/^.*:[0-9]+:[0-9]+: warning: //p' "$log" | head -1)"
        if [[ "$rc" -eq 0 && -z "$got" && "$got_warn" == "$warn" ]]; then
            pass=$((pass + 1))
        else
            fail=$((fail + 1))
            echo "FAIL $name"
            echo "  expected warning: $warn"
            echo "  got:              ${got_warn:-none} (${got:+error: $got, }exit $rc)"
        fi
        continue
    fi
    if [[ "$expect" == "ok" ]]; then
        if [[ "$rc" -eq 0 && -z "$got" ]]; then
            pass=$((pass + 1))
        else
            fail=$((fail + 1))
            echo "FAIL $name: expected no type error, got: ${got:-exit $rc}"
        fi
        continue
    fi
    if [[ "$rc" -ne 0 && "$got" == "$expect" ]]; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL $name"
        echo "  expected: $expect"
        echo "  got:      ${got:-exit $rc, no error line}"
    fi
done
echo "typecheck_rules: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
