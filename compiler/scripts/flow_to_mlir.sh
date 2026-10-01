#!/usr/bin/env bash
# Emit the MLIR of one Flow program with the Flow MLIR emitter.
#
#   compiler/scripts/flow_to_mlir.sh [--gpu] [--wasm32] [--jit] [--lenient] IN.flow OUT.mlir
#
# flowc (compiler/src/mlirgen.flow, FLOWC_EMIT=mlir) writes the MLIR. Every
# MLIR command goes through here: `flow mlir`, `mlir-run`, `jit`, `ml`,
# `test-mlir`, `test-matmul`, `compile-audio --mlir`, `--backend=mlir` and
# compiler/scripts/flow_to_llvm.sh (bpf, wasm32, wasm --backend=mlir).
#
# --gpu     @gpu kernels as a gpu.module (FLOWC_MLIR_GPU=1, Python --mlir-gpu)
# --wasm32  ILP32 ABI: libc size_t/long as i32 (FLOWC_MLIR_SIZE_T=32)
# --jit     guard modes jit, mlir and compile (FLOWC_MODE=jit adds jit to the
#           compile and mlir modes the emitter always has), as the JIT
#           runner used; otherwise compile and mlir. The JIT runner did
#           not typecheck, so --jit also implies --lenient.
# --lenient type errors that are not fatal are warnings (FLOWC_LENIENT=1,
#           Python --lenient); otherwise any type error fails the program
#
# FLOWC_BIN selects the compiler; otherwise compiler/build/flowc_bootstrap,
# built from compiler/bootstrap/flowc_stage_a.c when missing or stale.
# FLOWC_TYPECHECK (default 1), FLOWC_CHECKS (default 1: the runtime checks
# of division, shifts and array reads the C backend emits) and FLOWC_ROOT
# (default the checkout) pass through.
#
# The emitter covers every program the retired Python MLIR generator lowered
# (compiler/scripts/parity_mlir.flow); a program it refuses fails here, with
# `flowc mlir: unsupported: ...` on stderr.
#
# A program with @cEmbed C also gets OUT.c (the C with the standard headers
# ahead of it), which the caller compiles and links with the lowered MLIR.
#
# Exit status: 0 with OUT written; 1 when the program does not compile (the
# diagnostics are on stderr).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"

gpu=0
wasm32=0
modes=""
lenient=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --gpu) gpu=1; shift ;;
        --wasm32) wasm32=1; shift ;;
        --jit) modes="jit,mlir,compile"; lenient=1; shift ;;
        --lenient) lenient=1; shift ;;
        *) break ;;
    esac
done
if [[ $# -ne 2 ]]; then
    echo "usage: $0 [--gpu] [--wasm32] [--jit] [--lenient] IN.flow OUT.mlir" >&2
    exit 2
fi
in="$1"
out="$2"

flowc="${FLOWC_BIN:-}"
if [[ -z "$flowc" || ! -x "$flowc" ]]; then
    boot_c="$ROOT/compiler/bootstrap/flowc_stage_a.c"
    flowc="$ROOT/compiler/build/flowc_bootstrap"
    if [[ ! -x "$flowc" || "$boot_c" -nt "$flowc" ]]; then
        mkdir -p "$ROOT/compiler/build"
        if ! "${CC:-cc}" -O2 -w -o "$flowc.tmp.$$" "$boot_c" -lm >/dev/null 2>&1; then
            echo "flow_to_mlir: could not build flowc from $boot_c" >&2
            exit 1
        fi
        mv -f "$flowc.tmp.$$" "$flowc"
    fi
fi

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-to-mlir.XXXXXX")"
trap 'rm -rf "$work"' EXIT

# FLOWC_BACKEND=bpf|wasm (compiler/src/bpf_gen.flow, wasm_gen.flow) reach
# here through flow_to_llvm.sh; the inner flowc must not inherit that mode.
env_args=(-u FLOWC_BACKEND FLOWC_EMIT=mlir "FLOWC_TYPECHECK=${FLOWC_TYPECHECK:-1}"
    "FLOWC_CHECKS=${FLOWC_CHECKS:-1}"
    "FLOWC_ROOT=${FLOWC_ROOT:-$ROOT}" "FLOWC_IN=$in" "FLOWC_OUT=$work/program.mlir"
    "FLOWC_CEMBED_OUT=$work/program.c")
[[ "$gpu" -eq 1 ]] && env_args+=(FLOWC_MLIR_GPU=1)
[[ "$wasm32" -eq 1 ]] && env_args+=(FLOWC_MLIR_SIZE_T=32)
[[ -n "$modes" ]] && env_args+=(FLOWC_MODE=jit)
if [[ "$lenient" -eq 1 ]]; then
    env_args+=(FLOWC_LENIENT=1)
else
    env_args=(-u FLOWC_LENIENT "${env_args[@]}")
fi

if env "${env_args[@]}" "$flowc" >"$work/flowc.log" 2>&1 \
    && head -1 "$work/program.mlir" 2>/dev/null | grep -q '^module'; then
    mkdir -p "$(dirname "$out")"
    cp "$work/program.mlir" "$out"
    # @cEmbed C, compiled and linked next to the lowered MLIR.
    if [[ -f "$work/program.c" ]]; then
        cp "$work/program.c" "$out.c"
    else
        rm -f "$out.c"
    fi
    # Lenient mode keeps type warnings on stderr, as Python's --lenient did.
    grep -E 'type warning' "$work/flowc.log" >&2 || true
    exit 0
fi
cat "$work/flowc.log" >&2
exit 1
