#!/usr/bin/env bash
# Parity gate for algebraic effects on flowc (#675, #996).
#
# flowc lowers `effect`, `capability`, `handle E with C { }`, effect rows
# (`-> T with E`) and `capability E` parameters the way the Python host does
# (src/flow/parser.py, type_checker.py, c_generator.py). This gate holds it
# to the same results:
#
#   ./compiler/scripts/parity_effects.sh
#       flowc against the goldens in compiler/fixtures/effects/: the
#       diagnostics of each rejected fixture, or the run output and exit code
#       of each accepted one, plus the `log` registry package demo.
#
#   ./compiler/scripts/parity_effects.sh --python <rev>
#       also runs the Python host from git revision <rev> on the fixtures and
#       on every tracked .flow file that uses effects, and requires the same
#       result from flowc: accept or reject, the same diagnostics for the
#       fixtures, and the same output and exit code when both run.
#
#   ./compiler/scripts/parity_effects.sh --write-golden <rev>
#       rewrite the goldens from the Python host at <rev>.
#
# A result is one of
#   reject        followed by the effect diagnostics, one per line
#   reject-cc     the C did not compile
#   reject-link   the C compiled but did not link (a runtime the program
#                 needs is not linked here; the same holds on both hosts)
#   run exit=N    followed by what the program printed
#
# Fixtures run under the Python host's default strict checking; a fixture
# marked `# effects-mode: strict` adds --strict-effects (flowc:
# FLOWC_STRICT_EFFECTS=1), and `# effects-mode: runtime-strict` runs the
# program with FLOW_STRICT_EFFECTS=1 and records stderr too. Corpus files
# compile the way `flow run` does (Python --lenient, flowc FLOWC_TYPECHECK=1).
#
# Diagnostics are compared as text. Two Python messages spell a separator
# with an em dash and an ellipsis; flowc writes ": " and "...", and the gate
# maps the Python spelling before comparing.
#
# The last Python revision checked is 860b7dd7 (origin/main before the port).
#
# Env: FLOWC_BIN=<path> tests that binary instead of building
# compiler/build/flowc_bootstrap from the checked-in bootstrap C.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

FIX=compiler/fixtures/effects
WORK="$ROOT/compiler/build/parity_effects"
mode="${1:-}"
rev="${2:-}"
rm -rf "$WORK"
mkdir -p "$WORK/out" "$WORK/rt"

if [[ -n "${FLOWC_BIN:-}" ]]; then
    BIN="$FLOWC_BIN"
else
    BIN="$ROOT/compiler/build/flowc_bootstrap"
    "${CC:-cc}" -O2 -w -o "$BIN" compiler/bootstrap/flowc_stage_a.c -lm
fi
echo "=== parity_effects: flowc = ${BIN} ==="

# The C runtime `flow run` links (runtime/*.c), built once for both hosts.
CFLAGS=(-std=c11 -D_DEFAULT_SOURCE -w -O1 "-I$ROOT/runtime")
rt_objs=()
for f in flow_concurrency flow_fiber flow_fctx_init flow_netpoll flow_netpoll_fiber \
         flow_http_bench flow_tcp flow_race flow_cont flow_rt_support flow_rt_task_store \
         flow_rt_fiber_async flow_rt_parallel flow_rt_cchan flow_rt_sysinfo flow_rt_crypto flow_tls; do
    "${CC:-cc}" "${CFLAGS[@]}" -DFLOW_HAS_OPENSSL=0 -c "runtime/$f.c" -o "$WORK/rt/$f.o"
    rt_objs+=("$WORK/rt/$f.o")
done
case "$(uname -m)" in
    arm64|aarch64) "${CC:-cc}" -c runtime/flow_fctx_arm64.S -o "$WORK/rt/fctx.o"; rt_objs+=("$WORK/rt/fctx.o") ;;
    x86_64|amd64) "${CC:-cc}" -c runtime/flow_fctx_x86_64.S -o "$WORK/rt/fctx.o"; rt_objs+=("$WORK/rt/fctx.o") ;;
esac
# An archive, so a program links only the runtime objects it uses (the rest
# need the Flow-side runtime in lib/runtime, which `flow run` compiles).
rm -f "$WORK/rt/libflowrt.a"
ar rcs "$WORK/rt/libflowrt.a" "${rt_objs[@]}"
rt_objs=("$WORK/rt/libflowrt.a")
LDFLAGS=(-lm -pthread)
if [[ "$(uname -s)" == "Darwin" ]]; then
    LDFLAGS+=(-framework CoreFoundation)
fi

fixture_mode() {
    local f="$1"
    if grep -q '^# effects-mode: strict$' "$f"; then
        echo strict
    elif grep -q '^# effects-mode: runtime-strict$' "$f"; then
        echo runtime-strict
    else
        echo plain
    fi
}

# run_c <c-file> <result> <mode>: compile, link, run; append to <result>.
run_c() {
    local c="$1" res="$2" m="$3"
    local exe="${c%.c}.exe"
    if ! "${CC:-cc}" "${CFLAGS[@]}" -c "$c" -o "${c%.c}.o" >/dev/null 2>&1; then
        echo "reject-cc" > "$res"
        return
    fi
    if ! "${CC:-cc}" "${c%.c}.o" "${rt_objs[@]}" "${LDFLAGS[@]}" -o "$exe" >/dev/null 2>&1; then
        echo "reject-link" > "$res"
        return
    fi
    local code=0
    local dir
    dir="$(dirname "$c")"
    if [[ "$m" == runtime-strict ]]; then
        # The outer redirect keeps bash's "Abort trap" note out of the log.
        { FLOW_STRICT_EFFECTS=1 perl -e 'alarm 10; exec @ARGV' "$exe" > "$dir/run.txt" 2>&1 || code=$?; } 2>/dev/null
    else
        perl -e 'alarm 10; exec @ARGV' "$exe" > "$dir/run.txt" 2>/dev/null || code=$?
    fi
    { echo "run exit=${code}"; cat "$dir/run.txt"; } > "$res"
}

# flowc_result <flow-file> <result> <mode> <lenient 0|1>
flowc_result() {
    local f="$1" res="$2" m="$3"
    local d
    d="$(dirname "$res")"
    local env_strict=0
    [[ "$m" == strict ]] && env_strict=1
    local code=0
    FLOWC_STRICT_EFFECTS="$env_strict" FLOWC_BUNDLE=1 FLOWC_DIR="$ROOT" FLOWC_TYPECHECK=1 \
        FLOWC_IN="$f" FLOWC_OUT="$d/fc.c" "$BIN" > "$d/fc.log" 2>&1 || code=$?
    if [[ "$code" -ne 0 || ! -s "$d/fc.c" ]]; then
        { echo "reject"; sed -n 's/^.*:[0-9]*:[0-9]*: error: //p' "$d/fc.log"; } > "$res"
        return
    fi
    run_c "$d/fc.c" "$res" "$m"
}

# python_result <pyref> <flow-file> <result> <mode> <lenient 0|1>
python_result() {
    local ref="$1" f="$2" res="$3" m="$4" lenient="$5"
    local d
    d="$(dirname "$res")"
    local args=(--c)
    [[ "$lenient" == 1 ]] && args+=(--lenient)
    [[ "$m" == strict ]] && args+=(--strict-effects)
    local code=0
    (cd "$(dirname "$f")" && PYTHONPATH="$ref/src" python3 -m flow.transpiler "$(basename "$f")" \
        "${args[@]}" -o "$d/py.c") > "$d/py.log" 2>&1 || code=$?
    if [[ "$code" -ne 0 || ! -s "$d/py.c" ]]; then
        { echo "reject"; sed -n 's/^  ✗ //p' "$d/py.log" | sed -e 's/ — /: /g' -e 's/…/.../g' \
            | grep -E "effect|Effect|Capability|handle" || true; } > "$res"
        return
    fi
    run_c "$d/py.c" "$res" "$m"
}

# The `log` registry package demo (#991) with the package beside it, so both
# hosts resolve it without a package install.
make_log_demo() {
    local d="$WORK/log_demo"
    mkdir -p "$d"
    cp registry/packages/log/src/lib.flow "$d/lib.flow"
    sed 's/^import log\.lib {/import .lib {/' examples/ecosystem/log_demo/src/main.flow > "$d/main.flow"
    echo "$d/main.flow"
}

fixtures=()
for f in "$FIX"/*.flow; do
    fixtures+=("$ROOT/$f")
done
log_demo="$(make_log_demo)"

key_of() {
    local f="${1#"$ROOT"/}"
    printf '%s\n' "${f//\//__}"
}

golden_of() {
    local f="$1"
    if [[ "$f" == "$log_demo" ]]; then
        echo "$ROOT/$FIX/log_demo.expected"
    else
        echo "${f%.flow}.expected"
    fi
}

setup_python() {
    local r="$1"
    local ref="$WORK/pyref"
    mkdir -p "$ref"
    git archive "$r" src/flow lib | tar -x -C "$ref"
    echo "$ref"
}

if [[ "$mode" == "--write-golden" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --write-golden <rev>" >&2; exit 2; }
    ref="$(setup_python "$rev")"
    for f in "${fixtures[@]}" "$log_demo"; do
        k="$(key_of "$f")"
        mkdir -p "$WORK/out/$k"
        python_result "$ref" "$f" "$WORK/out/$k/py.res" "$(fixture_mode "$f")" 0
        cp "$WORK/out/$k/py.res" "$(golden_of "$f")"
    done
    echo "wrote goldens for $(( ${#fixtures[@]} + 1 )) programs from ${rev}"
    exit 0
fi

fail=0

# 1. Fixtures and the log demo against the goldens.
pass=0
for f in "${fixtures[@]}" "$log_demo"; do
    k="$(key_of "$f")"
    mkdir -p "$WORK/out/$k"
    flowc_result "$f" "$WORK/out/$k/fc.res" "$(fixture_mode "$f")"
    g="$(golden_of "$f")"
    if [[ -f "$g" ]] && cmp -s "$g" "$WORK/out/$k/fc.res"; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL ${f#"$ROOT"/}" >&2
        diff "$g" "$WORK/out/$k/fc.res" | head -10 >&2 || true
    fi
done
echo "fixtures: pass=${pass} fail=$(( ${#fixtures[@]} + 1 - pass ))"

# 2. Optional: live against the Python host at <rev>.
if [[ "$mode" == "--python" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --python <rev>" >&2; exit 2; }
    ref="$(setup_python "$rev")"
    live_pass=0
    live_fail=0
    for f in "${fixtures[@]}" "$log_demo"; do
        k="$(key_of "$f")"
        python_result "$ref" "$f" "$WORK/out/$k/py.res" "$(fixture_mode "$f")" 0
        if cmp -s "$WORK/out/$k/py.res" "$WORK/out/$k/fc.res"; then
            live_pass=$((live_pass + 1))
        else
            live_fail=$((live_fail + 1))
            echo "FAIL live ${f#"$ROOT"/}" >&2
            diff "$WORK/out/$k/py.res" "$WORK/out/$k/fc.res" | head -10 >&2 || true
        fi
    done
    echo "live fixtures python@${rev}: pass=${live_pass} fail=${live_fail}"
    fail=$((fail + live_fail))

    # Every tracked program that uses effects.
    git ls-files '*.flow' | LC_ALL=C sort \
        | xargs grep -lE '^\s*(export\s+)?(effect|capability)\s+[A-Z]\w*\s*\{|^\s*handle\s+\w|\)\s*(->\s*[^{]*)?\bwith\s+[A-Z]|capability\s+[A-Z]\w*\s*[,)]' \
        | grep -v "^$FIX/" > "$WORK/corpus.txt" || true
    n=0; same_run=0; same_reject=0; stage_diff=0; diff_n=0; known=0
    while IFS= read -r rel; do
        f="$ROOT/$rel"
        k="$(key_of "$f")"
        mkdir -p "$WORK/out/$k"
        n=$((n + 1))
        python_result "$ref" "$f" "$WORK/out/$k/py.res" plain 1
        flowc_result "$f" "$WORK/out/$k/fc.res" plain
        pyh="$(head -1 "$WORK/out/$k/py.res")"
        fch="$(head -1 "$WORK/out/$k/fc.res")"
        if [[ "$pyh" == run* ]] && cmp -s "$WORK/out/$k/py.res" "$WORK/out/$k/fc.res"; then
            same_run=$((same_run + 1))
        elif [[ "$pyh" == reject* && "$pyh" == "$fch" ]]; then
            same_reject=$((same_reject + 1))
        elif [[ "$pyh" == reject* && "$fch" == reject* ]]; then
            # Rejected on both hosts, at different stages. Listed so a flowc
            # C error behind a Python link error stays visible.
            same_reject=$((same_reject + 1))
            stage_diff=$((stage_diff + 1))
            echo "both reject $rel: python=${pyh} flowc=${fch}"
        elif grep -q "^${rel} " "$FIX/known_gaps.txt" 2>/dev/null; then
            known=$((known + 1))
            echo "known gap $rel: python=${pyh} flowc=${fch}"
        else
            diff_n=$((diff_n + 1))
            echo "FAIL corpus $rel: python=${pyh} flowc=${fch}" >&2
        fi
    done < "$WORK/corpus.txt"
    echo "corpus python@${rev}: files=${n} same_run=${same_run} same_reject=${same_reject} (different stage: ${stage_diff}) known_gaps=${known} fail=${diff_n}"
    fail=$((fail + diff_n))
fi

if [[ "$fail" -ne 0 ]]; then
    echo "parity_effects: FAIL (${fail})"
    exit 1
fi
echo "parity_effects: PASS"
