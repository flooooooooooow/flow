#!/bin/bash
# Build and run the adaptive ordering benchmark (issue #145).
#
#   benchmarks/ordering/run.sh          three runs, plans printed first
#   benchmarks/ordering/run.sh 5        five runs
#
# The plan report comes from `--explain`, so the timings and the plans that
# produced them always come from the same build.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNS="${1:-3}"
SRC="$ROOT/benchmarks/ordering/adaptive_sort_bench.flow"
OUT="$(mktemp -d 2>/dev/null || mktemp -d -t flow_order_bench)"

export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

echo "== plans =="
python3 -m flow.transpiler "$SRC" --c --strict --explain -o "$OUT/bench.c" 2>&1 \
    | grep -E '^\[[0-9]+\] sort|^      chose ' \
    | sed 's/^      //'

echo
echo "== timings (seconds for 100 sorts of 32768 elements, plus one copy each) =="
clang -O2 -Wno-everything "$OUT/bench.c" -o "$OUT/bench" -lm

for i in $(seq 1 "$RUNS"); do
    echo "-- run $i"
    "$OUT/bench"
done

rm -rf "$OUT"
