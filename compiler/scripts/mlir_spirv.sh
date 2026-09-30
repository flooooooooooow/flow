#!/usr/bin/env bash
# Lower an MLIR GPU module to SPIR-V, and SPIR-V on to Metal.
#
#   compiler/scripts/mlir_spirv.sh spirv IN.mlir OUT.spv [mlir-opt args...]
#   compiler/scripts/mlir_spirv.sh msl IN.spv OUT.metal [spirv-cross args...]
#   compiler/scripts/mlir_spirv.sh metallib IN.metal OUT.metallib [SDK]
#   compiler/scripts/mlir_spirv.sh mlir-msl IN.mlir OUT.metal [spirv-cross args...]
#   compiler/scripts/mlir_spirv.sh mlir-metallib IN.mlir OUT.metallib [SDK]
#
# SPIR-V is the portable GPU artifact: Vulkan takes it as is, and Apple
# targets lower it through SPIRV-Cross to Metal Shading Language, then to a
# .metallib with Xcode's xcrun metal and metallib. This is the retired
# src/flow/mlir_spirv.py (MLIRSPIRVCompiler) as a script, with its pass list
# and its messages. `flow mlir --mlir-gpu --emit-spirv` and
# scripts/compile_spirv_metal.sh run it.
#
# Tools: $MLIR_OPT / $MLIR_TRANSLATE / $SPIRV_CROSS / $XCRUN, then
# $LLVM_PATH (MLIR tools), PATH, and brew --prefix llvm or spirv-cross.
# SDK defaults to macosx.
#
# Exit status: 0, 1 when a step fails (the reason on stderr), 2 for usage.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"

die() {
    echo "$*" >&2
    exit 1
}

find_tool() {
    local name="$1" override="$2" pkg="$3"
    if [[ -n "$override" && -e "$override" ]]; then
        printf '%s\n' "$override"
        return 0
    fi
    if [[ "$pkg" == llvm && -n "${LLVM_PATH:-}" && -x "$LLVM_PATH/$name" ]]; then
        printf '%s\n' "$LLVM_PATH/$name"
        return 0
    fi
    if command -v "$name" >/dev/null 2>&1; then
        command -v "$name"
        return 0
    fi
    if [[ -n "$pkg" ]] && command -v brew >/dev/null 2>&1; then
        local prefix
        prefix="$(brew --prefix "$pkg" 2>/dev/null || true)"
        if [[ -n "$prefix" && -x "$prefix/bin/$name" ]]; then
            printf '%s\n' "$prefix/bin/$name"
            return 0
        fi
    fi
    return 1
}

require() {
    local var="$1" name="$2" override="$3" pkg="$4" path
    path="$(find_tool "$name" "$override" "$pkg")" \
        || die "$name not found ('$name'). Install it or set the matching tool override environment variable."
    printf -v "$var" '%s' "$path"
}

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-spirv.XXXXXX")"
trap 'rm -rf "$work"' EXIT

to_spirv() {
    local in="$1" out="$2"
    shift 2
    local opt translate rc=0
    require opt mlir-opt "${MLIR_OPT:-}" llvm
    require translate mlir-translate "${MLIR_TRANSLATE:-}" llvm
    # Outline kernels and lower to the SPIR-V dialect.
    "$opt" -gpu-kernel-outlining -convert-scf-to-spirv -convert-memref-to-spirv \
        -convert-arith-to-spirv -convert-index-to-spirv -convert-gpu-to-spirv \
        -reconcile-unrealized-casts "$@" "$in" -o "$work/spirv.mlir" \
        </dev/null >"$work/opt.out" 2>"$work/opt.err" || rc=$?
    if [[ "$rc" -ne 0 ]]; then
        die "mlir-opt SPIR-V lowering failed (exit $rc):
$(if [[ -s "$work/opt.err" ]]; then cat "$work/opt.err"; else cat "$work/opt.out"; fi)"
    fi
    # Serialize the SPIR-V binary.
    "$translate" --mlir-to-spirv "$work/spirv.mlir" </dev/null >"$work/out.spv" 2>"$work/tr.err" || rc=$?
    if [[ "$rc" -ne 0 ]]; then
        die "mlir-translate --mlir-to-spirv failed (exit $rc):
$(cat "$work/tr.err")"
    fi
    [[ -s "$work/out.spv" ]] || die "mlir-translate produced empty SPIR-V output"
    mkdir -p "$(dirname "$out")"
    cp "$work/out.spv" "$out"
}

to_msl() {
    local in="$1" out="$2"
    shift 2
    local cross rc=0
    require cross spirv-cross "${SPIRV_CROSS:-}" spirv-cross
    [[ -s "$in" ]] || die "SPIR-V input missing or empty: $in"
    "$cross" "$in" --msl "$@" </dev/null >"$work/out.metal" 2>"$work/cross.err" || rc=$?
    if [[ "$rc" -ne 0 ]]; then
        die "spirv-cross MSL lowering failed (exit $rc):
$(if [[ -s "$work/cross.err" ]]; then cat "$work/cross.err"; else cat "$work/out.metal"; fi)"
    fi
    grep -q '[^[:space:]]' "$work/out.metal" || die "spirv-cross produced empty MSL output"
    mkdir -p "$(dirname "$out")"
    cp "$work/out.metal" "$out"
}

to_metallib() {
    local in="$1" out="$2" sdk="${3:-macosx}"
    local xcrun rc=0
    require xcrun xcrun "${XCRUN:-}" ""
    [[ -s "$in" ]] || die "MSL input missing or empty: $in"
    mkdir -p "$(dirname "$out")"
    "$xcrun" -sdk "$sdk" metal -c "$in" -o "$work/kernel.air" </dev/null >"$work/m.log" 2>&1 || rc=$?
    [[ "$rc" -eq 0 ]] || die "Metal compilation failed (exit $rc):
$(cat "$work/m.log")"
    "$xcrun" -sdk "$sdk" metallib "$work/kernel.air" -o "$out" </dev/null >"$work/l.log" 2>&1 || rc=$?
    [[ "$rc" -eq 0 ]] || die "metallib failed (exit $rc):
$(cat "$work/l.log")"
    [[ -s "$out" ]] || die "metallib completed without producing output"
}

cmd="${1:-}"
[[ $# -ge 3 ]] || { echo "usage: $0 spirv|msl|metallib|mlir-msl|mlir-metallib IN OUT [...]" >&2; exit 2; }
in="$2"
out="$3"
shift 3
case "$cmd" in
    spirv) to_spirv "$in" "$out" "$@" ;;
    msl) to_msl "$in" "$out" "$@" ;;
    metallib) to_metallib "$in" "$out" "${1:-macosx}" ;;
    mlir-msl)
        to_spirv "$in" "$work/kernel.spv"
        to_msl "$work/kernel.spv" "$out" "$@" ;;
    mlir-metallib)
        to_spirv "$in" "$work/kernel.spv"
        to_msl "$work/kernel.spv" "$work/kernel.metal"
        to_metallib "$work/kernel.metal" "$out" "${1:-macosx}" ;;
    *) echo "usage: $0 spirv|msl|metallib|mlir-msl|mlir-metallib IN OUT [...]" >&2; exit 2 ;;
esac
