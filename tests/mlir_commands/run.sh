#!/usr/bin/env bash
# MLIR command goldens: `flow mlir`, `mlir-run`, `jit`, `ml`, `test-mlir`,
# `test-matmul`, `compile-audio --mlir`, `--mlir-gpu`, `--emit-spirv` and the
# optimizer pass pipelines, checked against the goldens in
# tests/mlir_commands/expected/. They were recorded from the Python MLIR stack
# at bb23f19f; the cases whose MLIR the emitter fixes changed (the text, and
# jit_spans and audio_offline, which now print what the C backend prints)
# were re-recorded from flowc with --record.
#
#   tests/mlir_commands/run.sh                 check this checkout, python stubbed
#   tests/mlir_commands/run.sh --record ROOT [NAME...]
#                                              rewrite the goldens from the flow at ROOT
#   tests/mlir_commands/run.sh --only NAME...  check the named cases only
#
# Check mode puts python and python3 shims that log and exit 127 first on
# PATH, so a Python fallback fails the case instead of hiding. JIT cases run
# with FLOW_JIT_LINK_RUNTIME=0 as recorded (the runtime link was broken at
# bb23f19f: flow_async_worker undefined); jit_*_rt cases link the runtime and
# share the plain golden.
#
# Needs mlir-opt and mlir-translate (LLVM_PATH, or brew --prefix llvm).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO="$(cd "$HERE/../.." && pwd -P)"
EXP="$HERE/expected"
NORM="$REPO/compiler/scripts/mlir_normalize.awk"

mode=check
root="$REPO"
only=()
case "${1:-}" in
    --record) mode=record; root="$(cd "${2:?usage: run.sh --record ROOT}" && pwd -P)"; shift 2; only=("$@") ;;
    --only) shift; only=("$@") ;;
    "") ;;
    *) echo "usage: $0 [--record ROOT | --only NAME...]" >&2; exit 2 ;;
esac

if [[ -z "${LLVM_PATH:-}" ]] && command -v brew >/dev/null 2>&1; then
    p="$(brew --prefix llvm 2>/dev/null || true)"
    [[ -n "$p" && -x "$p/bin/mlir-opt" ]] && export LLVM_PATH="$p/bin"
fi

WORK="$(mktemp -d "${TMPDIR:-/tmp}/flow-mlir-commands.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
if [[ "$mode" == check ]]; then
    mkdir -p "$WORK/nopy"
    printf '#!/bin/sh\necho "python invoked: $0 $*" >&2\nexit 127\n' > "$WORK/nopy/python3"
    cp "$WORK/nopy/python3" "$WORK/nopy/python"
    chmod +x "$WORK/nopy/python3" "$WORK/nopy/python"
    export PATH="$WORK/nopy:$PATH"
else
    mkdir -p "$EXP"
fi
export FLOW_JIT_LINK_RUNTIME="${FLOW_JIT_LINK_RUNTIME_OVERRIDE:-0}"

# Driver progress lines, Python host chatter, timings and the checkout path
# are not behaviour; the program output, results and failures are.
filter() {
    sed -E $'s/\x1b\\[[0-9;]*m//g' \
        | sed -e "s#$root#<ROOT>#g" -e "s#$WORK#<WORK>#g" -E -e 's#/build/run\.[A-Za-z0-9]{6}/#/build/run.X/#g' \
        | awk '/^module( attributes.*)? \{$/ { skip = 1 } skip && /-{20,}$/ { skip = 0; next } !skip' \
        | awk 'gf && /^[0-9.]+$/ { print "<GFLOPS>"; gf = 0; next } { gf = /^(Naive|Vectorized \((unroll|auto)\)|Parallelized|Tiled \+ .*|Baseline \(Flow naive GFLOP\/s\)):$/; print }' \
        | awk '/^MLIR: / { asm = 0 } asm { next } /^Assembly: / { print; print "<ASM>"; asm = 1; next } { print }' \
        | grep -vE '^(ℹ️|🚀)' \
        | grep -vE '^✅ (Generated|FLOW|MLIR|LLVM|Built|C →|🎧|🚀)' \
        | grep -vE '^⚠️ +flowc MLIR emitter' \
        | grep -vE '^(Resolving modules|Parsed [0-9]+ functions|Generated (MLIR|LLVM IR|SPIR-V)|Type warnings|  ⚠ |  \.\.\. and |Input file:)' \
        | grep -vE '^(real|user|sys) +[0-9.]+$' \
        | grep -vE '^-{20,}$' \
        | grep -vE 'overriding the module target triple|^[0-9]+ warnings? generated\.$' \
        || true
}

pipeline_of() {
    if [[ -f "$root/tools/flow_cli/mlir_tools.flow" ]]; then
        "$root/flow" mlir-optimize --print-pass-pipeline "$@"
    else
        PYTHONPATH="$root/src" python3 -m flow.transpiler --print-pass-pipeline "$@"
    fi
}

# run_case NAME KIND ARGS... -> writes $WORK/got/NAME.*
run_case() {
    local name="$1" kind="$2"
    shift 2
    local d="$WORK/case/$name"
    mkdir -p "$d/build" "$WORK/got"
    local args=() a run_after=0
    for a in "$@"; do
        a="${a//@WORK@/$d}"
        if [[ "$a" == "@RUN@" ]]; then run_after=1; continue; fi
        args+=("$a")
    done
    local g="$WORK/got/$name" rc=0 prog base
    case "$kind" in
        mlir|raw|spirv)
            prog="${args[0]}"
            base="$(basename "$prog" .flow)"
            (cd "$root" && FLOW_BUILD_ROOT="$d/build" ./flow mlir "${args[@]}" >"$d/log" 2>&1) || rc=$?
            echo "$rc" > "$g.rc"
            if [[ "$kind" == mlir ]]; then
                [[ -f "$d/build/$base.mlir" ]] && awk -f "$NORM" "$d/build/$base.mlir" > "$g.mlir"
            elif [[ "$kind" == raw ]]; then
                [[ -f "$d/build/$base.mlir" ]] && sed -e "s#$root#<ROOT>#g" "$d/build/$base.mlir" > "$g.txt"
            else
                if [[ -s "$d/k.spv" ]]; then shasum -a 256 < "$d/k.spv" | cut -d' ' -f1 > "$g.sha"; fi
            fi
            ;;
        pipeline)
            (cd "$root" && pipeline_of ${args[@]+"${args[@]}"}) > "$g.txt" 2>"$d/log" || rc=$?
            echo "$rc" > "$g.rc"
            ;;
        out)
            local rt="$FLOW_JIT_LINK_RUNTIME"
            [[ "$name" == *_rt ]] && rt=1
            (cd "$root" && FLOW_JIT_LINK_RUNTIME="$rt" timeout 600 ./flow "${args[@]}" </dev/null >"$d/log" 2>&1) || rc=$?
            if [[ "$run_after" -eq 1 ]]; then
                base="$(basename "${args[1]}" .flow)"
                if [[ -x "$root/build/$base" ]]; then
                    echo "== run $base" >> "$d/log"
                    (cd "$d" && timeout 60 "$root/build/$base" </dev/null >>"$d/log" 2>&1) || echo "run exit=$?" >> "$d/log"
                fi
            fi
            filter < "$d/log" > "$g.out"
            echo "$rc" > "$g.rc"
            ;;
        *) echo "unknown kind $kind" >&2; return 1 ;;
    esac
}

pass=0
fail=0
failed=()
while read -r name kind rest; do
    [[ -z "$name" || "$name" == \#* ]] && continue
    if [[ ${#only[@]} -gt 0 ]]; then
        hit=0
        for o in "${only[@]}"; do [[ "$o" == "$name" ]] && hit=1; done
        [[ "$hit" -eq 1 ]] || continue
    fi
    [[ "$mode" == record && "$name" == *_rt ]] && continue
    # shellcheck disable=SC2086
    run_case "$name" "$kind" $rest
    gold="${name%_rt}"
    if [[ "$mode" == record ]]; then
        rm -f "$EXP/$name".*
        cp "$WORK/got/$name".* "$EXP/"
        echo "recorded $name (rc=$(cat "$WORK/got/$name.rc"))"
        continue
    fi
    ok=1
    for f in "$EXP/$gold".*; do
        [[ -e "$f" ]] || { ok=0; break; }
        want_ext="${f##*.}"
        if ! cmp -s "$f" "$WORK/got/$name.$want_ext"; then
            ok=0
            echo "FAIL $name: $want_ext differs" >&2
            diff "$f" "$WORK/got/$name.$want_ext" 2>&1 | head -15 >&2
        fi
    done
    for f in "$WORK/got/$name".*; do
        [[ -e "$EXP/$gold.${f##*.}" ]] || { ok=0; echo "FAIL $name: unexpected ${f##*.} output" >&2; }
    done
    if [[ "$ok" -eq 1 ]]; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        failed+=("$name")
        grep -m3 -E 'python invoked|flowc mlir' "$WORK/case/$name/log" >&2 || true
    fi
done < "$HERE/cases.txt"

if [[ "$mode" == record ]]; then
    exit 0
fi
echo "mlir_commands: pass=$pass fail=$fail"
[[ "$fail" -eq 0 ]] || { echo "failed: ${failed[*]}"; exit 1; }
