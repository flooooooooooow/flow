"""
Shared fixtures and utilities for FLOW compiler tests.
This module provides common test data, fixtures, and helper functions
for testing the FLOW language compiler components.
"""

import sys
import tempfile
import subprocess
import atexit
import os
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports (same as flow script)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from flow.parser import parse_flow_code, Lexer, Parser, Token, TokenType
from flow.mlir_generator import MLIRGenerator


_TEMP_FILES: list[str] = []


def _cleanup_temp_files():
    for path in list(_TEMP_FILES):
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass


atexit.register(_cleanup_temp_files)


@pytest.fixture
def sample_flow_code():
    """Provide sample FLOW code snippets for testing."""
    return {
        "simple_function": """
function add(a: i32, b: i32) -> i32 {
    return a + b
}
        """.strip(),
        "main_function": """
function main() -> i32 {
    return 42
}
        """.strip(),
        "struct_definition": """
struct Point {
    x: i32,
    y: i32
}

function main() -> i32 {
    let p: Point = Point{x: 10, y: 20}
    return p.x + p.y
}
        """.strip(),
        "control_flow": """
function factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}

function main() -> i32 {
    return factorial(5)
}
        """.strip(),
        "loop_example": """
function sum_range(start: i32, end: i32) -> i32 {
    let sum: i32 = 0
    let i: i32 = start
    
    while i <= end {
        sum = sum + i
        i = i + 1
    }
    
    return sum
}

function main() -> i32 {
    return sum_range(1, 10)
}
        """.strip(),
        "array_operations": """
function sum_array(arr: [i32, 5]) -> i32 {
    let sum: i32 = 0
    let i: i32 = 0
    
    while i < 5 {
        sum = sum + arr[i]
        i = i + 1
    }
    
    return sum
}

function main() -> i32 {
    let numbers: [i32, 5] = [i32, 5]{1, 2, 3, 4, 5}
    return sum_array(numbers)
}
        """.strip(),
        "error_syntax": """
function broken( -> i32 {
    return 42
}
        """.strip(),
        "error_undefined": """
function main() -> i32 {
    return undefined_var + 1
}
        """.strip(),
    }


@pytest.fixture
def temp_flow_file():
    """Create temporary .flow files for testing."""

    def _create_file(content: str, suffix: str = ".flow") -> str:
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(content)
            _TEMP_FILES.append(f.name)
            return f.name

    return _create_file


@pytest.fixture
def parser():
    """Provide a parser factory for testing.
    
    Usage:
        ast = parser.parse("function main() -> i32 { return 0 }")
    """
    class ParserFactory:
        def parse(self, code: str):
            """Parse FLOW code and return AST."""
            return parse_flow_code(code)
    
    return ParserFactory()


@pytest.fixture
def lexer():
    """Provide a lexer factory for testing.
    
    Usage:
        tokens = lexer.tokenize("let x: i32 = 42")
        # or
        lexer_instance = lexer("let x: i32 = 42")
        tokens = lexer_instance.tokenize()
    """
    class LexerFactory:
        def __call__(self, text: str) -> Lexer:
            return Lexer(text)
        
        def tokenize(self, text: str) -> list:
            return Lexer(text).tokenize()
    
    return LexerFactory()


@pytest.fixture
def mlir_generator():
    """Provide an MLIR generator instance for testing."""
    return MLIRGenerator()


class TestHelpers:
    """Helper functions for testing."""

    @staticmethod
    def compile_flow_to_mlir(flow_code: str, source_file: str = "test.flow") -> str:
        """Compile FLOW code to MLIR using the existing pipeline."""
        try:
            ast = parse_flow_code(flow_code)
            generator = MLIRGenerator(source_file)
            return generator.generate_module(ast)
        except Exception as e:
            raise RuntimeError(f"Failed to compile FLOW to MLIR: {e}")

    @staticmethod
    def tokenize_code(code: str) -> list[Token]:
        """Tokenize FLOW code using the lexer."""
        lexer = Lexer(code)
        return lexer.tokenize()

    @staticmethod
    def parse_code(code: str):
        """Parse FLOW code into an AST."""
        return parse_flow_code(code)

    @staticmethod
    def create_temp_file(content: str, suffix: str = ".flow") -> str:
        """Create a temporary file with the given content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(content)
            _TEMP_FILES.append(f.name)
            return f.name

    @staticmethod
    def run_transpiler(
        input_file: str, output_file: str = None, **kwargs
    ) -> subprocess.CompletedProcess:
        """Run the FLOW transpiler on a file."""
        cmd = ["python3", "-m", "flow.transpiler", input_file]

        if output_file:
            cmd.extend(["-o", output_file])

        # Add any additional arguments
        for key, value in kwargs.items():
            if value is True:
                cmd.append(f"--{key.replace('_', '-')}")
            elif value:
                cmd.extend([f"--{key.replace('_', '-')}", str(value)])

        return subprocess.run(
            cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )

    @staticmethod
    def verify_token(
        tokens: list[Token],
        index: int,
        expected_type: TokenType,
        expected_value: str = None,
    ):
        """Verify a token at a specific index."""
        assert index < len(tokens), f"Token index {index} out of range"
        token = tokens[index]
        assert token.type == expected_type, (
            f"Expected token type {expected_type}, got {token.type}"
        )
        if expected_value is not None:
            assert token.value == expected_value, (
                f"Expected token value '{expected_value}', got '{token.value}'"
            )


@pytest.fixture
def test_helpers():
    """Provide test helper functions."""
    return TestHelpers()


# Test data for edge cases and error conditions
# Note: FLOW uses # for comments (not // or /* */)
EDGE_CASES = {
    "empty_string": "",
    "whitespace_only": "   \n\t   ",
    "only_comments": "# This is a comment\n# Another comment",
    "string_with_escapes": 'let s: string = "hello\\nworld\\t!"',
    "numeric_literals": "let a: i32 = 42\nlet b: i32 = -17\nlet c: bool = true\nlet d: bool = false",
    "complex_expressions": "result = a + b * c / d - e % f + (g * h)",
    "nested_calls": "outer(inner1(inner2(x), y), inner3(z))",
    "deeply_nested_struct": "let val: DeepType = outer.middle.inner.value",
}

ERROR_CASES = {
    "unclosed_string": 'let s: string = "unclosed',
    "invalid_escape": 'let s: string = "invalid\\x"',
    "mismatched_brackets": "result = [1, 2, 3",
    "invalid_syntax": "function broken( -> i32 {",
    "unknown_keyword": "unknown_keyword value",
    "invalid_type": "let x: invalid_type = 42",
}

# Expected MLIR patterns for validation
MLIR_PATTERNS = {
    "function_signature": r"func\.func @\w+\(",
    "arith_addi": r"%\d+ = arith\.addi %\d+, %\d+",
    "arith_muli": r"%\d+ = arith\.muli %\d+, %\d+",
    "return": r"return %\d+ : i32",
    "struct_type": r"llvm\.struct<.*>",
    "constant_int": r"llvm\.mlir\.constant\(\d+ : i32\)",
    "constant_zero": r"llvm\.mlir\.constant\(0 : i32\)",
}
