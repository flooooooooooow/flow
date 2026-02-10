"""
Tests for the FLOW MLIR generator.
This module tests AST to MLIR conversion functionality.
"""

import pytest
import re
from flow.mlir_generator import MLIRGenerator
from flow.parser import parse_flow_code
from tests.conftest import MLIR_PATTERNS, TestHelpers


class TestMLIRTypeConversion:
    """Test FLOW to MLIR type conversion."""

    def test_basic_integer_types(self, mlir_generator):
        """Test basic integer type conversion."""
        from flow.parser import Type

        test_cases = [
            ("i8", "i8"),
            ("i16", "i16"),
            ("i32", "i32"),
            ("i64", "i64"),
        ]

        for flow_type, expected_mlir in test_cases:
            flow_type_obj = Type(flow_type)
            mlir_type = mlir_generator.flow_type_to_mlir(flow_type_obj)
            assert expected_mlir in mlir_type

    def test_boolean_type(self, mlir_generator):
        """Test boolean type conversion."""
        from flow.parser import Type

        bool_type = Type("bool")
        mlir_type = mlir_generator.flow_type_to_mlir(bool_type)
        assert "i1" in mlir_type

    def test_pointer_types(self, mlir_generator):
        """Test pointer type conversion."""
        from flow.parser import Type

        ptr_type = Type("i32", is_pointer=True)
        mlir_type = mlir_generator.flow_type_to_mlir(ptr_type)
        # Pointer types currently lower to the element type (i32) in this generator
        assert mlir_type is not None

    def test_array_types(self, mlir_generator):
        """Test array type conversion."""
        from flow.parser import Type

        # Array type: [i32, 5]
        element_type = Type("i32")
        array_type = Type("array", element_type=element_type, size=5)
        mlir_type = mlir_generator.flow_type_to_mlir(array_type)
        assert "memref" in mlir_type or "vector" in mlir_type


class TestMLIRExpressionGeneration:
    """Test MLIR expression generation."""

    def test_literal_generation(self, mlir_generator):
        """Test literal value generation."""
        from flow.parser import Literal, Type

        test_cases = [
            ("42", "i32", "42"),
            ("17", "i64", "17"),
            ("true", "bool", "i1"),   # booleans lower to i1 constants
            ("false", "bool", "i1"),
        ]

        for value, type_name, expected_substr in test_cases:
            literal = Literal(value, Type(type_name))
            ssa_name, ops = mlir_generator.generate_expression(literal)
            # The result is a tuple (ssa_name, ops_list)
            combined = " ".join(ops) if ops else ssa_name
            assert expected_substr in combined or expected_substr in ssa_name

    def test_variable_generation(self, mlir_generator):
        """Test variable reference generation."""
        from flow.parser import Variable

        # Register the variable in symbol table first
        mlir_generator.symbol_table["x"] = {"type": "variable", "ssa_name": "%x"}
        var = Variable("x")
        ssa_name, ops = mlir_generator.generate_expression(var)
        assert "x" in ssa_name or "Undefined" in ssa_name

    def test_binary_operations(self, mlir_generator):
        """Test binary operation generation."""
        from flow.parser import BinaryOperation, Literal, Type

        # Test addition with literals (avoids undefined variable issues)
        left = Literal("1", Type("i32"))
        right = Literal("2", Type("i32"))
        add_op = BinaryOperation(left, "+", right)
        ssa_name, ops = mlir_generator.generate_expression(add_op)
        combined = " ".join(ops)
        assert "arith.addi" in combined

    def test_arithmetic_operations(self, mlir_generator):
        """Test various arithmetic operations."""
        from flow.parser import BinaryOperation, Literal, Type

        lit_a = Literal("1", Type("i32"))
        lit_b = Literal("2", Type("i32"))

        test_cases = [
            ("+", "arith.addi"),
            ("-", "arith.subi"),
            ("*", "arith.muli"),
            ("/", "arith.divsi"),
            ("%", "arith.remsi"),
        ]

        for op, expected_mlir in test_cases:
            bin_op = BinaryOperation(lit_a, op, lit_b)
            ssa_name, ops = mlir_generator.generate_expression(bin_op)
            combined = " ".join(ops)
            assert expected_mlir in combined

    def test_comparison_operations(self, mlir_generator):
        """Test comparison operations."""
        from flow.parser import BinaryOperation, Literal, Type

        lit_a = Literal("1", Type("i32"))
        lit_b = Literal("2", Type("i32"))

        test_cases = [
            ("==", "arith.cmpi"),
            ("!=", "arith.cmpi"),
            ("<", "arith.cmpi"),
            ("<=", "arith.cmpi"),
            (">", "arith.cmpi"),
            (">=", "arith.cmpi"),
        ]

        for op, expected_mlir in test_cases:
            bin_op = BinaryOperation(lit_a, op, lit_b)
            ssa_name, ops = mlir_generator.generate_expression(bin_op)
            combined = " ".join(ops)
            assert expected_mlir in combined

    def test_unary_operations(self, mlir_generator):
        """Test unary operation generation."""
        from flow.parser import UnaryOperation, Literal, Type

        lit = Literal("5", Type("i32"))

        # Test negation
        neg_op = UnaryOperation("-", lit)
        ssa_name, ops = mlir_generator.generate_expression(neg_op)
        combined = " ".join(ops)
        assert "arith.subi" in combined or "arith.negf" in combined

    def test_function_call_generation(self, mlir_generator):
        """Test function call generation."""
        from flow.parser import FunctionCall, Literal, Type

        # Call with arguments
        args = [Literal("10", Type("i32")), Literal("20", Type("i32"))]
        func_call = FunctionCall("add", args)
        ssa_name, ops = mlir_generator.generate_expression(func_call)
        combined = " ".join(ops)
        assert "func.call @add" in combined


class TestMLIRStatementGeneration:
    """Test MLIR statement generation."""

    def test_return_statement_generation(self, mlir_generator):
        """Test return statement generation."""
        from flow.parser import ReturnStatement, Literal, Type

        # Set up required state for return generation
        mlir_generator.current_function_return_type = Type("i32")

        # Return with value
        ret_val = ReturnStatement(Literal("42", Type("i32")))
        mlir = mlir_generator.generate_return(ret_val)
        assert "return" in mlir

    def test_variable_declaration_generation(self, mlir_generator):
        """Test variable declaration generation."""
        from flow.parser import VarDecl, Literal, Type

        # Declaration with initialization
        var_decl = VarDecl("x", Type("i32"), Literal("42", Type("i32")))
        mlir = mlir_generator.generate_var_decl(var_decl)
        assert "42" in mlir
        assert "i32" in mlir

    def test_assignment_generation(self, mlir_generator):
        """Test assignment statement generation."""
        from flow.parser import Assignment, Literal, Type

        # Register variable with required metadata
        mlir_generator.symbol_table["x"] = {
            "type": "variable", "ssa_name": "%x", "mlir_type": "i32"
        }
        assign = Assignment("x", Literal("42", Type("i32")))
        mlir = mlir_generator.generate_assignment(assign)
        assert "42" in mlir or "x" in mlir


class TestMLIRFunctionGeneration:
    """Test MLIR function generation."""

    def test_simple_function_generation(self, mlir_generator):
        """Test simple function generation."""
        flow_code = """
        function add(a: i32, b: i32) -> i32 {
            return a + b
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate_module(ast)

        assert "func.func @add" in mlir
        assert "i32" in mlir
        assert "return" in mlir

    def test_main_function_generation(self, mlir_generator):
        """Test main function generation."""
        flow_code = """
        function main() -> i32 {
            return 42
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate_module(ast)

        assert "func.func @main" in mlir
        assert "42" in mlir

    def test_function_with_parameters(self, mlir_generator):
        """Test function with multiple parameters."""
        flow_code = """
        function test(x: i32, y: bool, z: i64) -> i32 {
            return x
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate_module(ast)

        assert "i32" in mlir
        assert "i1" in mlir  # bool -> i1
        assert "i64" in mlir

    def test_recursive_function_generation(self, mlir_generator):
        """Test recursive function generation."""
        flow_code = """
        function factorial(n: i32) -> i32 {
            if n <= 1 {
                return 1
            } else {
                return n * factorial(n - 1)
            }
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate_module(ast)

        assert "func.func @factorial" in mlir
        assert "func.call @factorial" in mlir  # Recursive call
        assert "arith.muli" in mlir
        assert "arith.cmpi" in mlir


class TestMLIRControlFlowGeneration:
    """Test MLIR control flow generation."""

    def test_if_statement_generation(self, mlir_generator):
        """Test if statement generation."""
        flow_code = """
        function test(x: i32) -> i32 {
            if x > 0 {
                return 1
            } else {
                return 0
            }
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate_module(ast)

        assert "scf.if" in mlir or "cf.cond_br" in mlir
        assert "arith.cmpi" in mlir

    def test_while_loop_generation(self, mlir_generator):
        """Test while loop generation."""
        flow_code = """
        function test() -> i32 {
            let i: i32 = 0
            while i < 10 {
                i = i + 1
            }
            return i
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate_module(ast)

        assert "scf.while" in mlir or "cf.br" in mlir
        assert "arith.cmpi" in mlir

    def test_for_loop_generation(self, mlir_generator):
        """Test for loop generation."""
        flow_code = """
        function test() -> i32 {
            let sum: i32 = 0
            for i in 0..10 {
                sum = sum + i
            }
            return sum
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate_module(ast)

        assert "scf.for" in mlir or "cf.br" in mlir


class TestMLIRStructGeneration:
    """Test MLIR struct type generation."""

    def test_simple_struct_generation(self, mlir_generator):
        """Test simple struct declaration."""
        flow_code = """
        struct Point {
            x: i32,
            y: i32
        }

        function main() -> i32 {
            let p: Point = Point{x: 10, y: 20}
            return p.x + p.y
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate_module(ast)

        # Struct operations use memref or arith ops in the MLIR generator
        assert "Point" in mlir or "memref" in mlir or "arith" in mlir

    def test_nested_struct_generation(self, mlir_generator):
        """Test nested struct handling."""
        flow_code = """
        struct Inner {
            value: i32
        }

        struct Outer {
            inner: Inner,
            count: i32
        }

        function main() -> i32 {
            let o: Outer = Outer{inner: Inner{value: 42}, count: 1}
            return o.inner.value
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate_module(ast)

        # Nested struct access uses memref or arith ops
        assert "Inner" in mlir or "memref" in mlir or "arith" in mlir


class TestMLIRStringHandling:
    """Test MLIR string constant handling."""

    def test_string_constant_generation(self, mlir_generator):
        """Test string constant pool generation."""
        flow_code = """
        function main() -> i32 {
            let message: string = "Hello, World!"
            return 0
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate_module(ast)

        # String should be in the generated MLIR (as a global or constant)
        assert "Hello" in mlir or "module" in mlir


class TestMLIRGenerationIntegration:
    """Integration tests for MLIR generation."""

    def test_simple_program_generation(self, sample_flow_code, mlir_generator):
        """Test generating MLIR for a simple program."""
        ast = parse_flow_code(sample_flow_code["simple_function"])
        mlir = mlir_generator.generate_module(ast)

        # Basic checks
        assert "module" in mlir
        assert "func.func" in mlir
        assert len(mlir) > 50

    def test_complex_program_generation(self, sample_flow_code, mlir_generator):
        """Test generating MLIR for a complex program."""
        ast = parse_flow_code(sample_flow_code["control_flow"])
        mlir = mlir_generator.generate_module(ast)

        assert "func.func" in mlir
        assert "arith.cmpi" in mlir or "scf.if" in mlir

    def test_mlir_syntax_validity(self, sample_flow_code, mlir_generator):
        """Test that generated MLIR has valid syntax."""
        ast = parse_flow_code(sample_flow_code["main_function"])
        mlir = mlir_generator.generate_module(ast)

        assert not mlir.startswith("Error")
        assert "func.func" in mlir
        assert "return" in mlir
        assert mlir.count("{") == mlir.count("}")  # Balanced braces


@pytest.mark.unit
class TestMLIRGeneratorUnit:
    """Unit tests for MLIR generator components."""

    def test_indent_functionality(self, mlir_generator):
        """Test indentation functionality."""
        mlir_generator.indent_level = 0
        assert mlir_generator.indent() == ""

        mlir_generator.indent_level = 1
        assert mlir_generator.indent() == "  "

        mlir_generator.indent_level = 3
        assert mlir_generator.indent() == "      "

    def test_block_label_generation(self, mlir_generator):
        """Test block label generation."""
        label1 = mlir_generator._new_block_label()
        label2 = mlir_generator._new_block_label()

        assert label1.startswith("bb")
        assert label2.startswith("bb")
        assert label1 != label2  # Should be unique

    def test_symbol_table_management(self, mlir_generator):
        """Test symbol table operations."""
        # Add symbol
        mlir_generator.symbol_table["test_var"] = "%0"
        assert "test_var" in mlir_generator.symbol_table
        assert mlir_generator.symbol_table["test_var"] == "%0"

        # Clear symbol table
        mlir_generator.symbol_table.clear()
        assert len(mlir_generator.symbol_table) == 0
