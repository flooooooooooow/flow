#!/bin/bash
# Flow Language Benchmark Suite
# Compares Flow, C, and Python performance

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           FLOW LANGUAGE BENCHMARK SUITE                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Build directory
mkdir -p build

# Optimization flags
C_FLAGS="-O3 -march=native -ffast-math"
FLOW_ROOT="$(cd ../.. && pwd)"

# CPython subjects live in benchmarks/baselines/python/suite. They run when
# python3 works, and the NumPy variant runs too when NumPy is installed.
PY_SUBJECTS="$FLOW_ROOT/benchmarks/baselines/python/suite"
if python3 --version >/dev/null 2>&1; then HAVE_PY=1; else HAVE_PY=0; fi

run_python() {
    local stem=$1
    local plain="$PY_SUBJECTS/${stem}.py"
    local numpy="$PY_SUBJECTS/${stem}_numpy.py"
    echo -e "${BLUE}────────────────────────────────────────${NC}"
    echo -e "${BLUE}  Python 3${NC}"
    echo -e "${BLUE}────────────────────────────────────────${NC}"
    if [ "$HAVE_PY" -ne 1 ]; then
        echo "python3 not found; skipping the Python subject"
        return 0
    fi
    if [ ! -f "$plain" ]; then
        echo "no Python subject for ${stem}"
        return 0
    fi
    python3 "$plain"
    if [ -f "$numpy" ] && python3 -c "import numpy" >/dev/null 2>&1; then
        echo ""
        echo -e "${BLUE}  Python 3 + NumPy${NC}"
        python3 "$numpy"
    fi
}

run_benchmark() {
    local name=$1
    local num=$2
    
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  BENCHMARK: $name${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Compile C version
    echo -e "${GREEN}[C] Compiling with: clang $C_FLAGS${NC}"
    clang $C_FLAGS -lm "c/${num}_${name}.c" -o "build/${num}_${name}_c"
    echo ""
    
    # Compile Flow version - generate C, then compile with same flags as C benchmark
    echo -e "${GREEN}[Flow] Compiling with same flags as C...${NC}"
    cd "$FLOW_ROOT"
    # Generate C code with flowc (--lenient downgrades type errors to warnings)
    ./flow tool compiler/scripts/flowc_emit.flow --lenient "benchmarks/suite/flow/${num}_${name}.flow" "build/${num}_${name}.c" 2>&1 | head -5 || true
    # Check if C file was created
    if [ -f "build/${num}_${name}.c" ]; then
        # Compile with optimizations
        clang $C_FLAGS -lm "build/${num}_${name}.c" -o "benchmarks/suite/build/${num}_${name}_flow" 2>&1 || echo "Clang compilation failed"
    else
        echo "C file not generated, trying direct compile..."
        ./flow compile "benchmarks/suite/flow/${num}_${name}.flow" 2>&1 | head -3 || true
        if [ -f "build/${num}_${name}" ]; then
            cp "build/${num}_${name}" "benchmarks/suite/build/${num}_${name}_flow"
        fi
    fi
    cd "$SCRIPT_DIR"
    echo ""
    
    # Run C version
    echo -e "${BLUE}────────────────────────────────────────${NC}"
    echo -e "${BLUE}  C (clang -O3)${NC}"
    echo -e "${BLUE}────────────────────────────────────────${NC}"
    ./build/${num}_${name}_c
    echo ""
    
    # Run Flow version
    echo -e "${BLUE}────────────────────────────────────────${NC}"
    echo -e "${BLUE}  Flow (compiled to C)${NC}"
    echo -e "${BLUE}────────────────────────────────────────${NC}"
    ./build/${num}_${name}_flow
    echo ""
    
    # Run the CPython subjects (benchmarks/baselines/python/suite)
    run_python "${num}_${name}"
    echo ""
}

# Parse arguments
BENCHMARK=""
if [ $# -ge 1 ]; then
    case "$1" in
        1|fib|fibonacci)
            BENCHMARK="fibonacci"
            ;;
        2|nbody)
            BENCHMARK="nbody"
            ;;
        3|matmul)
            BENCHMARK="matmul"
            ;;
        4|spectral)
            BENCHMARK="spectral"
            ;;
        5|spmv)
            BENCHMARK="spmv"
            ;;
        6|audio|audio_rt)
            BENCHMARK="audio_rt"
            ;;
        all|"")
            BENCHMARK="all"
            ;;
        *)
            echo "Usage: $0 [benchmark]"
            echo "  Benchmarks: fibonacci, nbody, matmul, spectral, spmv, audio_rt, all"
            exit 1
            ;;
    esac
else
    BENCHMARK="all"
fi

# Run benchmarks
if [ "$BENCHMARK" = "all" ] || [ "$BENCHMARK" = "fibonacci" ]; then
    run_benchmark "fibonacci" "01"
fi

if [ "$BENCHMARK" = "all" ] || [ "$BENCHMARK" = "nbody" ]; then
    run_benchmark "nbody" "02"
fi

if [ "$BENCHMARK" = "all" ] || [ "$BENCHMARK" = "matmul" ]; then
    run_benchmark "matmul" "03"
fi

if [ "$BENCHMARK" = "all" ] || [ "$BENCHMARK" = "spectral" ]; then
    run_benchmark "spectral" "04"
fi

if [ "$BENCHMARK" = "all" ] || [ "$BENCHMARK" = "spmv" ]; then
    run_benchmark "spmv" "05"
fi

if [ "$BENCHMARK" = "all" ] || [ "$BENCHMARK" = "audio_rt" ]; then
    run_benchmark "audio_rt" "06"
fi

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    BENCHMARKS COMPLETE                       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
