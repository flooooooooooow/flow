#!/usr/bin/env bash
# Flow vs Go concurrency microbenchmarks
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "=== Flow vs Go concurrency benches ==="
echo "Machine: $(uname -m) $(uname -s)"
echo "Date: $(date -u +%Y-%m-%d)"
echo ""

run_flow() {
  local name="$1"
  echo "--- Flow: $name ---"
  local out
  out=$(FLOW_CFLAGS='-O2 -fno-omit-frame-pointer' ./flow run "benchmarks/concurrency/${name}.flow" 2>&1) || true
  echo "$out" | grep -E '^flow_' || echo "$out" | tail -20
  echo ""
}

run_go() {
  local name="$1"
  if ! command -v go >/dev/null 2>&1; then
    echo "--- Go: $name (skipped — go not installed) ---"
    echo ""
    return
  fi
  echo "--- Go: $name ---"
  (cd "$DIR" && go run "${name}.go")
  echo ""
}

run_flow channel_throughput
run_go channel_throughput
run_flow chan_pingpong
run_flow chan_pingpong_fiber
run_go chan_pingpong
run_flow fiber_fanout
run_go fiber_fanout
run_flow parallel_sum
run_go parallel_sum
run_flow http_server
run_go http_server

echo "Done. See benchmarks/concurrency/RESULTS.md + docs/language/replace-go.md"
