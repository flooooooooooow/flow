#!/bin/bash

# Memory Management Test Runner
# Exercises lib/stdlib/memory.flow (malloc/free + alignment helpers + the
# C11 aligned_alloc extern) through the C backend — the same `flow run`
# pipeline the CI tier-2 corpus uses (FLOW_HOST=python).
#
# Wired into CI: runs as an extra step of the `flow-tier2` job in
# .github/workflows/ci.yml, and from scripts/test_ci_locally.sh.

set -e  # Exit on any error

# Resolve the repo root regardless of this script's depth (tools/test/ or
# scripts/tools/test/), then run from there so `./flow` and stdlib imports
# resolve the same way they do in CI.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
while [ ! -x "$PROJECT_ROOT/flow" ] && [ "$PROJECT_ROOT" != "/" ]; do
    PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
done
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Run a .flow file through the same C-backend pipeline CI uses.
run_program() {
    FLOW_HOST=python "$PROJECT_ROOT/flow" run "$1"
}

# Function to run a test and report results
run_test() {
    local test_name="$1"
    local test_file="$2"

    echo -e "\n${BLUE}Testing: $test_name${NC}"
    echo "File: $test_file"
    echo "----------------------------------------"

    if run_program "$test_file" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        echo "Run manually: FLOW_HOST=python ./flow run $test_file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
}

# Function to check if dependencies are available
check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"

    if [ ! -x "$PROJECT_ROOT/flow" ]; then
        echo -e "${RED}❌ Error: ./flow launcher not found at $PROJECT_ROOT/flow${NC}"
        exit 1
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "${RED}❌ Error: python3 not found${NC}"
        exit 1
    fi

    if ! command -v clang >/dev/null 2>&1 && ! command -v cc >/dev/null 2>&1; then
        echo -e "${RED}❌ Error: clang or cc not found${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Dependencies OK${NC}"
}

# Function to run memory leak detection
run_leak_check() {
    echo -e "\n${YELLOW}Running memory leak detection...${NC}"
    echo "Note: This requires external tools like valgrind"

    if command -v valgrind >/dev/null 2>&1 && [ -f "$PROJECT_ROOT/build/test_memory_lib" ]; then
        echo "Running valgrind on memory tests..."
        valgrind --leak-check=full --show-leak-kinds=all "$PROJECT_ROOT/build/test_memory_lib" 2>/dev/null || echo "Valgrind check completed"
    else
        echo -e "${YELLOW}⚠️  Valgrind not installed (or binary not built). Install with: brew install valgrind${NC}"
    fi
}

# Function to run performance benchmarks
run_benchmarks() {
    echo -e "\n${YELLOW}Running performance benchmarks...${NC}"

    if [ -f "tests/stdlib/test_memory_benchmarks.flow" ]; then
        echo "Executing memory benchmarks..."
        if run_program "tests/stdlib/test_memory_benchmarks.flow" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Benchmarks completed${NC}"
        else
            echo -e "${RED}❌ Benchmarks failed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Benchmark file not found${NC}"
    fi
}

# Main test execution
main() {
    echo "🧠 FLOW Memory Management Test Suite"
    echo "===================================="
    echo "Starting comprehensive memory management tests..."

    # Check dependencies
    check_dependencies

    # Run basic memory library tests
    echo -e "\n${BLUE}=== Basic Memory Library Tests ===${NC}"
    run_test "Memory Library Core" "tests/stdlib/test_memory_lib.flow"

    # Run advanced memory tests
    echo -e "\n${BLUE}=== Advanced Memory Tests ===${NC}"
    run_test "Memory Advanced Tests" "tests/stdlib/test_memory_advanced.flow"

    # Run benchmarks
    run_benchmarks

    # Test edge cases with different scenarios
    echo -e "\n${BLUE}=== Edge Case Tests ===${NC}"

    # Test with very small allocations
    echo -e "${YELLOW}Testing micro-allocations...${NC}"
    cat > /tmp/test_micro_allocations.flow << 'EOF'
import "memory.flow"

function main() -> i32 {
    let mut i: i32 = 0
    while i < 1000 {
        let ptr: ptr<void> = malloc(1)
        if ptr == null {
            println("FAIL: Micro-allocation failed")
            return 1
        }
        free(ptr)
        i = i + 1
    }
    println("PASS: Micro-allocations")
    return 0
}
EOF

    if run_program /tmp/test_micro_allocations.flow > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED: Micro-allocations${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAILED: Micro-allocations${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    # Test alignment edge cases (via the C11 aligned_alloc extern + the
    # is_aligned helper now in lib/stdlib/memory.flow). Alignments must be
    # >= sizeof(void*) on every libc (macOS aligned_alloc rejects smaller
    # ones) and the size must be a multiple of each alignment.
    echo -e "${YELLOW}Testing alignment edge cases...${NC}"
    cat > /tmp/test_alignment_edge.flow << 'EOF'
import "memory.flow"

function main() -> i32 {
    let alignments: array<i64, 4> = [8, 16, 32, 64]
    let mut i: i64 = 0
    while i < 4 {
        let alignment: i64 = alignments[i]
        let ptr: ptr<void> = aligned_alloc(alignment, 64)
        if ptr == null {
            println("FAIL: aligned_alloc returned null")
            return 1
        }
        if !is_aligned(ptr, alignment) {
            println("FAIL: Alignment not respected")
            free(ptr)
            return 1
        }
        free(ptr)
        i = i + 1
    }
    println("PASS: Alignment edge cases")
    return 0
}
EOF

    if run_program /tmp/test_alignment_edge.flow > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED: Alignment edge cases${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAILED: Alignment edge cases${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    # Run leak detection if available
    run_leak_check

    # Clean up temporary files
    rm -f /tmp/test_micro_allocations.flow /tmp/test_alignment_edge.flow

    # Final report
    echo -e "\n${BLUE}====================================${NC}"
    echo -e "${BLUE}FINAL TEST RESULTS${NC}"
    echo -e "${BLUE}====================================${NC}"
    echo -e "Total Tests: $TESTS_TOTAL"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}🎉 ALL TESTS PASSED! 🎉${NC}"
        echo -e "${GREEN}Memory management library is working correctly!${NC}"
        exit 0
    else
        echo -e "\n${RED}❌ SOME TESTS FAILED ❌${NC}"
        echo -e "${RED}Please check the failed tests and fix issues${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
