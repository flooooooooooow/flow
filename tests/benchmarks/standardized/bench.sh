#!/bin/bash
# Standardized benchmark runner for Flow
# Compatible with github.com/andrewmcwattersandco/programming-language-benchmarks
#
# Runs each benchmark 10 times and reports mean

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FLOW_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"

mkdir -p "$BUILD_DIR"

C_FLAGS="-O3 -march=native -ffast-math"

run_benchmark() {
    local name=$1
    local flow_file=$2
    local iterations=${3:-10}
    
    echo -n "  flow            "
    
    # Compile Flow to C, then to binary
    cd "$FLOW_ROOT"
    PYTHONPATH=src python3 -m flow.transpiler "$flow_file" --c --lenient -o "$BUILD_DIR/${name}.c" 2>/dev/null
    clang $C_FLAGS -lm "$BUILD_DIR/${name}.c" -o "$BUILD_DIR/${name}" 2>/dev/null
    
    # Run multiple times and collect timings
    local total=0
    for i in $(seq 1 $iterations); do
        # Use /usr/bin/time for wall clock, but we want the program's internal timing
        result=$("$BUILD_DIR/${name}" 2>/dev/null | grep -oE '^[0-9.]+' | head -1)
        if [ -n "$result" ]; then
            total=$(echo "$total + $result" | bc)
        fi
    done
    
    if [ "$total" != "0" ]; then
        mean=$(echo "scale=1; $total / $iterations" | bc)
        echo "mean ${mean} µs"
    else
        # For minimal, use external timing
        local start=$(python3 -c "import time; print(int(time.time() * 1000000))")
        for i in $(seq 1 $iterations); do
            "$BUILD_DIR/${name}" >/dev/null 2>&1
        done
        local end=$(python3 -c "import time; print(int(time.time() * 1000000))")
        mean=$(echo "scale=1; ($end - $start) / $iterations" | bc)
        echo "mean ${mean} µs"
    fi
}

echo "=== Flow Language Standardized Benchmarks ==="
echo "(Compatible with programming-language-benchmarks)"
echo ""

echo "minimal"
run_benchmark "minimal" "$SCRIPT_DIR/minimal/minimal.flow"

echo "record"
run_benchmark "record" "$SCRIPT_DIR/record/record.flow"

echo "json"
run_benchmark "json" "$SCRIPT_DIR/json/json.flow"

echo ""
echo "Done."
