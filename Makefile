# FLOW Programming Language Makefile
# Build and run FLOW programs

CC = clang
CXX = clang++
LLVM_PATH = /opt/homebrew/opt/llvm/bin
FLOWC = PYTHONPATH=./src python3 -m flow.transpiler
MLIR_OPT = $(LLVM_PATH)/mlir-opt
MLIR_TRANSLATE = $(LLVM_PATH)/mlir-translate
LLC = $(LLVM_PATH)/llc

# Default target
all: setup
	@echo "FLOW Programming Language Ready!"
	@echo "Usage:"
	@echo "  make run PROGRAM=example.flow    # Compile and run"
	@echo "  make compile PROGRAM=example.flow # Compile only"
	@echo "  make clean                       # Clean build files"

# Setup LLVM path
setup:
	@export PATH="$(LLVM_PATH):$$PATH"

# Compile and run FLOW program
run: compile
	@echo "Running $(PROGRAM)..."
	@./$(basename $(PROGRAM))

# Compile FLOW program to executable
compile:
	@echo "Compiling $(PROGRAM)..."
	@mkdir -p build
	@$(FLOWC) $(PROGRAM) -o build/$(basename $(PROGRAM)).mlir
	@echo "✅ FLOW → MLIR: build/$(basename $(PROGRAM)).mlir"
	@$(MLIR_OPT) build/$(basename $(PROGRAM)).mlir --convert-func-to-llvm --convert-arith-to-llvm --convert-cf-to-llvm -o build/$(basename $(PROGRAM)).llvm.mlir
	@echo "✅ MLIR → LLVM MLIR: build/$(basename $(PROGRAM)).llvm.mlir"
	@$(MLIR_TRANSLATE) build/$(basename $(PROGRAM)).llvm.mlir --mlir-to-llvmir -o build/$(basename $(PROGRAM)).ll
	@echo "✅ LLVM MLIR → LLVM IR: build/$(basename $(PROGRAM)).ll"
	@$(LLC) build/$(basename $(PROGRAM)).ll -filetype=obj -o build/$(basename $(PROGRAM)).o
	@echo "✅ LLVM IR → Object: build/$(basename $(PROGRAM)).o"
	@$(CC) build/$(basename $(PROGRAM)).o -o build/$(basename $(PROGRAM))
	@echo "✅ Object → Executable: build/$(basename $(PROGRAM))"
	@echo "🚀 Ready to run: ./build/$(basename $(PROGRAM))"

# Quick compile (just to MLIR)
mlir:
	@$(FLOWC) $(PROGRAM) -o build/$(basename $(PROGRAM)).mlir
	@echo "✅ Generated: build/$(basename $(PROGRAM)).mlir"

# Test with examples
test: setup
	@echo "Testing FLOW examples..."
	@make run PROGRAM=examples/minimal_turing.flow
	@echo ""
	@make run PROGRAM=tests/test_simple.flow
	@echo ""
	@make run PROGRAM=tests/test_control.flow

# Test standard library
test-stdlib: setup
	@echo "Testing FLOW standard library..."
	@echo "Testing math library..."
	@make run PROGRAM=tests/stdlib/test_math_lib.flow
	@echo ""
	@echo "Testing array library..."
	@make run PROGRAM=tests/stdlib/test_array_lib.flow
	@echo ""
	@echo "Testing memory library..."
	@make run PROGRAM=tests/stdlib/test_memory_lib.flow
	@echo ""
	@echo "Running memory benchmarks..."
	@make run PROGRAM=tests/stdlib/test_memory_benchmarks.flow
	@echo ""
	@echo "Running advanced memory tests..."
	@make run PROGRAM=tests/stdlib/test_memory_advanced.flow

# Test all components
test-all: test test-stdlib
	@echo "All tests completed!"

# Interactive mode
repl:
	@echo "FLOW REPL (type 'exit' to quit)"
	@while true; do \
		read -p "flow> " line; \
		if [ "$$line" = "exit" ]; then break; fi; \
		echo "$$line" > temp.flow; \
		echo "function main() -> i32 { $$line return 0 }" >> temp.flow; \
		$(FLOWC) temp.flow 2>/dev/null && echo "✅ Valid FLOW syntax" || echo "❌ Invalid syntax"; \
		rm -f temp.flow; \
	done

# Install dependencies
install:
	@echo "Installing FLOW dependencies..."
	@brew install llvm
	@echo "✅ LLVM installed"
	@pip3 install --user dataclasses 2>/dev/null || true
	@echo "✅ Python dependencies ready"

# Clean build files
clean:
	@rm -rf build/
	@rm -f *.o *.ll *.mlir
	@echo "✅ Cleaned build files"

# Show help
help:
	@echo "FLOW Programming Language"
	@echo ""
	@echo "Targets:"
	@echo "  compile PROGRAM=file.flow  - Compile to executable"
	@echo "  run PROGRAM=file.flow      - Compile and run"
	@echo "  mlir PROGRAM=file.flow     - Compile to MLIR only"
	@echo "  test                       - Run basic tests"
	@echo "  test-stdlib                - Run standard library tests"
	@echo "  test-all                   - Run all tests"
	@echo "  repl                       - Interactive REPL"
	@echo "  install                    - Install dependencies"
	@echo "  clean                      - Clean build files"
	@echo "  help                       - Show this help"
	@echo ""
	@echo "Examples:"
	@echo "  make run PROGRAM=examples/minimal_turing.flow"
	@echo "  make compile PROGRAM=examples/fibonacci.flow"

.PHONY: all setup run compile mlir test test-stdlib test-all repl install clean help
