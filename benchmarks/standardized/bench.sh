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

# Microsecond wall clock without Python: the Flow benchmark harness prints it.
TIMER="$FLOW_ROOT/$("$FLOW_ROOT/scripts/tools/build_tool.sh" bench_harness)"
now_us() {
    "$TIMER" --now-us
}

# The NumPy subject in benchmarks/baselines/python/standardized reports its
# own time. It is skipped when python3 or NumPy is missing.
run_python_subject() {
    local subject=$1
    local iterations=${2:-10}
    echo -n "  python numpy    "
    if ! python3 --version >/dev/null 2>&1; then
        echo "skipped (python3 not found)"
        return 0
    fi
    local total=0
    local out result mean
    for i in $(seq 1 $iterations); do
        if ! out=$(python3 "$subject" 2>/dev/null); then
            echo "skipped (the subject did not run; is NumPy installed?)"
            return 0
        fi
        result=$(printf '%s\n' "$out" | grep -oE '^[0-9.]+' | head -1)
        if [ -n "$result" ]; then
            total=$(echo "$total + $result" | bc)
        fi
    done
    mean=$(echo "scale=1; $total / $iterations" | bc)
    echo "mean ${mean} µs"
}

run_benchmark() {
    local name=$1
    local flow_file=$2
    local iterations=${3:-10}
    
    echo -n "  flow            "
    
    # Compile Flow to C, then to binary
    cd "$FLOW_ROOT"
    compiler/scripts/flowc_emit.sh --lenient "$flow_file" "$BUILD_DIR/${name}.c" 2>/dev/null
    clang $C_FLAGS -D_DEFAULT_SOURCE -Iruntime -lm "$BUILD_DIR/${name}.c" -o "$BUILD_DIR/${name}" 2>/dev/null
    
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
        local start=$(now_us)
        for i in $(seq 1 $iterations); do
            "$BUILD_DIR/${name}" >/dev/null 2>&1
        done
        local end=$(now_us)
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
run_python_subject "$FLOW_ROOT/benchmarks/baselines/python/standardized/record_numpy.py"

echo "json"
run_benchmark "json" "$SCRIPT_DIR/json/json.flow"

echo ""
echo "Done."
