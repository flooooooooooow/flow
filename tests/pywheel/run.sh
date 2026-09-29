#!/usr/bin/env bash
# Parity gate for `flow python` (tools/pywheel, the Flow port of the retired
# src/flow/python_generator.py).
#
# Each line of tests/pywheel/cases.txt is `ID PROGRAM [ARGS...]`. The gate
# copies tests/pywheel/cases/ to a scratch directory, runs
# `./flow python PROGRAM ARGS` there and compares with tests/pywheel/expected/ID/:
#
#   stdout.txt  stdout, byte for byte
#   stderr.txt  stderr, with the scratch directory written as @WORK@
#   rc.txt      the exit status
#   dist/       every file written under dist/, byte for byte; a missing
#               dist/ means nothing may be written. In a generated
#               MODULE_ext.c the line @FLOWC_C@ stands for the program's C,
#               which the gate takes from compiler/scripts/flowc_emit.sh, so a
#               change in flowc's output does not touch these goldens.
#
# The goldens were captured from the Python generator before it was deleted
# (see expected/README). python and python3 are stubs on PATH that log their
# arguments and fail. A --source run must not call them. The one wheel-mode
# case must call `python3 -m pip wheel` once (the setuptools build, the only
# step that uses Python) and then fall back to the source file, as the Python
# generator did when the wheel build failed.
#
# expected/package/ holds the setup.py (as setup.py.expect, so the Python
# ratchet does not count a golden as source) and pyproject.toml the tool
# writes for the wheel build.
#
# FLOW_PYWHEEL_SMOKE=1 also builds a real wheel with the system python3 and
# setuptools, installs it into the scratch directory and calls it.
#
# Usage: tests/pywheel/run.sh            check
#        tests/pywheel/run.sh --update   rewrite expected/ from the Flow tool
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

update=0
[[ "${1:-}" == "--update" ]] && update=1

real_python="$(command -v python3 || true)"
work="$(mktemp -d "${TMPDIR:-/tmp}/flow-pywheel-gate.XXXXXX")"
work="$(cd "$work" && pwd -P)"
trap 'rm -rf "$work"' EXIT

stub_dir="$work/bin"
log="$work/python-calls.log"
mkdir -p "$stub_dir"
: > "$log"
for name in python python3; do
    cat > "$stub_dir/$name" <<EOF
#!/bin/sh
echo "$name \$*" >> "$log"
echo "stub-python: no Python here" >&2
exit 1
EOF
    chmod +x "$stub_dir/$name"
done
export PATH="$stub_dir:$PATH"
unset FLOW_PYTHON

exp_root="tests/pywheel/expected"

# The program's C, as the tool embeds it.
flowc_c() {
    local prog="$1" out="$2"
    compiler/scripts/flowc_emit.sh --strict "$prog" "$out" >/dev/null 2>&1
}

# Expand @FLOWC_C@ in template $1 with the C file $2 into $3.
expand_template() {
    local tpl="$1" c="$2" out="$3"
    if grep -qx '@FLOWC_C@' "$tpl"; then
        { sed '/^@FLOWC_C@$/,$d' "$tpl"; cat "$c"; sed '1,/^@FLOWC_C@$/d' "$tpl"; } > "$out"
        # The template ends without a newline after the last line exactly
        # when the generated file does; sed adds one, so trim to match.
        if [[ "$(tail -c1 "$tpl" | od -An -c | tr -d ' ')" != '\n' ]]; then
            local n; n="$(wc -c < "$out")"
            head -c $((n - 1)) "$out" > "$out.t" && mv "$out.t" "$out"
        fi
    else
        cp "$tpl" "$out"
    fi
}

# Replace the program's C in generated file $1 by @FLOWC_C@ (for --update).
make_template() {
    local gen="$1" c="$2" out="$3"
    local n_gen n_c head_len
    n_gen="$(wc -c < "$gen")"
    n_c="$(wc -c < "$c")"
    head_len="$(grep -n -F '/* ===== Flow compiled code ===== */' "$gen" | head -1 | cut -d: -f1)"
    local pre; pre="$(head -n "$head_len" "$gen" | wc -c)"
    { head -c "$pre" "$gen"; echo '@FLOWC_C@'; tail -c $((n_gen - pre - n_c)) "$gen"; } > "$out"
}

pass=0
fail=0
while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" || "$line" == \#* ]] && continue
    read -r -a words <<< "$line"
    id="${words[0]}"
    prog="${words[1]}"
    args=("${words[@]:2}")
    d="$work/cases/$id"
    mkdir -p "$d"
    cp -R tests/pywheel/cases/. "$d/"
    : > "$log"
    rc=0
    (cd "$d" && "$ROOT/flow" python "$prog" "${args[@]+"${args[@]}"}" >"$d/.stdout" 2>"$d/.stderr") || rc=$?
    sed "s#$d#@WORK@#g; s#$ROOT#@ROOT@#g" "$d/.stderr" > "$d/.stderr.n"
    e="$exp_root/$id"
    if [[ "$update" -eq 1 ]]; then
        rm -rf "$e"
        mkdir -p "$e"
        cp "$d/.stdout" "$e/stdout.txt"
        cp "$d/.stderr.n" "$e/stderr.txt"
        echo "$rc" > "$e/rc.txt"
        if [[ -d "$d/dist" ]]; then
            mkdir -p "$e/dist"
            for f in "$d/dist"/*; do
                b="$(basename "$f")"
                if [[ "$b" == *_ext.c ]]; then
                    flowc_c "$d/$prog" "$work/$id.c"
                    make_template "$f" "$work/$id.c" "$e/dist/$b"
                else
                    cp "$f" "$e/dist/$b"
                fi
            done
        fi
        echo "UPDATED $id"
        continue
    fi
    bad=()
    cmp -s "$d/.stdout" "$e/stdout.txt" || bad+=("stdout")
    cmp -s "$d/.stderr.n" "$e/stderr.txt" || bad+=("stderr")
    [[ "$rc" == "$(cat "$e/rc.txt")" ]] || bad+=("exit $rc, want $(cat "$e/rc.txt")")
    if [[ -d "$e/dist" ]]; then
        if [[ ! -d "$d/dist" ]]; then
            bad+=("no dist/")
        else
            want="$(cd "$e/dist" && ls | sort | tr '\n' ' ')"
            have="$(cd "$d/dist" && ls | sort | tr '\n' ' ')"
            [[ "$want" == "$have" ]] || bad+=("dist files: $have, want $want")
            for f in "$e/dist"/*; do
                b="$(basename "$f")"
                [[ -f "$d/dist/$b" ]] || continue
                flowc_c "$d/$prog" "$work/$id.c" || true
                expand_template "$f" "$work/$id.c" "$work/$id.want"
                cmp -s "$work/$id.want" "$d/dist/$b" || bad+=("dist/$b")
            done
        fi
    elif [[ -d "$d/dist" ]]; then
        bad+=("wrote dist/")
    fi
    calls="$(wc -l < "$log" | tr -d ' ')"
    if [[ " ${args[*]-} " == *" --source "* || "$rc" != 0 ]]; then
        [[ "$calls" == 0 ]] || bad+=("called Python: $(head -1 "$log")")
    else
        grep -q '^python3 -m pip wheel \. -w /' "$log" || bad+=("no pip wheel call")
        [[ "$calls" == 1 ]] || bad+=("$calls Python calls")
    fi
    if [[ ${#bad[@]} -eq 0 ]]; then
        pass=$((pass + 1))
        echo "PASS $id"
    else
        fail=$((fail + 1))
        echo "FAIL $id: ${bad[*]}"
        if [[ " ${bad[*]} " == *" stdout "* ]]; then diff "$e/stdout.txt" "$d/.stdout" | head -20 || true; fi
        if [[ " ${bad[*]} " == *" stderr "* ]]; then diff "$e/stderr.txt" "$d/.stderr.n" | head -20 || true; fi
    fi
done < tests/pywheel/cases.txt

# setup.py and pyproject.toml for the wheel build.
pk="$work/pkgwork"
mkdir -p "$pk"
# The cases above built the tool (flow_native_tool).
tool="$ROOT/build/tools/flow-pywheel"
[[ -x "$tool" ]] || tool="${XDG_CACHE_HOME:-$HOME/.cache}/flow/tools/flow-pywheel"
(cd tests/pywheel/cases && "$tool" mathlib.flow my_math 2.0.0 package dist "$pk" "$ROOT" >/dev/null 2>&1) || true
if [[ "$update" -eq 1 ]]; then
    mkdir -p "$exp_root/package"
    cp "$pk/pkg/setup.py" "$exp_root/package/setup.py.expect"
    cp "$pk/pkg/pyproject.toml" "$exp_root/package/"
else
    pbad=()
    cmp -s "$pk/pkg/setup.py" "$exp_root/package/setup.py.expect" || pbad+=("setup.py")
    cmp -s "$pk/pkg/pyproject.toml" "$exp_root/package/pyproject.toml" || pbad+=("pyproject.toml")
    if [[ ${#pbad[@]} -eq 0 ]]; then
        pass=$((pass + 1)); echo "PASS package files"
    else
        fail=$((fail + 1)); echo "FAIL package files: ${pbad[*]}"
    fi
fi

if [[ "${FLOW_PYWHEEL_SMOKE:-0}" == "1" && "$update" -eq 0 ]]; then
    s="$work/smoke"
    mkdir -p "$s"
    cp tests/pywheel/cases/mathlib.flow "$s/"
    if (cd "$s" && FLOW_PYTHON="$real_python" "$ROOT/flow" python mathlib.flow --version 1.2.3 >"$s/out" 2>&1) \
        && whl="$(ls "$s"/dist/mathlib-1.2.3-*.whl 2>/dev/null | head -1)" && [[ -n "$whl" ]] \
        && "$real_python" -m pip install --quiet --no-deps --target "$s/site" "$whl" \
        && got="$(PYTHONPATH="$s/site" "$real_python" -c 'import mathlib; print(mathlib.square(5.0), mathlib.factorial(5))')" \
        && [[ "$got" == "25.0 120" ]]; then
        pass=$((pass + 1)); echo "PASS wheel smoke ($got)"
    else
        fail=$((fail + 1)); echo "FAIL wheel smoke"; cat "$s/out" || true
    fi
fi

if [[ "$update" -eq 1 ]]; then
    echo "pywheel: goldens updated"
    exit 0
fi
echo "pywheel: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
