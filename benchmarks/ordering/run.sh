#!/bin/bash
# Build and run the adaptive ordering benchmark (issue #145).
#
#   benchmarks/ordering/run.sh          three runs
#   benchmarks/ordering/run.sh 5        five runs
#
# The program is compiled with flowc. flowc has no sort plan selection and
# no `--explain`: every sort is a stable insertion sort. The plan report that
# the retired Python C backend printed is gone, so this script prints timings
# only. They measure flowc's single sort strategy.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNS="${1:-3}"
SRC="$ROOT/benchmarks/ordering/adaptive_sort_bench.flow"
OUT="$(mktemp -d 2>/dev/null || mktemp -d -t flow_order_bench)"

"$ROOT/compiler/scripts/flowc_emit.sh" --strict "$SRC" "$OUT/bench.c"

echo "== timings (seconds for 100 sorts of 32768 elements, plus one copy each) =="
clang -O2 -Wno-everything -D_DEFAULT_SOURCE -I"$ROOT/runtime" "$OUT/bench.c" -o "$OUT/bench" -lm

for i in $(seq 1 "$RUNS"); do
    echo "-- run $i"
    "$OUT/bench"
done

rm -rf "$OUT"
