#!/usr/bin/env bash
# Lower one Flow program to LLVM IR through MLIR.
#
#   compiler/scripts/flow_to_llvm.sh [--wasm32] [--optimize OLEVEL] IN.flow OUT.ll
#
# compiler/scripts/flow_to_mlir.sh writes the MLIR (the Flow emitter,
# compiler/src/mlirgen.flow) and compiler/scripts/mlir_lower.sh lowers it.
# This is the path `flow compile --backend=mlir` takes; the bpf and wasm32
# targets (scripts/tools/llvm_target) and `flow wasm --backend=mlir`
# (scripts/tools/wasm_build) use it too.
#
# --wasm32  ILP32 ABI: libc size_t/long as i32 (flow_to_mlir.sh --wasm32).
# --optimize OLEVEL  accepted for the callers (bpf_gen.flow, llvm_target) and
#           not applied: the Flow path leaves optimisation to clang, which
#           the callers run at the same level.
#
# Exit status: 0 with OUT written; 1 when the program does not compile (the
# diagnostics are on stderr); 3 when mlir-opt/mlir-translate are missing.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"

emit_args=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --wasm32) emit_args+=(--wasm32); shift ;;
        --optimize) shift 2 ;;
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

# FLOWC_BACKEND=bpf|wasm (compiler/src/bpf_gen.flow, wasm_gen.flow) run this
# script; the inner flowc must not inherit that mode.
unset FLOWC_BACKEND

"$ROOT/compiler/scripts/flow_to_mlir.sh" ${emit_args[@]+"${emit_args[@]}"} "$in" "$work/program.mlir" || exit 1
"$ROOT/compiler/scripts/mlir_lower.sh" "$work/program.mlir" "$out"
