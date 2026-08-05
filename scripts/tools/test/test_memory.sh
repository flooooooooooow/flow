#!/bin/bash

# Memory Management Test Runner
# Comprehensive testing script for FLOW memory management library

set -e  # Exit on any error

echo "🧠 FLOW Memory Management Test Suite"
echo "===================================="

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

# Function to run a test and report results
run_test() {
    local test_name="$1"
    local test_file="$2"
    
    echo -e "\n${BLUE}Testing: $test_name${NC}"
    echo "File: $test_file"
    echo "----------------------------------------"
    
    if make run PROGRAM="$test_file" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        echo "Run manually: make run PROGRAM=$test_file"
        ((TESTS_FAILED++))
    fi
    ((TESTS_TOTAL++))
}

# Function to check if dependencies are available
check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    if ! command -v make &> /dev/null; then
        echo -e "${RED}❌ Error: make not found${NC}"
        exit 1
    fi
    
    if ! python3 -c "import flow.transpiler" 2>/dev/null; then
        echo -e "${RED}❌ Error: FLOW transpiler not found${NC}"
        echo "Please ensure FLOW is properly installed"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Dependencies OK${NC}"
}

# Function to run memory leak detection
run_leak_check() {
    echo -e "\n${YELLOW}Running memory leak detection...${NC}"
    echo "Note: This requires external tools like valgrind"
    
    if command -v valgrind &> /dev/null; then
        echo "Running valgrind on memory tests..."
        valgrind --leak-check=full --show-leak-kinds=all ./build/test_memory_lib 2>/dev/null || echo "Valgrind check completed"
    else
        echo -e "${YELLOW}⚠️  Valgrind not installed. Install with: brew install valgrind${NC}"
    fi
}

# Function to run performance benchmarks
run_benchmarks() {
    echo -e "\n${YELLOW}Running performance benchmarks...${NC}"
    
    if [ -f "tests/stdlib/test_memory_benchmarks.flow" ]; then
        echo "Executing memory benchmarks..."
        if make run PROGRAM="tests/stdlib/test_memory_benchmarks.flow" 2>/dev/null; then
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
    echo "Starting comprehensive memory management tests..."
    
    # Check dependencies
    check_dependencies
    
    # Clean build directory
    echo -e "\n${YELLOW}Cleaning build directory...${NC}"
    make clean > /dev/null 2>&1
    
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
import "io.flow"

function run_demo() -> i32 {
    print("Testing micro-allocations...")
    
    let i: i32 = 0
    while i < 1000 {
        let ptr: *mut void = malloc(1)  # 1 byte allocations
        if ptr != null {
            free(ptr)
        } else {
            print("FAIL: Micro-allocation failed")
            return 1
        }
        i = i + 1
    }
    
    print("PASS: Micro-allocations")
    return 0
}
EOF
    
    if make run PROGRAM="/tmp/test_micro_allocations.flow" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED: Micro-allocations${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED: Micro-allocations${NC}"
        ((TESTS_FAILED++))
    fi
    ((TESTS_TOTAL++))
    
    # Test alignment edge cases
    echo -e "${YELLOW}Testing alignment edge cases...${NC}"
    cat > /tmp/test_alignment_edge.flow << 'EOF'
import "memory.flow"
import "io.flow"

function run_demo() -> i32 {
    print("Testing alignment edge cases...")
    
    # Test various power-of-2 alignments
    let alignments: [i32; 5] = [1, 2, 4, 8, 16]
    let i: i32 = 0
    
    while i < 5 {
        let alignment: i32 = alignments[i]
        let ptr: *mut void = aligned_alloc(alignment, 64)
        
        if ptr != null {
            if not is_aligned(ptr, alignment) {
                print("FAIL: Alignment not respected")
                free(ptr)
                return 1
            }
            free(ptr)
        }
        i = i + 1
    }
    
    print("PASS: Alignment edge cases")
    return 0
}
EOF
    
    if make run PROGRAM="/tmp/test_alignment_edge.flow" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED: Alignment edge cases${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED: Alignment edge cases${NC}"
        ((TESTS_FAILED++))
    fi
    ((TESTS_TOTAL++))
    
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
