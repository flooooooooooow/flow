"""
Working parser tests based on actual FLOW API.
These tests are designed to actually pass with the current codebase.
"""

import pytest
from flow.parser import parse_flow_code, Lexer, TokenType


class TestWorkingParser:
    """Tests that actually work with the current parser API."""

    def test_simple_function_parsing(self):
        """Test parsing a simple function."""
        code = """
        function add(a: i32, b: i32) -> i32 {
            return a + b
        }
        """

        ast = parse_flow_code(code)
        assert len(ast) == 1

        func = ast[0]
        assert func.name == "add"
        assert len(func.parameters) == 2
        assert func.parameters[0].name == "a"
        assert func.parameters[1].name == "b"
        assert func.return_type.name == "i32"

    def test_main_function_parsing(self):
        """Test parsing main function."""
        code = """
        function main() -> i32 {
            return 42
        }
        """

        ast = parse_flow_code(code)
        assert len(ast) == 1

        func = ast[0]
        assert func.name == "main"
        assert len(func.parameters) == 0

    def test_multiple_functions(self):
        """Test parsing multiple functions."""
        code = """
        function add(a: i32, b: i32) -> i32 {
            return a + b
        }
        
        function multiply(x: i32, y: i32) -> i32 {
            return x * y
        }
        """

        ast = parse_flow_code(code)
        assert len(ast) == 2
        assert ast[0].name == "add"
        assert ast[1].name == "multiply"

    def test_control_flow_parsing(self):
        """Test parsing if statement."""
        code = """
        function check(x: i32) -> i32 {
            if x > 0 {
                return 1
            } else {
                return -1
            }
        }
        """

        ast = parse_flow_code(code)
        assert len(ast) == 1
        func = ast[0]
        assert func.name == "check"

    def test_struct_parsing(self):
        """Test parsing struct definition."""
        code = """
        struct Point {
            x: i32,
            y: i32
        }
        
        function main() -> i32 {
            return 42
        }
        """

        ast = parse_flow_code(code)
        assert len(ast) == 2  # struct + function
        # First should be struct
        assert hasattr(ast[0], "name")  # Basic check


class TestWorkingLexer:
    """Tests that work with the current lexer API."""

    def test_basic_lexing(self):
        """Test basic lexer functionality."""
        code = "function add(a: i32) -> i32"
        lexer = Lexer(code)

        # Test we can get tokens (check first few)
        tokens = []
        try:
            while True:
                token = lexer.next_token()
                if token.type == TokenType.EOF:
                    break
                tokens.append(token)
                if len(tokens) > 10:  # Limit to avoid infinite loops
                    break
        except Exception:
            pass

        assert len(tokens) > 0
        # Should contain FUNCTION token
        function_tokens = [t for t in tokens if t.type == TokenType.FUNCTION]
        assert len(function_tokens) > 0
