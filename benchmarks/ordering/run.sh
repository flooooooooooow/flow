#!/bin/bash
# Build and run the adaptive ordering benchmark (issue #145).
#
#   benchmarks/ordering/run.sh          three runs, plans printed first
#   benchmarks/ordering/run.sh 5        five runs
#
# The plan report comes from flowc's `flow explain` output (FLOWC_EXPLAIN=1),
# so the timings and the plans that produced them always come from the same
# build.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNS="${1:-3}"
SRC="$ROOT/benchmarks/ordering/adaptive_sort_bench.flow"
OUT="$(mktemp -d 2>/dev/null || mktemp -d -t flow_order_bench)"

echo "== plans =="
FLOWC_EXPLAIN=1 "$ROOT/flow" tool "$ROOT/compiler/scripts/flowc_emit.flow" --strict "$SRC" "$OUT/bench.c" \
    2>"$OUT/plans" >/dev/null
grep -E '^\[[0-9]+\] sort|^      chose ' "$OUT/plans" | sed 's/^      //'

echo
echo "== timings (seconds for 100 sorts of 32768 elements, plus one copy each) =="
clang -O2 -Wno-everything -D_DEFAULT_SOURCE -I"$ROOT/runtime" "$OUT/bench.c" -o "$OUT/bench" -lm

for i in $(seq 1 "$RUNS"); do
    echo "-- run $i"
    "$OUT/bench"
done

rm -rf "$OUT"
