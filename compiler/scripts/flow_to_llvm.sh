#!/usr/bin/env bash
# Lower one Flow program to LLVM IR through MLIR.
#
#   compiler/scripts/flow_to_llvm.sh [--wasm32] [--optimize OLEVEL] IN.flow OUT.ll
#
# The Flow MLIR emitter (compiler/src/mlirgen.flow, FLOWC_EMIT=mlir) writes
# the MLIR and compiler/scripts/mlir_lower.sh lowers it, with no Python. This
# is the path `flow compile --backend=mlir` takes. A program outside the
# emitter's slice (flowc prints `flowc mlir: ...`) falls back to the Python
# MLIR generator, `python3 -m flow.transpiler --llvm`, with a warning on
# stderr. The bpf and wasm32 targets (scripts/tools/llvm_target) use this.
#
# --wasm32  ILP32 ABI. The Flow emitter has no size_t width option, so a
#           program that declares external functions (whose size_t/long
#           parameters would change width) goes to the Python generator,
#           which lowers them as i32.
# --optimize OLEVEL  passed to the Python generator as --optimize
#           --opt-level OLEVEL. The Flow path leaves optimisation to clang,
#           which the callers run at the same level.
#
# Exit status: 0 with OUT written; 1 when the program does not compile (the
# diagnostics are on stderr); 3 when mlir-opt/mlir-translate are missing.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"

wasm32=0
opt=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --wasm32) wasm32=1; shift ;;
        --optimize) opt="${2:-}"; shift 2 ;;
        *) break ;;
    esac
done
if [[ $# -ne 2 ]]; then
    echo "usage: $0 [--wasm32] [--optimize OLEVEL] IN.flow OUT.ll" >&2
    exit 2
fi
in="$1"
out="$2"

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-to-llvm.XXXXXX")"
trap 'rm -rf "$work"' EXIT

flowc="${FLOWC_BIN:-}"
if [[ -z "$flowc" || ! -x "$flowc" ]]; then
    boot_c="$ROOT/compiler/bootstrap/flowc_stage_a.c"
    flowc="$ROOT/compiler/build/flowc_bootstrap"
    if [[ ! -x "$flowc" || "$boot_c" -nt "$flowc" ]]; then
        mkdir -p "$ROOT/compiler/build"
        if ! "${CC:-cc}" -O2 -w -o "$flowc.tmp.$$" "$boot_c" -lm >/dev/null 2>&1; then
            echo "flow_to_llvm: could not build flowc from $boot_c" >&2
            exit 1
        fi
        mv -f "$flowc.tmp.$$" "$flowc"
    fi
fi

refusal=""
if FLOWC_EMIT=mlir FLOWC_TYPECHECK="${FLOWC_TYPECHECK:-1}" \
    FLOWC_IN="$in" FLOWC_OUT="$work/program.mlir" \
    "$flowc" >"$work/flowc.log" 2>&1 \
    && head -1 "$work/program.mlir" | grep -q '^module'; then
    if [[ "$wasm32" -eq 1 ]] && grep -q 'func\.func private' "$work/program.mlir"; then
        refusal="external functions need the wasm32 size_t ABI"
    fi
elif grep -q 'flowc mlir' "$work/flowc.log"; then
    refusal="$(grep -m1 'flowc mlir' "$work/flowc.log")"
elif [[ ! -s "$work/program.mlir" ]] && ! grep -q . "$work/flowc.log"; then
    refusal="$flowc does not know FLOWC_EMIT=mlir"
else
    cat "$work/flowc.log" >&2
    exit 1
fi

if [[ -z "$refusal" ]]; then
    "$ROOT/compiler/scripts/mlir_lower.sh" "$work/program.mlir" "$out"
    exit $?
fi

echo "flow_to_llvm: flowc MLIR emitter does not cover $in yet ($refusal); using the Python MLIR generator" >&2
args=("$in" --llvm)
[[ "$wasm32" -eq 1 ]] && args+=(--wasm32)
[[ -n "$opt" ]] && args+=(--optimize --opt-level "$opt")
PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}" python3 -m flow.transpiler "${args[@]}" -o "$out"
