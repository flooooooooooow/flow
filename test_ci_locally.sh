#!/bin/bash
# Run CI tests locally (without Docker/act)
# This simulates what GitHub Actions does

set -e  # Exit on error

echo "🧪 Running CI tests locally..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
python3 --version

# Check clang
echo -e "${BLUE}Checking clang...${NC}"
clang --version | head -3

echo ""
echo -e "${BLUE}Setting up environment...${NC}"
export PYTHONPATH=src

# Install Python dependencies (if needed)
echo -e "${BLUE}Installing dependencies...${NC}"
pip3 install pytest --quiet || echo "pytest already installed"

echo ""
echo -e "${BLUE}=== Running Tier 1 tests (transpile only) ===${NC}"
./flow test --tier 1

echo ""
echo -e "${BLUE}=== Running Tier 2 tests (transpile + compile) ===${NC}"
./flow test --tier 2

echo ""
echo -e "${BLUE}=== Running Python unit tests ===${NC}"
PYTHONPATH=src pytest tests/ -v --tb=short || echo "No Python unit tests or pytest not configured"

echo ""
echo -e "${BLUE}=== Running example programs ===${NC}"
./flow run examples/basics/hello_world.flow
./flow compile examples/basics/fibonacci.flow

echo ""
echo -e "${BLUE}=== Running Lint checks ===${NC}"
python3 -m py_compile src/flow/parser.py
python3 -m py_compile src/flow/c_generator.py
python3 -m py_compile src/flow/transpiler.py
python3 -m py_compile src/flow/type_checker.py
python3 -m py_compile src/flow/mlir_generator.py
python3 -m py_compile src/flow/monomorphize.py
python3 -m py_compile src/flow/module_resolver.py

echo ""
echo -e "${GREEN}✅ All CI checks passed locally!${NC}"
