#!/usr/bin/env bash
# Build and run the GPU microbenchmarks (gpu_microbenchmark.c) against the
# Flow GPU runtime: runtime/gpu_metal.m on macOS, the simulated figures
# elsewhere.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(cd "$HERE/../.." && pwd -P)"

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-gpu-bench.XXXXXX")"
trap 'rm -rf "$work"' EXIT

cc="${CC:-clang}"
if [[ "$(uname -s)" == Darwin ]]; then
    "$cc" -O2 -fobjc-arc -I"$ROOT/runtime" "$HERE/gpu_microbenchmark.c" "$ROOT/runtime/gpu_metal.m" \
        -framework Metal -framework Foundation -o "$work/gpu_bench"
else
    "$cc" -O2 -I"$ROOT/runtime" "$HERE/gpu_microbenchmark.c" -o "$work/gpu_bench"
fi
"$work/gpu_bench"
