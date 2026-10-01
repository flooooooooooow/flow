#!/usr/bin/env bash
# Regression for #817: concurrent `flow run` of two projects that share a
# source basename (src/main.flow) must each execute their own program.
#
# Before the fix, `flow run` emitted every executable to build/<basename> in
# the repo-global build directory, so two projects both named main.flow raced
# through the same build/main artifact and one could launch the other's
# binary. The fix gives each run invocation an isolated build root.
source "$(dirname "$0")/lib.sh"

make_project() {
    local root="$1" tag="$2"
    mkdir -p "$root/src"
    printf 'function main() -> i32 {\n    println("%s")\n    return 0\n}\n' "$tag" > "$root/src/main.flow"
}

check_concurrent_run_does_not_cross_projects() {
    t_need clang
    make_project "$T_TMP/proj_a" I_AM_PROJECT_A
    make_project "$T_TMP/proj_b" I_AM_PROJECT_B

    # Repeat a few times to exercise the compile/launch overlap window.
    local round out_a out_b pid_a pid_b
    for round in 1 2 3; do
        FLOW_HOST=flowc ./flow run "$T_TMP/proj_a/src/main.flow" \
            > "$T_TMP/a.$round.out" 2> "$T_TMP/a.$round.err" &
        pid_a=$!
        FLOW_HOST=flowc ./flow run "$T_TMP/proj_b/src/main.flow" \
            > "$T_TMP/b.$round.out" 2> "$T_TMP/b.$round.err" &
        pid_b=$!
        # Only stdout is asserted, as before; the exit status is not.
        wait "$pid_a" || true
        wait "$pid_b" || true
        out_a="$(cat "$T_TMP/a.$round.out")"
        out_b="$(cat "$T_TMP/b.$round.out")"
        a_contains "$out_a" I_AM_PROJECT_A
        a_not_contains "$out_a" I_AM_PROJECT_B
        a_contains "$out_b" I_AM_PROJECT_B
        a_not_contains "$out_b" I_AM_PROJECT_A
    done
}

t_check concurrent_run_does_not_cross_projects check_concurrent_run_does_not_cross_projects
t_done
