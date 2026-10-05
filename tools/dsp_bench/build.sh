#!/usr/bin/env bash
# Build the dsp_bench tool (Apple Silicon: NEON + Metal).
set -euo pipefail
cd "$(dirname "$0")"
clang++ -O3 -std=c++17 -ffast-math -fobjc-arc \
    bench.mm \
    -framework Metal -framework Foundation \
    -o dsp_bench
echo "built ./dsp_bench"
