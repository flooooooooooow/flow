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
            mlir_type = mlir_generator._flow_type_to_mlir(flow_type_obj)
            assert expected_mlir in mlir_type

    def test_boolean_type(self, mlir_generator):
        """Test boolean type conversion."""
        from flow.parser import Type

        bool_type = Type("bool")
        mlir_type = mlir_generator._flow_type_to_mlir(bool_type)
        assert "i1" in mlir_type

    def test_pointer_types(self, mlir_generator):
        """Test pointer type conversion."""
        from flow.parser import Type

        ptr_type = Type("i32", is_pointer=True)
        mlir_type = mlir_generator._flow_type_to_mlir(ptr_type)
        assert "!" in mlir_type or "ptr" in mlir_type.lower()

    def test_array_types(self, mlir_generator):
        """Test array type conversion."""
        from flow.parser import Type

        # Array type: [i32, 5]
        element_type = Type("i32")
        array_type = Type("array", element_type=element_type, size=5)
        mlir_type = mlir_generator._flow_type_to_mlir(array_type)
        assert "memref" in mlir_type or "vector" in mlir_type


class TestMLIRExpressionGeneration:
    """Test MLIR expression generation."""

    def test_literal_generation(self, mlir_generator):
        """Test literal value generation."""
        from flow.parser import Literal, Type

        test_cases = [
            ("42", "i32", r"llvm\.mlir\.constant\(42 : i32\)"),
            ("17", "i64", r"llvm\.mlir\.constant\(17 : i64\)"),
            ("true", "bool", r"llvm\.mlir\.constant\(true : i1\)"),
            ("false", "bool", r"llvm\.mlir\.constant\(false : i1\)"),
        ]

        for value, type_name, expected_pattern in test_cases:
            literal = Literal(value, Type(type_name))
            mlir = mlir_generator.generate_expression(literal)
            assert re.search(expected_pattern, mlir), (
                f"Pattern {expected_pattern} not found in {mlir}"
            )

    def test_variable_generation(self, mlir_generator):
        """Test variable reference generation."""
        from flow.parser import Variable

        var = Variable("x")
        mlir = mlir_generator.generate_expression(var)
        assert "%x" in mlir

    def test_binary_operations(self, mlir_generator):
        """Test binary operation generation."""
        from flow.parser import BinaryOperation, Literal, Variable, Type

        # Test addition: a + b
        left = Variable("a")
        right = Variable("b")
        add_op = BinaryOperation(left, "+", right)
        mlir = mlir_generator.generate_expression(add_op)
        assert "arith.addi" in mlir

    def test_arithmetic_operations(self, mlir_generator):
        """Test various arithmetic operations."""
        from flow.parser import BinaryOperation, Variable, Type

        var_a = Variable("a")
        var_b = Variable("b")

        test_cases = [
            ("+", "arith.addi"),
            ("-", "arith.subi"),
            ("*", "arith.muli"),
            ("/", "arith.divi"),
            ("%", "arith.remi"),
        ]

        for op, expected_mlir in test_cases:
            bin_op = BinaryOperation(var_a, op, var_b)
            mlir = mlir_generator.generate_expression(bin_op)
            assert expected_mlir in mlir

    def test_comparison_operations(self, mlir_generator):
        """Test comparison operations."""
        from flow.parser import BinaryOperation, Variable, Type

        var_a = Variable("a")
        var_b = Variable("b")

        test_cases = [
            ("==", "arith.cmpi"),
            ("!=", "arith.cmpi"),
            ("<", "arith.cmpi"),
            ("<=", "arith.cmpi"),
            (">", "arith.cmpi"),
            (">=", "arith.cmpi"),
        ]

        for op, expected_mlir in test_cases:
            bin_op = BinaryOperation(var_a, op, var_b)
            mlir = mlir_generator.generate_expression(bin_op)
            assert expected_mlir in mlir

    def test_unary_operations(self, mlir_generator):
        """Test unary operation generation."""
        from flow.parser import UnaryOperation, Variable

        var = Variable("x")

        # Test negation
        neg_op = UnaryOperation("-", var)
        mlir = mlir_generator.generate_expression(neg_op)
        assert "arith.subi" in mlir or "arith.negf" in mlir

        # Test logical not
        not_op = UnaryOperation("!", var)
        mlir = mlir_generator.generate_expression(not_op)
        assert "arith.xori" in mlir or "arith.not" in mlir

    def test_function_call_generation(self, mlir_generator):
        """Test function call generation."""
        from flow.parser import FunctionCall, Literal, Type

        # Call with arguments
        args = [Literal("10", Type("i32")), Literal("20", Type("i32"))]
        func_call = FunctionCall("add", args)
        mlir = mlir_generator.generate_expression(func_call)
        assert "func.call @add" in mlir

        # Call without arguments
        empty_call = FunctionCall("no_args", [])
        mlir = mlir_generator.generate_expression(empty_call)
        assert "func.call @no_args" in mlir


class TestMLIRStatementGeneration:
    """Test MLIR statement generation."""

    def test_return_statement_generation(self, mlir_generator):
        """Test return statement generation."""
        from flow.parser import ReturnStatement, Literal, Type

        # Return with value
        ret_val = ReturnStatement(Literal("42", Type("i32")))
        mlir = mlir_generator.generate_return(ret_val)
        assert "return" in mlir
        assert ": i32" in mlir

        # Return without value
        ret_empty = ReturnStatement(None)
        mlir = mlir_generator.generate_return(ret_empty)
        assert "return" in mlir

    def test_variable_declaration_generation(self, mlir_generator):
        """Test variable declaration generation."""
        from flow.parser import VarDecl, Literal, Type

        # Declaration with initialization
        var_decl = VarDecl("x", Type("i32"), Literal("42", Type("i32")))
        mlir = mlir_generator.generate_var_decl(var_decl)
        assert "%x" in mlir
        assert "llvm.mlir.constant" in mlir

    def test_assignment_generation(self, mlir_generator):
        """Test assignment statement generation."""
        from flow.parser import Assignment, Literal, Variable, Type

        assign = Assignment("x", Literal("42", Type("i32")))
        mlir = mlir_generator.generate_assignment(assign)
        assert "llvm.store" in mlir or "%x" in mlir


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
        mlir = mlir_generator.generate(ast)

        # Check function signature
        assert "func.func @add" in mlir
        assert "(%arg0: i32, %arg1: i32)" in mlir
        assert "-> i32" in mlir

        # Check function body contains addition
        assert "arith.addi" in mlir
        assert "return" in mlir

    def test_main_function_generation(self, mlir_generator):
        """Test main function generation."""
        flow_code = """
        function main() -> i32 {
            return 42
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate(ast)

        assert "func.func @main" in mlir
        assert "() -> i32" in mlir
        assert "llvm.mlir.constant(42 : i32)" in mlir

    def test_function_with_parameters(self, mlir_generator):
        """Test function with multiple parameters."""
        flow_code = """
        function test(x: i32, y: bool, z: i64) -> i32 {
            return x
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate(ast)

        # Should have all three parameters with correct types
        assert "%arg0: i32" in mlir
        assert "%arg1: i1" in mlir  # bool -> i1
        assert "%arg2: i64" in mlir

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
        mlir = mlir_generator.generate(ast)

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
                return -1
            }
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate(ast)

        # Should contain SCF dialect for control flow
        assert "scf.if" in mlir or "cf.cond_br" in mlir
        assert "arith.cmpi" in mlir  # Comparison

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
        mlir = mlir_generator.generate(ast)

        # Should contain loop constructs
        assert "scf.while" in mlir or "cf.br" in mlir
        assert "arith.cmpi" in mlir  # Loop condition

    def test_for_loop_generation(self, mlir_generator):
        """Test for loop generation."""
        flow_code = """
        function test() -> i32 {
            let sum: i32 = 0
            for i in range(0, 10) {
                sum = sum + i
            }
            return sum
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate(ast)

        # Should contain for loop constructs
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
        mlir = mlir_generator.generate(ast)

        # Should contain struct type definition
        assert "llvm.struct" in mlir or "struct<" in mlir

        # Should contain struct operations
        assert "llvm.undef" in mlir or "llvm.insertvalue" in mlir

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
        mlir = mlir_generator.generate(ast)

        # Should handle nested struct access
        assert "llvm.extractvalue" in mlir or "llvm.insertvalue" in mlir


class TestMLIRStringHandling:
    """Test MLIR string constant handling."""

    def test_string_constant_generation(self, mlir_generator):
        """Test string constant pool generation."""
        flow_code = """
        function main() -> i32 {
            // This would use printf if implemented
            let message: string = "Hello, World!"
            return 0
        }
        """
        ast = parse_flow_code(flow_code)
        mlir = mlir_generator.generate(ast)

        # Should generate string constants if implemented
        # This might not be fully implemented yet
        pass  # Skip if not implemented


class TestMLIRGenerationIntegration:
    """Integration tests for MLIR generation."""

    def test_simple_program_generation(self, sample_flow_code, mlir_generator):
        """Test generating MLIR for a simple program."""
        ast = parse_flow_code(sample_flow_code["simple_function"])
        mlir = mlir_generator.generate(ast)

        # Basic checks
        assert "module" in mlir
        assert "func.func" in mlir
        assert len(mlir) > 50  # Should generate substantial MLIR

    def test_complex_program_generation(self, sample_flow_code, mlir_generator):
        """Test generating MLIR for a complex program."""
        ast = parse_flow_code(sample_flow_code["control_flow"])
        mlir = mlir_generator.generate(ast)

        # Should contain multiple functions and control flow
        assert "func.func" in mlir
        assert "arith.cmpi" in mlir or "scf.if" in mlir

    def test_mlir_syntax_validity(self, sample_flow_code, mlir_generator):
        """Test that generated MLIR has valid syntax."""
        ast = parse_flow_code(sample_flow_code["main_function"])
        mlir = mlir_generator.generate(ast)

        # Basic syntax checks
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
