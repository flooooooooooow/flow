#!/bin/bash

# FLOW Performance Benchmark Suite
# Quick setup and run script
# Run from project root: ./scripts/bench.sh

set -e

# Get project root (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "🚀 FLOW Performance Benchmark Suite"
echo "=================================="

# Check dependencies
check_deps() {
    echo "🔍 Checking dependencies..."
    
    if ! command -v clang &> /dev/null; then
        echo "❌ clang not found. Please install Xcode Command Line Tools."
        exit 1
    fi
    
    if ! python3 --version &> /dev/null; then
        echo "python3 not found: the Python comparison subjects will be skipped."
    fi
    
    echo "✅ Dependencies OK"
}

# Setup environment
setup_env() {
    echo "🔧 Setting up environment..."
    
    
    # Create temp directory
    mkdir -p /tmp/flow_benchmarks
    
    echo "✅ Environment ready"
}

# Run C benchmarks only
run_c() {
    echo "🔨 Compiling C benchmarks..."
    cd benchmarks
    clang -O3 -march=native -lm c_benchmarks.c -o c_benchmarks
    
    echo "🚀 Running C benchmarks..."
    ./c_benchmarks
    cd ..
}

# Run FLOW benchmarks only
run_flow() {
    echo "🚀 Running FLOW benchmarks..."
    scripts/run_bench.sh benchmarks/main.flow
}

# Run full comparison
run_comparison() {
    echo "🎯 Running full benchmark comparison..."
    cd benchmarks
    ./run_benchmarks.sh --cleanup
    cd ..
}

# Main menu
case "${1:-comparison}" in
    "c")
        check_deps
        setup_env
        run_c
        ;;
    "flow")
        check_deps
        setup_env
        run_flow
        ;;
    "comparison")
        check_deps
        setup_env
        run_comparison
        ;;
    "help")
        echo "Usage: $0 [c|flow|comparison|help]"
        echo "  c          - Run C benchmarks only"
        echo "  flow       - Run FLOW benchmarks only" 
        echo "  comparison - Run full comparison (default)"
        echo "  help       - Show this help"
        ;;
    *)
        echo "Unknown option: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

echo "✅ Done!"
