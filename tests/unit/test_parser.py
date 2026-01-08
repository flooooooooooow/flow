"""
Tests for the FLOW language parser.
This module tests the lexer, parser, and AST generation functionality.
"""

import pytest
from flow.parser import (
    Lexer,
    Parser,
    Token,
    TokenType,
    parse_flow_code,
    FunctionDecl,
    VarDecl,
    Type,
    Literal,
    Variable,
    BinaryOperation,
    UnaryOperation,
    FunctionCall,
    ReturnStatement,
    Block,
    Assignment,
    IfStatement,
    WhileStatement,
    ForStatement,
    Parameter,
)
from tests.conftest import EDGE_CASES, ERROR_CASES, TestHelpers


class TestLexer:
    """Test the FLOW lexer functionality."""

    def test_keyword_tokenization(self):
        """Test that keywords are properly tokenized."""
        code = "function let return if else while for import export struct"
        from flow.parser import Lexer

        lexer = Lexer(code)
        tokens = lexer.tokenize()

        expected_keywords = [
            TokenType.FUNCTION,
            TokenType.LET,
            TokenType.RETURN,
            TokenType.IF,
            TokenType.ELSE,
            TokenType.WHILE,
            TokenType.FOR,
            TokenType.IMPORT,
            TokenType.EXPORT,
            TokenType.STRUCT,
        ]

        for i, expected_type in enumerate(expected_keywords):
            assert tokens[i].type == expected_type

    def test_type_tokenization(self):
        """Test that type keywords are properly tokenized."""
        code = "i8 i16 i32 i64 bool string"
        from flow.parser import Lexer

        lexer = Lexer(code)
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.I8,
            TokenType.I16,
            TokenType.I32,
            TokenType.I64,
            TokenType.BOOLEAN,  # string is handled as identifier
        ]

        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type

    def test_identifier_tokenization(self, lexer):
        """Test identifier tokenization."""
        code = "variable_name function123 _private_var"
        tokens = lexer.tokenize(code)

        assert len(tokens) == 3
        for token in tokens:
            assert token.type == TokenType.IDENTIFIER
            assert token.value.startswith(("variable", "function", "_private"))

    def test_numeric_literals(self, lexer):
        """Test numeric literal tokenization."""
        code = "42 -17 0 123456"
        tokens = lexer.tokenize(code)

        assert len(tokens) == 4
        for token in tokens:
            assert token.type == TokenType.NUMBER
        assert tokens[0].value == "42"
        assert tokens[1].value == "-17"

    def test_boolean_literals(self, lexer):
        """Test boolean literal tokenization."""
        code = "true false"
        tokens = lexer.tokenize(code)

        assert len(tokens) == 2
        assert tokens[0].type == TokenType.BOOLEAN
        assert tokens[0].value == "true"
        assert tokens[1].type == TokenType.BOOLEAN
        assert tokens[1].value == "false"

    def test_operator_tokenization(self, lexer):
        """Test operator tokenization."""
        code = "+ - * / % == != < > <= >= && || ! = -> , . [ ] { } ( ) ; :"
        tokens = lexer.tokenize(code)

        # Check that all tokens were tokenized (no errors)
        assert len(tokens) > 20
        for token in tokens:
            assert token.type != TokenType.EOF

    def test_string_literals(self, lexer):
        """Test string literal tokenization."""
        code = '"hello world" "test\\nescapes" "simple"'
        tokens = lexer.tokenize(code)

        assert len(tokens) == 3
        for token in tokens:
            assert token.type == TokenType.STRING
        assert tokens[0].value == "hello world"
        assert tokens[1].value == "test\nescapes"

    def test_comments_and_whitespace(self, lexer):
        """Test that comments and whitespace are properly handled."""
        code = """
        // This is a comment
        function test() -> i32 {  // Another comment
            /* multiline comment */
            return 42
        }
        """
        tokens = lexer.tokenize(code)

        # Should have: FUNCTION, IDENTIFIER, (, ), ->, i32, {, RETURN, NUMBER, }, EOF
        assert len(tokens) >= 10
        function_token = next(t for t in tokens if t.type == TokenType.FUNCTION)
        assert function_token.type == TokenType.FUNCTION

    def test_edge_cases(self, lexer):
        """Test edge cases for the lexer."""
        # Empty string
        tokens = lexer.tokenize("")
        assert len(tokens) == 1  # Only EOF

        # Whitespace only
        tokens = lexer.tokenize("   \n\t   ")
        assert len(tokens) == 1  # Only EOF

        # Only comments
        tokens = lexer.tokenize("// Comment\n// Another comment")
        assert len(tokens) == 1  # Only EOF


class TestParser:
    """Test the FLOW parser functionality."""

    def test_empty_program(self, parser):
        """Test parsing an empty program."""
        ast = parser.parse("")
        assert ast == []

    def test_simple_function_declaration(self, parser):
        """Test parsing a simple function declaration."""
        code = """
        function add(a: i32, b: i32) -> i32 {
            return a + b
        }
        """
        ast = parser.parse(code)
        assert len(ast) == 1

        func = ast[0]
        assert isinstance(func, FunctionDecl)
        assert func.name == "add"
        assert len(func.parameters) == 2
        assert func.parameters[0].name == "a"
        assert func.parameters[0].type.name == "i32"
        assert func.parameters[1].name == "b"
        assert func.return_type.name == "i32"
        assert isinstance(func.body, Block)
        assert len(func.body.statements) == 1

    def test_main_function(self, parser):
        """Test parsing a main function."""
        code = "function main() -> i32 { return 42 }"
        ast = parser.parse(code)
        assert len(ast) == 1

        func = ast[0]
        assert isinstance(func, FunctionDecl)
        assert func.name == "main"
        assert len(func.parameters) == 0
        assert func.return_type.name == "i32"

    def test_variable_declarations(self, parser):
        """Test parsing variable declarations."""
        code = """
        function test() -> i32 {
            let x: i32 = 42
            let y: bool = true
            let z: i32
            return x
        }
        """
        ast = parser.parse(code)
        func = ast[0]

        # Should have 3 variable declarations + return
        assert len(func.body.statements) == 4

        # Test first declaration with initialization
        var1 = func.body.statements[0]
        assert isinstance(var1, VarDecl)
        assert var1.name == "x"
        assert var1.type.name == "i32"
        assert isinstance(var1.initializer, Literal)
        assert var1.initializer.value == "42"

        # Test second declaration with boolean
        var2 = func.body.statements[1]
        assert var2.name == "y"
        assert var2.type.name == "bool"
        assert isinstance(var2.initializer, Literal)
        assert var2.initializer.value == "true"

    def test_assignment_statements(self, parser):
        """Test parsing assignment statements."""
        code = """
        function test() -> i32 {
            let x: i32 = 0
            x = 42
            x = x + 1
            return x
        }
        """
        ast = parser.parse(code)
        func = ast[0]

        # Should have: var decl, assignment, assignment, return
        assert len(func.body.statements) == 4

        # Test simple assignment
        assign1 = func.body.statements[1]
        assert isinstance(assign1, Assignment)
        assert assign1.target == "x"
        assert isinstance(assign1.value, Literal)
        assert assign1.value.value == "42"

        # Test assignment with expression
        assign2 = func.body.statements[2]
        assert isinstance(assign2, Assignment)
        assert assign2.target == "x"
        assert isinstance(assign2.value, BinaryOperation)

    def test_binary_operations(self, parser):
        """Test parsing binary operations with correct precedence."""
        test_cases = [
            ("a + b", "+"),
            ("a - b", "-"),
            ("a * b", "*"),
            ("a / b", "/"),
            ("a % b", "%"),
            ("a == b", "=="),
            ("a != b", "!="),
            ("a < b", "<"),
            ("a > b", ">"),
            ("a <= b", "<="),
            ("a >= b", ">="),
            ("a && b", "&&"),
            ("a || b", "||"),
        ]

        for expr, expected_op in test_cases:
            code = f"function test() -> i32 {{ let x: i32 = {expr} return x }}"
            ast = parser.parse(code)
            func = ast[0]
            var_decl = func.body.statements[0]

            assert isinstance(var_decl, VarDecl)
            assert isinstance(var_decl.initializer, BinaryOperation)
            assert var_decl.initializer.operator == expected_op

    def test_operator_precedence(self, parser):
        """Test that operator precedence is correctly handled."""
        code = """
        function test() -> i32 {
            let result: i32 = a + b * c / d - e
            return result
        }
        """
        ast = parser.parse(code)
        func = ast[0]
        var_decl = func.body.statements[0]
        expr = var_decl.initializer

        # Should parse as: ((a + ((b * c) / d)) - e)
        assert isinstance(expr, BinaryOperation)
        assert expr.operator == "-"

        # Right side should be 'e'
        assert isinstance(expr.right, Variable)
        assert expr.right.name == "e"

        # Left side should be (a + ((b * c) / d))
        left = expr.left
        assert isinstance(left, BinaryOperation)
        assert left.operator == "+"

        # Right side of left should be ((b * c) / d)
        right_left = left.right
        assert isinstance(right_left, BinaryOperation)
        assert right_left.operator == "/"

    def test_unary_operations(self, parser):
        """Test parsing unary operations."""
        test_cases = [
            ("-x", "-"),
            ("!x", "!"),
        ]

        for expr, expected_op in test_cases:
            code = f"function test() -> i32 {{ let x: i32 = {expr} return x }}"
            ast = parser.parse(code)
            func = ast[0]
            var_decl = func.body.statements[0]

            assert isinstance(var_decl, VarDecl)
            assert isinstance(var_decl.initializer, UnaryOperation)
            assert var_decl.initializer.operator == expected_op

    def test_function_calls(self, parser):
        """Test parsing function calls."""
        code = """
        function test() -> i32 {
            let result: i32 = add(10, 20)
            let empty: i32 = no_args()
            return result
        }
        """
        ast = parser.parse(code)
        func = ast[0]

        # Test function call with arguments
        var1 = func.body.statements[0]
        assert isinstance(var1, VarDecl)
        assert isinstance(var1.initializer, FunctionCall)
        assert var1.initializer.name == "add"
        assert len(var1.initializer.arguments) == 2

        # Test function call without arguments
        var2 = func.body.statements[1]
        assert isinstance(var2, VarDecl)
        assert isinstance(var2.initializer, FunctionCall)
        assert var2.initializer.name == "no_args"
        assert len(var2.initializer.arguments) == 0

    def test_if_statements(self, parser):
        """Test parsing if statements."""
        code = """
        function test() -> i32 {
            if x > 0 {
                return 1
            } else {
                return -1
            }
        }
        """
        ast = parser.parse(code)
        func = ast[0]
        if_stmt = func.body.statements[0]

        assert isinstance(if_stmt, IfStatement)
        assert isinstance(if_stmt.condition, BinaryOperation)
        assert isinstance(if_stmt.then_block, Block)
        assert isinstance(if_stmt.else_block, Block)

    def test_while_loops(self, parser):
        """Test parsing while loops."""
        code = """
        function test() -> i32 {
            let i: i32 = 0
            while i < 10 {
                i = i + 1
            }
            return i
        }
        """
        ast = parser.parse(code)
        func = ast[0]
        while_stmt = func.body.statements[1]

        assert isinstance(while_stmt, WhileStatement)
        assert isinstance(while_stmt.condition, BinaryOperation)
        assert isinstance(while_stmt.body, Block)

    def test_for_loops(self, parser):
        """Test parsing for loops."""
        code = """
        function test() -> i32 {
            let sum: i32 = 0
            for i in range(0, 10) {
                sum = sum + i
            }
            return sum
        }
        """
        ast = parser.parse(code)
        func = ast[0]
        for_stmt = func.body.statements[1]

        assert isinstance(for_stmt, ForStatement)
        assert for_stmt.variable == "i"
        assert for_stmt.is_parallel == False

    def test_return_statements(self, parser):
        """Test parsing return statements."""
        test_cases = [
            "return 42",  # Return with value
            "return",  # Return without value
        ]

        for ret_code in test_cases:
            code = f"function test() -> i32 {{ {ret_code} }}"
            ast = parser.parse(code)
            func = ast[0]
            return_stmt = func.body.statements[0]

            assert isinstance(return_stmt, ReturnStatement)
            if ret_code == "return 42":
                assert isinstance(return_stmt.value, Literal)
                assert return_stmt.value.value == "42"
            else:
                assert return_stmt.value is None


class TestParserErrorHandling:
    """Test parser error handling and edge cases."""

    def test_unclosed_string_literal(self, parser):
        """Test handling of unclosed string literals."""
        with pytest.raises(Exception):
            parser.parse('let s: string = "unclosed')

    def test_invalid_syntax(self, parser):
        """Test handling of invalid syntax."""
        with pytest.raises(Exception):
            parser.parse("function broken( -> i32 {")

    def test_mismatched_brackets(self, parser):
        """Test handling of mismatched brackets."""
        with pytest.raises(Exception):
            parser.parse("let x: i32 = [1, 2, 3")

    def test_invalid_character(self, parser):
        """Test handling of invalid characters."""
        with pytest.raises(Exception):
            parser.parse("let x: i32 = @invalid")


class TestParserIntegration:
    """Integration tests for the parser."""

    def test_parse_flow_code_function(self):
        """Test the convenience parse_flow_code function."""
        code = """
        function add(a: i32, b: i32) -> i32 {
            return a + b
        }
        """

        ast = parse_flow_code(code)
        assert len(ast) == 1
        assert isinstance(ast[0], FunctionDecl)
        assert ast[0].name == "add"

    def test_complex_program(self, parser):
        """Test parsing a complex program with multiple features."""
        code = """
        function fibonacci(n: i32) -> i32 {
            if n <= 1 {
                return n
            } else {
                return fibonacci(n - 1) + fibonacci(n - 2)
            }
        }
        
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
            let fib: i32 = fibonacci(10)
            let sum: i32 = sum_range(1, 100)
            return fib + sum
        }
        """

        ast = parser.parse(code)
        assert len(ast) == 3

        # Check fibonacci function
        fib_func = ast[0]
        assert fib_func.name == "fibonacci"
        assert len(fib_func.parameters) == 1

        # Check sum_range function
        sum_func = ast[1]
        assert sum_func.name == "sum_range"
        assert len(sum_func.parameters) == 2

        # Check main function
        main_func = ast[2]
        assert main_func.name == "main"
        assert len(main_func.parameters) == 0


@pytest.mark.unit
class TestParserUnit:
    """Unit tests for parser components."""

    def test_type_parsing(self, parser):
        """Test type parsing."""
        code = "function test() -> i32 { let x: i32 = 42 return x }"
        ast = parser.parse(code)
        func = ast[0]
        var_decl = func.body.statements[0]

        assert var_decl.type.name == "i32"
        assert var_decl.type.is_pointer == False
        assert var_decl.type.size == None

    def test_parameter_parsing(self, parser):
        """Test parameter parsing."""
        code = "function test(a: i32, b: bool) -> i32 { return 0 }"
        ast = parser.parse(code)
        func = ast[0]

        assert len(func.parameters) == 2
        assert func.parameters[0].name == "a"
        assert func.parameters[0].type.name == "i32"
        assert func.parameters[1].name == "b"
        assert func.parameters[1].type.name == "bool"

    def test_nested_expressions(self, parser):
        """Test parsing deeply nested expressions."""
        code = """
        function test() -> i32 {
            let result: i32 = outer(inner1(inner2(x), y), inner3(z))
            return result
        }
        """
        ast = parser.parse(code)
        func = ast[0]
        var_decl = func.body.statements[0]

        assert isinstance(var_decl.initializer, FunctionCall)
        assert var_decl.initializer.name == "outer"
        assert len(var_decl.initializer.arguments) == 2
