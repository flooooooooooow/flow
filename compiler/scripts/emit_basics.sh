#!/usr/bin/env bash
# Stage-A emit + cc smoke for examples/basics that use the Stage-A subset.
#
# Reports PASS/FAIL per file (emit → cc → run). Does not fail the script on
# the first error — prints a summary table and exits non-zero if any failed.
#
# Env:
#   FLOWC_FORCE_HOST=1  — emit via ./flow run (latest sources) instead of driver
#   FLOWC_EMIT_ONLY=1   — skip binary run (emit+cc only; useful under XProtect load)
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build/basics

stage_a_emit() {
    local src="$1"
    local c_out="$2"
    if [[ "${FLOWC_FORCE_HOST:-}" == "1" ]] && [[ -f compiler/src/main.flow ]]; then
        export FLOWC_IN="$src"
        export FLOWC_OUT="$c_out"
        ./flow run compiler/src/main.flow
    elif [[ -x compiler/build/stage_a_driver_flow ]]; then
        ./compiler/build/stage_a_driver_flow "$src" "$c_out"
    elif [[ -x compiler/build/stage_a_driver ]]; then
        ./compiler/build/stage_a_driver "$src" "$c_out"
    elif [[ -f compiler/src/main.flow ]]; then
        export FLOWC_IN="$src"
        export FLOWC_OUT="$c_out"
        ./flow run compiler/src/main.flow
    else
        echo "FAIL stage_a_emit: no emitter" >&2
        return 1
    fi
}

# Run $bin with a wall-clock timeout (seconds). Sets RUN_RC.
# Prefer GNU timeout; fall back to perl alarm (macOS).
run_with_timeout() {
    local secs="$1"
    local bin="$2"
    if command -v timeout >/dev/null 2>&1; then
        timeout "$secs" "$bin"
        RUN_RC=$?
        if [[ $RUN_RC -eq 124 ]]; then
            return 124
        fi
        return 0
    fi
    perl -e "alarm $secs; exec @ARGV" "$bin"
    RUN_RC=$?
    # 142 = 128+SIGALRM on many systems; also accept 14 (bare signal).
    if [[ $RUN_RC -eq 142 || $RUN_RC -eq 14 ]]; then
        return 124
    fi
    return 0
}

# name | expect_exit | path
# Primary batch (user-facing): fibonacci + hello_world.
# Extra Stage-A-clean basics included for broader C-path coverage.
CASES=(
    "fibonacci|55|examples/basics/fibonacci.flow"
    "hello_world|0|examples/basics/hello_world.flow"
    "factorial|120|examples/basics/factorial.flow"
    "gcd|14|examples/basics/gcd.flow"
    "palindrome|1|examples/basics/palindrome.flow"
    "prime_numbers|10|examples/basics/prime_numbers.flow"
    "loops|50|examples/basics/loops.flow"
    "power|0|examples/basics/power.flow"
    "bubble_sort|2|examples/basics/bubble_sort.flow"
    "simple_search|5|examples/basics/simple_search.flow"
)

pass=0
fail=0
declare -a RESULTS=()

echo "=== emit_basics (Stage-A) ==="
echo

for case in "${CASES[@]}"; do
    IFS='|' read -r name expect src <<<"$case"
    c_out="compiler/build/basics/${name}.c"
    bin="compiler/build/basics/${name}"
    status="PASS"
    detail=""

    set +e
    stage_a_emit "$src" "$c_out" >/dev/null 2>&1
    emit_rc=$?
    set -e

    if [[ $emit_rc -ne 0 || ! -f "$c_out" ]]; then
        status="FAIL"
        detail="emit failed (rc=$emit_rc)"
    else
        set +e
        cc -O0 -o "$bin" "$c_out" 2>/dev/null
        cc_rc=$?
        set -e
        if [[ $cc_rc -ne 0 ]]; then
            status="FAIL"
            detail="cc failed"
        elif [[ "${FLOWC_EMIT_ONLY:-}" == "1" ]]; then
            detail="emit+cc ok (run skipped)"
        else
            set +e
            run_with_timeout 10 "$bin"
            to_rc=$?
            set -e
            if [[ $to_rc -eq 124 ]]; then
                status="FAIL"
                detail="run timed out"
            elif [[ $RUN_RC -ne $expect ]]; then
                status="FAIL"
                detail="exit=$RUN_RC (want $expect)"
            else
                detail="exit=$RUN_RC"
            fi
        fi
    fi

    if [[ "$status" == "PASS" ]]; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
    fi
    RESULTS+=("$status|$name|$detail")
    echo "${status}  ${name}  ${detail}"
done

echo
echo "---- emit_basics summary ----"
printf '%-6s %-16s %s\n' "STATUS" "FILE" "DETAIL"
printf '%-6s %-16s %s\n' "------" "----------------" "------"
for row in "${RESULTS[@]}"; do
    IFS='|' read -r status name detail <<<"$row"
    printf '%-6s %-16s %s\n' "$status" "$name" "$detail"
done
echo "pass=$pass fail=$fail"
echo

if [[ $fail -ne 0 ]]; then
    echo "FAIL emit_basics"
    exit 1
fi
echo "PASS emit_basics"
exit 0
