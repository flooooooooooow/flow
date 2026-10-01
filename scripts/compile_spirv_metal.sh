#!/usr/bin/env bash
# Compile Flow GPU kernels through SPIR-V to MSL or a native Metal library.
#
#   scripts/compile_spirv_metal.sh IN.flow|IN.spv [-o OUT] [--msl-only]
#       [--sdk SDK] [--spirv-cross-arg ARG ...]
#
# A Flow source goes through `flow mlir --mlir-gpu --emit-spirv`; an .spv is
# used as is. SPIRV-Cross lowers the SPIR-V to Metal Shading Language
# (--msl-only stops there), then xcrun metal and metallib build the library.
# OUT defaults to build/<stem>.metallib, or build/<stem>.metal with
# --msl-only. The steps are `flow mlir-spirv` (tools/flow_cli/mlir_tools.flow).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

usage() {
    echo "usage: $0 IN.flow|IN.spv [-o OUT] [--msl-only] [--sdk SDK] [--spirv-cross-arg ARG]" >&2
    exit 2
}

input=""
output=""
msl_only=0
sdk=macosx
cross_args=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output) output="${2:-}"; shift ;;
        --msl-only) msl_only=1 ;;
        --sdk) sdk="${2:-}"; shift ;;
        --spirv-cross-arg) cross_args+=("${2:-}"); shift ;;
        -h|--help) usage ;;
        -*) usage ;;
        *) [[ -z "$input" ]] || usage; input="$1" ;;
    esac
    shift
done
[[ -n "$input" ]] || usage
if [[ ! -e "$input" ]]; then
    echo "$0: error: input does not exist: $input" >&2
    exit 2
fi
stem="$(basename "$input")"
stem="${stem%.*}"
if [[ -z "$output" ]]; then
    if [[ "$msl_only" -eq 1 ]]; then
        output="$ROOT/build/$stem.metal"
    else
        output="$ROOT/build/$stem.metallib"
    fi
fi
mkdir -p "$(dirname "$output")"

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-spirv-metal.XXXXXX")"
trap 'rm -rf "$work"' EXIT
SPIRV=("$ROOT/flow" mlir-spirv)

fail() {
    echo "Metal compilation failed: $*" >&2
    exit 1
}

spv="$input"
case "$input" in
    *.spv|*.SPV) ;;
    *)
        spv="$work/$stem.spv"
        if ! FLOW_BUILD_ROOT="$work" "$ROOT/flow" mlir "$input" --mlir-gpu --emit-spirv \
            --spirv-out "$spv" >"$work/flow.log" 2>&1; then
            fail "Flow -> SPIR-V compilation failed:
$(cat "$work/flow.log")"
        fi
        ;;
esac

if [[ "$msl_only" -eq 1 ]]; then
    "${SPIRV[@]}" msl "$spv" "$output" ${cross_args[@]+"${cross_args[@]}"} 2>"$work/err" \
        || fail "$(cat "$work/err")"
else
    "${SPIRV[@]}" msl "$spv" "$work/$stem.metal" ${cross_args[@]+"${cross_args[@]}"} 2>"$work/err" \
        || fail "$(cat "$work/err")"
    "${SPIRV[@]}" metallib "$work/$stem.metal" "$output" "$sdk" 2>"$work/err" \
        || fail "$(cat "$work/err")"
fi
echo "Generated Metal artifact: $output"
