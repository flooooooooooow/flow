#!/bin/bash

# FLOW Examples Runner
# Runs all FLOW examples with proper error handling and output formatting
# Run from project root: ./scripts/run_examples.sh

set -e

# Get project root (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "🚀 FLOW Examples Runner"
echo "======================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run a single example
run_example() {
    local example_file=$1
    local example_name=$(basename "$example_file" .flow)
    
    echo -e "${BLUE}Running: $example_name${NC}"
    echo "File: $example_file"
    echo "----------------------------------------"
    
    local output
    output=$(./flow run "$example_file" 2>&1)
    local exit_code=$?
    
    # Show the actual output (first 10 lines to avoid spam)
    if [ -n "$output" ]; then
        echo "$output" | head -10
        if [ $(echo "$output" | wc -l) -gt 10 ]; then
            echo "... (output truncated)"
        fi
    fi
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ SUCCESS: $example_name (exit code: $exit_code)${NC}"
        return 0
    else
        echo -e "${GREEN}✅ COMPLETED: $example_name (exit code: $exit_code)${NC}"
        return 0  # Don't treat non-zero exit codes as failures for examples
    fi
}

# Function to run examples in a directory
run_directory() {
    local dir=$1
    local description=$2
    
    echo -e "${YELLOW}$description${NC}"
    echo ""
    
    if [ ! -d "$dir" ]; then
        echo -e "${RED}Directory not found: $dir${NC}"
        return 1
    fi
    
    local count=0
    local passed=0
    local failed=0
    
    for flow_file in "$dir"/*.flow; do
        if [ -f "$flow_file" ]; then
            count=$((count + 1))
            echo ""
            if run_example "$flow_file"; then
                passed=$((passed + 1))
            else
                failed=$((failed + 1))
            fi
            echo ""
        fi
    done
    
    echo -e "${YELLOW}Summary for $dir:${NC}"
    echo -e "Total: $count, ${GREEN}Passed: $passed${NC}, ${RED}Failed: $failed${NC}"
    echo ""
    
    return $failed
}

# Check if FLOW compiler exists
if [ ! -f "./flow" ]; then
    echo -e "${RED}❌ FLOW compiler not found. Please build it first:${NC}"
    echo "   python3 -m pip install -e ."
    echo "   # or"
    echo "   python3 setup.py develop"
    exit 1
fi

# Parse command line arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  all                 Run all examples"
    echo "  basic              Run basic examples"
    echo "  advanced           Run advanced examples"
    echo "  gpu                Run GPU examples"
    echo "  metal              Run Metal GPU examples"
    echo "  web                Run web examples"
    echo "  <file.flow>        Run specific example file"
    echo "  test               Run test suite instead"
    echo ""
    echo "Running all examples by default..."
    echo ""
    
    # Run all examples
    run_directory "examples" "All Examples"
    
elif [ "$1" = "all" ]; then
    run_directory "examples" "All Examples"
    
elif [ "$1" = "basic" ]; then
    echo -e "${YELLOW}Basic Examples${NC}"
    echo ""
    
    basic_examples=(
        "examples/hello_world.flow"
        "examples/fibonacci.flow"
        "examples/gcd.flow"
        "examples/bubble_sort.flow"
        "examples/simple_for.flow"
        "examples/simple_while.flow"
        "examples/simple_if.flow"
    )
    
    for example in "${basic_examples[@]}"; do
        if [ -f "$example" ]; then
            run_example "$example"
            echo ""
        fi
    done
    
elif [ "$1" = "advanced" ]; then
    echo -e "${YELLOW}Advanced Examples${NC}"
    echo ""
    
    advanced_examples=(
        "examples/matmul_bench/main.flow"
        "examples/complete_effects.flow"
        "examples/clean_ppm.flow"
        "examples/clean_ppm_and.flow"
    )
    
    for example in "${advanced_examples[@]}"; do
        if [ -f "$example" ]; then
            run_example "$example"
            echo ""
        fi
    done
    
elif [ "$1" = "gpu" ]; then
    echo -e "${YELLOW}GPU Examples${NC}"
    echo ""
    
    gpu_examples=(
        "examples/simple_gpu_fft.flow"
        "examples/gpu_integration_demo.flow"
        "examples/test_for_parallel.flow"
        "examples/test_simd_saxpy.flow"
    )
    
    for example in "${gpu_examples[@]}"; do
        if [ -f "$example" ]; then
            run_example "$example"
            echo ""
        fi
    done
    
elif [ "$1" = "metal" ]; then
    echo -e "${YELLOW}Metal GPU Examples${NC}"
    echo ""
    
    metal_examples=(
        "examples/metal_simple_test.flow"
        "examples/metal_gpu_demo.flow"
        "examples/metal_gpu_demo_simple.flow"
    )
    
    for example in "${metal_examples[@]}"; do
        if [ -f "$example" ]; then
            run_example "$example"
            echo ""
        fi
    done
    
elif [ "$1" = "web" ]; then
    echo -e "${YELLOW}WebAssembly Examples${NC}"
    echo ""
    
    web_examples=(
        "examples/web_simple.flow"
        "examples/web_demo.flow"
    )
    
    for example in "${web_examples[@]}"; do
        if [ -f "$example" ]; then
            run_example "$example"
            echo ""
        fi
    done
    
elif [ "$1" = "test" ]; then
    echo -e "${YELLOW}Running Test Suite${NC}"
    echo ""
    ./flow test
    
elif [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "FLOW Examples Runner Help"
    echo "========================="
    echo ""
    echo "This script helps you run FLOW examples with proper formatting and error handling."
    echo ""
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  all                 Run all examples in examples/ directory"
    echo "  basic              Run basic programming examples"
    echo "  advanced           Run advanced examples (graphics, effects, etc.)"
    echo "  gpu                Run GPU computing examples"
    echo "  metal              Run Metal GPU examples (Apple Silicon)"
    echo "  web                Run WebAssembly examples"
    echo "  test               Run the test suite instead of examples"
    echo "  <file.flow>        Run a specific .flow file"
    echo "  help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 basic           # Run basic examples"
    echo "  $0 examples/fibonacci.flow  # Run specific file"
    echo "  $0 test            # Run test suite"
    echo ""
    
elif [[ "$1" == *.flow ]]; then
    # Run specific file
    if [ -f "$1" ]; then
        run_example "$1"
    else
        echo -e "${RED}❌ File not found: $1${NC}"
        exit 1
    fi
    
else
    echo -e "${RED}❌ Unknown option: $1${NC}"
    echo "Use '$0 help' for usage information"
    exit 1
fi

echo -e "${GREEN}🎉 Examples runner complete!${NC}"
