# FLOW Compiler Testing Guide

This guide explains the comprehensive testing infrastructure for the FLOW programming language compiler.

## Overview

The FLOW project uses a **dual-layered testing approach**:

1. **FLOW Language Tests** (existing): `.flow` files that validate compilation success
2. **Python Unit Tests** (new): Python tests that validate compiler internals and functionality

Both approaches are complementary and serve different purposes:

- **FLOW Tests**: Validate that the language works correctly from a user perspective
- **Python Tests**: Validate that the compiler implementation is robust and correct

## Test Structure

```
tests/
├── core/                    # Existing FLOW language tests
├── stdlib/                  # Standard library tests
├── gpu/                     # GPU-specific tests
├── experimental/            # Experimental feature tests
├── misc/                    # Miscellaneous tests
├── unit/                    # Python unit tests (NEW)
│   ├── test_parser.py       # Parser and lexer tests
│   ├── test_mlir_generator.py # MLIR generation tests
│   ├── test_c_generator.py  # C generation tests
│   ├── test_transpiler.py   # Transpiler pipeline tests
│   ├── test_mlir_jit.py     # JIT compilation tests
│   ├── test_module_resolver.py # Module resolution tests
│   ├── test_mlir_optimizer.py # MLIR optimization tests
│   └── test_lsp_server.py   # LSP server tests
├── integration/             # End-to-end tests (NEW)
│   └── test_compilation_pipeline.py # Full pipeline tests
├── fixtures/               # Test data and utilities (NEW)
└── conftest.py             # Shared test configuration (NEW)
```

## Running Tests

### FLOW Language Tests (existing workflow)

```bash
# Run all FLOW language tests
./flow test

# This runs all .flow files in tests/ and examples/
# Tests compilation success, not runtime behavior
```

### Python Unit Tests (new)

```bash
# Run Python unit tests only
./flow test-python

# Run specific test file
./flow test-python tests/unit/test_parser.py

# Run with coverage
./flow test-python --cov=flow --cov-report=html
```

### All Tests (combined)

```bash
# Run both FLOW and Python tests
./flow test-all
```

### Using pytest directly

```bash
# Run tests directly with pytest
pytest tests/unit/ -v

# Run with coverage
pytest tests/ --cov=flow --cov-report=html

# Run specific test categories
pytest tests/unit/test_parser.py::TestLexer::test_keyword_tokenization -v
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)

Unit tests focus on individual components of the compiler:

#### Parser Tests (`test_parser.py`)
- **Lexer Tests**: Tokenization, keyword recognition, operator handling
- **Expression Parsing**: Binary operations, function calls, precedence
- **Statement Parsing**: Function declarations, control flow, variable declarations
- **Error Handling**: Syntax errors, invalid tokens, recovery

#### MLIR Generator Tests (`test_mlir_generator.py`)
- **Type Conversion**: FLOW types to MLIR types
- **Expression Generation**: Arithmetic, logical operations, function calls
- **Function Generation**: Function signatures, return handling
- **Control Flow**: if statements, loops, branching
- **Struct Handling**: Type definitions, field access

#### Integration Tests (`test_compilation_pipeline.py`)
- **End-to-End Compilation**: FLOW → MLIR → Executable
- **Backend Selection**: MLIR vs C backends
- **Error Propagation**: Compilation errors through pipeline
- **Tool Integration**: MLIR tools, clang integration

### 2. Integration Tests (`tests/integration/`)

Integration tests validate the complete compilation pipeline:

- **Compilation Pipeline**: Full FLOW to MLIR/C/LLVM conversion
- **Real Programs**: Test with actual FLOW programs
- **Performance**: Large program compilation, memory usage
- **Tool Dependencies**: MLIR tools, clang availability

## Writing Tests

### Test Naming Conventions

```python
# Test classes should be descriptive
class TestLexer:
class TestMLIRGenerator:
class TestCompilationPipeline:

# Test methods should be specific and readable
def test_keyword_tokenization(self):
def test_binary_operation_generation(self):
def test_function_with_parameters(self):
def test_error_propagation(self):
```

### Test Structure

```python
import pytest
from flow.parser import Parser, Lexer
from tests.conftest import TestHelpers

class TestParser:
    def test_simple_function_parsing(self, parser):
        """Test parsing a simple function declaration."""
        code = """
        function add(a: i32, b: i32) -> i32 {
            return a + b
        }
        """
        
        ast = parser.parse(code)
        assert len(ast) == 1
        assert ast[0].name == "add"
        assert len(ast[0].parameters) == 2
    
    def test_error_handling(self, parser):
        """Test that syntax errors are properly reported."""
        with pytest.raises(Exception):
            parser.parse("function broken( -> i32 {")
```

### Using Fixtures

```python
def test_with_sample_code(self, sample_flow_code):
    """Use predefined test code snippets."""
    ast = parse_flow_code(sample_flow_code['simple_function'])
    # Test with known good code

def test_with_temp_file(self, temp_flow_file):
    """Create temporary files for testing."""
    code = "function main() -> i32 { return 42 }"
    file_path = temp_flow_file(code)
    result = TestHelpers.run_transpiler(file_path)
    assert result.returncode == 0
```

### Test Categories and Markers

```python
import pytest

@pytest.mark.unit  # Fast unit test
def test_lexer_tokenization(self):
    pass

@pytest.mark.integration  # Slower integration test
def test_compilation_pipeline(self):
    pass

@pytest.mark.slow  # Very slow test (runs JIT, etc.)
def test_jit_execution(self):
    pass

# Run specific categories
pytest tests/ -m unit
pytest tests/ -m "not slow"
```

## Test Data and Helpers

### Sample Code Snippets

Pre-defined test cases are available in `conftest.py`:

```python
def test_with_samples(self, sample_flow_code):
    # Available keys:
    # - 'simple_function'
    # - 'main_function' 
    # - 'struct_definition'
    # - 'control_flow'
    # - 'loop_example'
    # - 'array_operations'
    # - 'error_syntax'
    # - 'error_undefined'
    
    ast = parse_flow_code(sample_flow_code['control_flow'])
```

### Helper Functions

```python
# TestHelpers provides utility functions
def test_compilation_helpers(self, test_helpers):
    # Compile FLOW to MLIR
    mlir = test_helpers.compile_flow_to_mlir(flow_code)
    
    # Run transpiler with options
    result = test_helpers.run_transpiler(input_file, output_file, optimize=True)
    
    # Verify tokens
    tokens = test_helpers.tokenize_code(code)
    test_helpers.verify_token(tokens, 0, TokenType.FUNCTION)
```

## Best Practices

### 1. Test Organization

- **Group related tests** in descriptive classes
- **Use descriptive names** that explain what's being tested
- **Separate unit and integration tests** into different files
- **Use markers** to categorize test speed and type

### 2. Test Data Management

- **Use fixtures** for common test data
- **Create temporary files** for file-based tests
- **Clean up artifacts** after tests
- **Use parameterized tests** for multiple test cases

### 3. Error Testing

- **Test both success and failure** cases
- **Verify error messages** are informative
- **Test error propagation** through pipeline
- **Check graceful degradation** when tools are missing

### 4. Performance Considerations

- **Mark slow tests** with `@pytest.mark.slow`
- **Use mocks** for external dependencies when appropriate
- **Avoid expensive operations** in unit tests
- **Cache compilation results** where possible

## Example Test Cases

### Parser Example

```python
def test_complex_expression_parsing(self, parser):
    """Test parsing expressions with correct precedence."""
    code = """
    function test() -> i32 {
        let result: i32 = a + b * c / d - e % f + (g * h)
        return result
    }
    """
    
    ast = parser.parse(code)
    func = ast[0]
    var_decl = func.body.statements[0]
    expr = var_decl.initializer
    
    # Should parse as: ((((a + ((b * c) / d)) - (e % f)) + (g * h))
    assert isinstance(expr, BinaryOperation)
    assert expr.operator == "+"
```

### MLIR Generator Example

```python
def test_function_generation(self, mlir_generator):
    """Test MLIR function generation."""
    flow_code = """
    function add(a: i32, b: i32) -> i32 {
        return a + b
    }
    """
    
    ast = parse_flow_code(flow_code)
    mlir = mlir_generator.generate(ast)
    
    # Verify function signature
    assert "func.func @add(%arg0: i32, %arg1: i32) -> i32" in mlir
    assert "arith.addi %arg0, %arg1" in mlir
    assert "return %0 : i32" in mlir
```

### Integration Example

```python
def test_complete_compilation_pipeline(self, temp_flow_file):
    """Test complete compilation from FLOW to executable."""
    flow_code = """
    function fibonacci(n: i32) -> i32 {
        if n <= 1 {
            return n
        } else {
            return fibonacci(n - 1) + fibonacci(n - 2)
        }
    }
    
    function main() -> i32 {
        return fibonacci(10)
    }
    """
    
    input_file = temp_flow_file(flow_code)
    
    # Test MLIR generation
    result = TestHelpers.run_transpiler(input_file, mlir=True)
    assert result.returncode == 0
    
    # Test C generation
    result = TestHelpers.run_transpiler(input_file, c=True)
    assert result.returncode == 0
    
    # Verify both outputs exist and have content
    mlir_file = input_file.replace('.flow', '.mlir')
    c_file = input_file.replace('.flow', '.c')
    
    assert os.path.exists(mlir_file)
    assert os.path.exists(c_file)
    
    with open(mlir_file, 'r') as f:
        mlir_content = f.read()
        assert "func.func @fibonacci" in mlir_content
    
    with open(c_file, 'r') as f:
        c_content = f.read()
        assert "fibonacci" in c_content
```

## Debugging Tests

### Running Individual Tests

```bash
# Run specific test method
pytest tests/unit/test_parser.py::TestParser::test_simple_function_parsing -v

# Run with more detail
pytest tests/unit/test_parser.py -v -s --tb=long

# Stop on first failure
pytest tests/ -x

# Run with debugger
pytest tests/ --pdb
```

### Common Issues

1. **Import Errors**: Ensure `PYTHONPATH=./src` is set
2. **Missing Dependencies**: Install with `pip install -e .[test]`
3. **MLIR Tools Missing**: Run `./flow install` or install LLVM
4. **File Permissions**: Ensure build directory is writable

## Coverage

### Generating Coverage Reports

```bash
# Generate coverage report
pytest tests/ --cov=flow --cov-report=html

# Check coverage threshold
pytest tests/ --cov=flow --cov-fail-under=80

# View coverage in HTML
open htmlcov/index.html
```

### Coverage Goals

- **Parser**: 95%+ coverage (critical component)
- **MLIR Generator**: 90%+ coverage (complex code generation)
- **Transpiler**: 85%+ coverage (integration point)
- **Overall**: 80%+ coverage target

## Continuous Integration

The test suite is designed to run in CI/CD environments:

```bash
# Install dependencies
pip install -e .[test]

# Run fast tests first
pytest tests/unit/ -x -v

# Run integration tests
pytest tests/integration/ -v

# Generate coverage
pytest tests/ --cov=flow --cov-report=xml
```

## Contributing Tests

When adding new features:

1. **Write unit tests** for new components
2. **Add integration tests** for new functionality
3. **Update existing tests** if behavior changes
4. **Add test fixtures** for common test data
5. **Document testing approach** in this guide

## Future Enhancements

Planned testing improvements:

- **Property-based testing** with Hypothesis
- **Fuzz testing** for robustness
- **Performance regression tests**
- **Cross-platform compatibility tests**
- **Memory leak detection**
- **Static analysis integration**

This comprehensive testing infrastructure ensures the FLOW compiler remains reliable, maintainable, and ready for production use.