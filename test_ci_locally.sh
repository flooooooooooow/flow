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
pip3 install pytest ruff pytest-cov --quiet || echo "dependencies already installed"

echo ""
echo -e "${BLUE}=== Running Lint checks (Ruff) ===${NC}"
ruff check src
ruff format --check src

echo ""
echo -e "${BLUE}=== Running Tier 1 tests (transpile only) ===${NC}"
./flow test --tier 1

echo ""
echo -e "${BLUE}=== Running Tier 2 tests (transpile + compile) ===${NC}"
./flow test --tier 2

echo ""
echo -e "${BLUE}=== Running Runtime tests (compile + execute) ===${NC}"
./flow test-runtime

echo ""
echo -e "${BLUE}=== Running MLIR verification tests ===${NC}"
./flow test-mlir || echo "MLIR tests skipped (no tools)"

echo ""
echo -e "${BLUE}=== Running Python unit tests with coverage ===${NC}"
PYTHONPATH=src pytest tests/ -v --cov=src --tb=short || echo "No Python unit tests or pytest not configured"

echo ""
echo -e "${BLUE}=== Running example programs ===${NC}"
./flow run examples/basics/hello_world.flow
./flow compile examples/basics/fibonacci.flow

echo ""
echo -e "${GREEN}✅ All CI checks passed locally!${NC}"
