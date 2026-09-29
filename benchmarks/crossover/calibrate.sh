#!/usr/bin/env bash
# C against MLIR for the crossover corpus, next to the cost model's guess.
#
# Each program runs through `./flow run --json` with each backend; the time
# is the runner's own total_s. A failed run reads Error. The last column is
# `./flow run --predict`, the backend the cost model picks. RESULTS.md holds
# a measured table.
#
# Usage: benchmarks/crossover/calibrate.sh
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

run_backend() {
    local out
    if ! out="$(./flow run "$1" "--backend=$2" --json 2>/dev/null)"; then
        echo "Error"
        return
    fi
    printf '%s\n' "$out" | sed -n 's/.*"total_s": \([0-9.]*\).*/\1/p'
}

printf '%-30s | %-12s | %-15s | %-6s | %s\n' "Program" "C Time (s)" "MLIR Time (s)" "Winner" "Predicted"
printf '%s\n' "-------------------------------------------------------------------------------------"
for f in benchmarks/crossover/*.flow; do
    c="$(run_backend "$f" c)"
    m="$(run_backend "$f" mlir)"
    winner="C"
    if [[ "$c" == "Error" && "$m" != "Error" ]]; then
        winner="MLIR"
    elif [[ "$c" != "Error" && "$m" != "Error" ]] && awk "BEGIN { exit !($m < $c) }"; then
        winner="MLIR"
    fi
    predicted="$(./flow run "$f" --predict)"
    printf '%-30s | %-12s | %-15s | %-6s | %s\n' "$(basename "$f")" "$c" "$m" "$winner" "$predicted"
done
