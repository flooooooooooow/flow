#!/usr/bin/env bash
# C output goldens for flowc.
#
# Each case is tests/cgen/<name>.flow plus tests/cgen/<name>.expect. The
# program is compiled to C with compiler/scripts/flowc_emit.sh and the
# expectations are checked line by line:
#
#   + TEXT     the emitted C contains TEXT (fixed string)
#   - TEXT     the emitted C does not contain TEXT
#   ~ REGEX    the emitted C matches REGEX (grep -E)
#   exit N     the C builds with cc and the program exits with N
#   stdout T   ... and its stdout contains the line T (needs an exit line)
#   reject T   flowc refuses the program and its output contains T
#   flags F    pass F to flowc_emit.sh (--strict, --no-checks)
#   env K=V    set K=V for flowc (FLOWC_DEBUG_INFO=1)
#   # ...      comment
#
# Usage: tests/cgen/run.sh [name...]
# Needs a C compiler and nothing else.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-cgen-tests.XXXXXX")"
trap 'rm -rf "$work"' EXIT

cases=()
if [[ $# -gt 0 ]]; then
    for n in "$@"; do cases+=("tests/cgen/${n%.flow}.flow"); done
else
    for f in tests/cgen/*.flow; do cases+=("$f"); done
fi

pass=0
fail=0
for src in "${cases[@]}"; do
    name="$(basename "$src" .flow)"
    expect="${src%.flow}.expect"
    if [[ ! -f "$expect" ]]; then
        echo "FAIL $name: missing $expect"
        fail=$((fail + 1))
        continue
    fi
    c="$work/$name.c"
    log="$work/$name.log"
    flags=()
    envs=()
    reject=""
    while IFS= read -r line || [[ -n "$line" ]]; do
        case "$line" in
            "flags "*) read -r -a more <<< "${line#flags }"; flags+=("${more[@]}") ;;
            "reject "*) reject="${line#reject }" ;;
            "env "*) envs+=("${line#env }") ;;
        esac
    done < "$expect"

    rc=0
    env "${envs[@]+"${envs[@]}"}" compiler/scripts/flowc_emit.sh "${flags[@]+"${flags[@]}"}" "$src" "$c" >"$log" 2>&1 || rc=$?
    bad=()
    if [[ -n "$reject" ]]; then
        if [[ "$rc" -eq 0 ]]; then
            bad+=("flowc accepted the program (want: reject $reject)")
        elif ! grep -Fq -- "$reject" "$log"; then
            bad+=("rejection does not mention: $reject")
        fi
    elif [[ "$rc" -ne 0 ]]; then
        bad+=("flowc failed: $(tail -3 "$log" | tr '\n' ' ')")
    fi

    built=0
    run_rc=""
    if [[ "${#bad[@]}" -eq 0 && -z "$reject" ]]; then
        while IFS= read -r line || [[ -n "$line" ]]; do
            case "$line" in
                "+ "*) grep -Fq -- "${line#+ }" "$c" || bad+=("missing: ${line#+ }") ;;
                "- "*) ! grep -Fq -- "${line#- }" "$c" || bad+=("unexpected: ${line#- }") ;;
                "~ "*) grep -Eq -- "${line#\~ }" "$c" || bad+=("no match: ${line#\~ }") ;;
                "exit "*)
                    want="${line#exit }"
                    if [[ "$built" -eq 0 ]]; then
                        built=1
                        if ! "${CC:-cc}" -std=c11 -D_DEFAULT_SOURCE -w -O0 -Iruntime \
                                -o "$work/$name" "$c" -lm >"$work/$name.cc" 2>&1; then
                            bad+=("cc failed: $(head -3 "$work/$name.cc" | tr '\n' ' ')")
                            continue
                        fi
                        run_rc=0
                        "$work/$name" >"$work/$name.out" 2>&1 || run_rc=$?
                    fi
                    [[ "$run_rc" == "$want" ]] || bad+=("exit ${run_rc:-none}, want $want")
                    ;;
                "stdout "*)
                    if [[ -f "$work/$name.out" ]]; then
                        grep -Fxq -- "${line#stdout }" "$work/$name.out" || bad+=("stdout lacks: ${line#stdout }")
                    else
                        bad+=("stdout line needs an earlier exit line")
                    fi
                    ;;
            esac
        done < "$expect"
    fi

    if [[ "${#bad[@]}" -eq 0 ]]; then
        echo "PASS $name"
        pass=$((pass + 1))
    else
        echo "FAIL $name"
        printf '    %s\n' "${bad[@]}"
        fail=$((fail + 1))
    fi
done

echo "cgen goldens: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
