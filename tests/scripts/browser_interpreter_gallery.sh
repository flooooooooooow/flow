#!/usr/bin/env bash
# Every program in the Flow Way gallery runs in the browser interpreter.
#
# The gallery teaches idioms, and a reader should be able to press Run on each
# one. Four of the five could not: effects, a pipeline fork into a struct,
# enums with `choose`, and a flow block were all outside the subset.
#
# Each case is checked against the native compiler's own output where the
# program prints something, because agreeing with `./flow run` is the only
# standard that matters for an interpreter that exists to preview it.
source "$(dirname "$0")/lib.sh"

ENGINE="$T_ROOT/site/flow-compile.js"
GALLERY="$T_ROOT/examples/flow_way/README.md"

# Execute one program file through site/flow-compile.js under node. Leaves
# {ok, output, exit, detail} as JSON in $T_TMP/result.json.
run_in_browser_engine() {
    local program="$1"
    cat > "$T_TMP/d.js" <<JS
const fs=require('fs'); global.window={};
eval(fs.readFileSync($(jq -Rn --arg p "$ENGINE" '$p'),'utf8'));
const src=fs.readFileSync(process.argv[2],'utf8');
const r=window.FlowCompile.run(src);
process.stdout.write(JSON.stringify({ok:r.ok,output:r.output,exit:r.exitCode,detail:r.construct||String(r.error||'')}));
JS
    if ! node "$T_TMP/d.js" "$program" > "$T_TMP/result.json" 2> "$T_TMP/node.err"; then
        tail -c 500 "$T_TMP/node.err"
        return 1
    fi
}

result() {
    jq -r "$1" "$T_TMP/result.json"
}

# The runnable gallery programs, as a JSON array of strings. Uses the
# repository's own extractor: a regex over fences mispairs a closing fence
# with the next opening one, which is why tools/doc_examples/blocks.flow
# exists.
gallery_programs() {
    scripts/check_doc_examples.sh blocks "$GALLERY" > "$T_TMP/blocks.json"
    jq '[.[] | select(.lang == "flow" and (.code | test("function\\s+main\\s*\\("))) | .code]' \
        "$T_TMP/blocks.json"
}

# A guard: if the gallery grows, this file should see the new ones.
check_the_gallery_has_the_programs_this_asserts_about() {
    t_need node
    local n
    n="$(gallery_programs | jq length)"
    a_eq "$n" 5 "number of gallery programs"
}

# Each gallery program returns 1 on a failed assertion, so exit 0 means the
# program checked itself and passed.
check_gallery_program_runs_and_exits_zero() {
    local index="$1"
    t_need node
    gallery_programs > "$T_TMP/programs.json"
    jq -j ".[$index]" "$T_TMP/programs.json" > "$T_TMP/p.flow"
    run_in_browser_engine "$T_TMP/p.flow"
    if [[ "$(result .ok)" != true ]]; then
        result .detail | head -c 200
        return 1
    fi
    if [[ "$(result .exit)" != 0 ]]; then
        result .output
        return 1
    fi
}

# 20000 Euler steps with an every-block firing 200 times. A stepper that is
# close is not the same as one that agrees, so this compares the printed
# state against `./flow run` rather than a tolerance.
check_a_flow_block_integrates_the_same_as_the_native_compiler() {
    t_need node
    cat > "$T_TMP/p.flow" <<'FLOW'

function bang(temp: f64, heater: f64, low: f64, high: f64) -> f64 {
    if temp < low { return 1.0 }
    if temp > high { return 0.0 }
    return heater
}

flow Thermostat {
    state temperature : f64 = 12.0
    state heater      : f64 = 1.0
    param ambient     : f64 = 8.0
    param leak        : f64 = 0.12
    param power       : f64 = 1.8
    param low         : f64 = 19.5
    param high        : f64 = 20.5

    solver { dt 1 ms  method euler }

    temperature evolves as (ambient - temperature) * leak + heater * power

    every 100 ms {
        heater becomes bang(temperature, heater, low, high)
    }
}

function main() -> i32 {
    let mut room: Thermostat = Thermostat_new()
    let mut i: i32 = 0
    while i < 20000 {
        Thermostat_step(&room, 0.001)
        i = i + 1
    }
    printf("temp=%.3f heater=%.1f\n", room.temperature, room.heater)
    return 0
}
FLOW
    run_in_browser_engine "$T_TMP/p.flow"
    if [[ "$(result .ok)" != true ]]; then
        result .detail | head -c 200
        return 1
    fi
    a_eq "$(result '.output | gsub("^\\s+|\\s+$"; "")')" "temp=20.414 heater=1.0" "printed state"
}

check_an_unimplemented_solver_method_says_which_one() {
    t_need node
    cat > "$T_TMP/p.flow" <<'FLOW'

flow F {
    state x : f64 = 0.0
    solver { dt 1 ms  method rk4 }
    x evolves as 1.0
}
function main() -> i32 { return 0 }
FLOW
    run_in_browser_engine "$T_TMP/p.flow"
    a_eq "$(result .ok)" false "ok"
    a_contains "$(result .detail)" rk4
}

# Constants were parsed and then never installed as globals.
check_a_top_level_const_is_available() {
    t_need node
    printf 'const LIMIT: i32 = 7\nfunction main() -> i32 { printf("%%d\\n", LIMIT * 2) return 0 }' > "$T_TMP/p.flow"
    run_in_browser_engine "$T_TMP/p.flow"
    if [[ "$(result .ok)" != true ]]; then
        result .detail | head -c 200
        return 1
    fi
    a_eq "$(result '.output | gsub("^\\s+|\\s+$"; "")')" 14 "printed value"
}

t_check the_gallery_has_the_programs_this_asserts_about check_the_gallery_has_the_programs_this_asserts_about
for index in 0 1 2 3 4; do
    t_check "every_gallery_program_runs_and_exits_zero[$index]" check_gallery_program_runs_and_exits_zero "$index"
done
t_check a_flow_block_integrates_the_same_as_the_native_compiler check_a_flow_block_integrates_the_same_as_the_native_compiler
t_check an_unimplemented_solver_method_says_which_one check_an_unimplemented_solver_method_says_which_one
t_check a_top_level_const_is_available check_a_top_level_const_is_available
t_done
