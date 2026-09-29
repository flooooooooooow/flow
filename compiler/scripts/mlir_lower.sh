#!/usr/bin/env bash
# Lower textual MLIR to LLVM IR with mlir-opt and mlir-translate.
#
# This is the process-orchestration half of src/flow/mlir_jit.py
# (MLIRJIT.compile_mlir_to_llvm) as a shell script, so the Flow MLIR emitter
# (compiler/src/mlirgen.flow, FLOWC_EMIT=mlir) needs no Python to reach an
# executable. The pass list is the Python one, in the same order.
#
#   compiler/scripts/mlir_lower.sh <in.mlir> <out.ll>
#   compiler/scripts/mlir_lower.sh --tools     # print the tool paths and exit
#
# Tool lookup, as in mlir_jit.py: $MLIR_OPT / $MLIR_TRANSLATE, then
# $LLVM_PATH/<tool>, then PATH, then `brew --prefix llvm`/bin.
set -euo pipefail

find_tool() {
    local name="$1" override="$2"
    if [[ -n "$override" ]]; then
        printf '%s\n' "$override"
        return 0
    fi
    if [[ -n "${LLVM_PATH:-}" && -x "${LLVM_PATH}/${name}" ]]; then
        printf '%s\n' "${LLVM_PATH}/${name}"
        return 0
    fi
    if command -v "$name" >/dev/null 2>&1; then
        command -v "$name"
        return 0
    fi
    if command -v brew >/dev/null 2>&1; then
        local prefix
        prefix="$(brew --prefix llvm 2>/dev/null || true)"
        if [[ -n "$prefix" && -x "$prefix/bin/$name" ]]; then
            printf '%s\n' "$prefix/bin/$name"
            return 0
        fi
    fi
    return 1
}

MLIR_OPT_BIN="$(find_tool mlir-opt "${MLIR_OPT:-}")" || {
    echo "mlir_lower: mlir-opt not found (brew install llvm, or set LLVM_PATH)" >&2
    exit 3
}
MLIR_TRANSLATE_BIN="$(find_tool mlir-translate "${MLIR_TRANSLATE:-}")" || {
    echo "mlir_lower: mlir-translate not found (brew install llvm, or set LLVM_PATH)" >&2
    exit 3
}

if [[ "${1:-}" == "--tools" ]]; then
    printf 'mlir-opt=%s\nmlir-translate=%s\n' "$MLIR_OPT_BIN" "$MLIR_TRANSLATE_BIN"
    exit 0
fi

if [[ $# -ne 2 ]]; then
    echo "usage: $0 <in.mlir> <out.ll>" >&2
    exit 2
fi
in="$1"
out="$2"
lowered="${out%.ll}.lowered.mlir"

# vector.transfer_* -> scf/vector.load-store must run before scf-to-cf, and
# convert-vector-to-llvm before func-to-llvm (same order as mlir_jit.py).
"$MLIR_OPT_BIN" \
    --convert-linalg-to-loops \
    --convert-vector-to-scf \
    --convert-math-to-llvm \
    --convert-scf-to-cf \
    --memref-expand \
    --convert-vector-to-llvm \
    --convert-arith-to-llvm \
    --convert-index-to-llvm \
    --convert-cf-to-llvm \
    --convert-func-to-llvm \
    --finalize-memref-to-llvm \
    --reconcile-unrealized-casts \
    "$in" -o "$lowered" </dev/null
"$MLIR_TRANSLATE_BIN" --mlir-to-llvmir "$lowered" -o "$out" </dev/null
rm -f "$lowered"
