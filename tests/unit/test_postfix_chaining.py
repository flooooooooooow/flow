"""
Regression tests for postfix expression chaining (flow-ptr-field-parse).

The parser must chain index, field-access, and method-call postfix operators
arbitrarily: ptr[0].field, a.b[0].c, f()[1].x, pts[0].method(), (p)[0].x.
The C output for these shapes is covered by tests/cgen/postfix_chaining_*.
"""

from flow.parser import (
    Lexer,
    Parser,
    ArrayAccess,
    FieldAccess,
    FunctionCall,
    MethodCall,
    Variable,
    Assignment,
)


def parse_stmt(stmt: str):
    """Parse a single statement inside a function body and return its AST node."""
    code = "function main() -> i32 {\n    %s\n    return 0\n}\n" % stmt
    ast = Parser(Lexer(code)).parse()
    return ast[0].body.statements[0]


def rhs_of_let(stmt: str):
    node = parse_stmt(stmt)
    return node.initializer


class TestPostfixChainingParser:
    """Parser-level AST shape checks for chained postfix operators."""

    def test_index_then_field_read(self):
        expr = rhs_of_let("let a: i32 = pts[0].x")
        assert isinstance(expr, FieldAccess)
        assert expr.field == "x"
        assert isinstance(expr.object, ArrayAccess)
        assert isinstance(expr.object.array, Variable)
        assert expr.object.array.name == "pts"

    def test_index_then_field_write(self):
        node = parse_stmt("pts[0].x = 7")
        assert isinstance(node, Assignment)
        target = node.target_expr
        assert isinstance(target, FieldAccess)
        assert isinstance(target.object, ArrayAccess)

    def test_field_then_index_then_field(self):
        expr = rhs_of_let("let a: i32 = g.buses[0].buffer")
        assert isinstance(expr, FieldAccess)
        assert expr.field == "buffer"
        assert isinstance(expr.object, ArrayAccess)
        assert isinstance(expr.object.array, FieldAccess)
        assert expr.object.array.field == "buses"

    def test_index_field_index_write(self):
        node = parse_stmt("rb[0].data[rb[0].write_idx] = v")
        assert isinstance(node, Assignment)
        target = node.target_expr
        assert isinstance(target, ArrayAccess)
        assert isinstance(target.array, FieldAccess)
        assert isinstance(target.index, FieldAccess)

    def test_call_then_index_then_field(self):
        expr = rhs_of_let("let a: i32 = f()[1].x")
        assert isinstance(expr, FieldAccess)
        assert isinstance(expr.object, ArrayAccess)
        assert isinstance(expr.object.array, FunctionCall)
        assert expr.object.array.name == "f"

    def test_call_then_field(self):
        expr = rhs_of_let("let a: i32 = f().x")
        assert isinstance(expr, FieldAccess)
        assert isinstance(expr.object, FunctionCall)

    def test_index_then_method_call(self):
        expr = rhs_of_let("let a: i32 = pts[0].norm()")
        assert isinstance(expr, MethodCall)
        assert expr.method == "norm"
        assert isinstance(expr.object, ArrayAccess)

    def test_field_index_method_call(self):
        expr = rhs_of_let("let a: i32 = a.b[0].c()")
        assert isinstance(expr, MethodCall)
        assert expr.method == "c"
        assert isinstance(expr.object, ArrayAccess)
        assert isinstance(expr.object.array, FieldAccess)

    def test_method_call_then_field(self):
        expr = rhs_of_let("let a: i32 = a.b().c")
        assert isinstance(expr, FieldAccess)
        assert isinstance(expr.object, MethodCall)

    def test_method_call_then_index(self):
        expr = rhs_of_let("let a: i32 = a.b()[0]")
        assert isinstance(expr, ArrayAccess)
        assert isinstance(expr.array, MethodCall)

    def test_nested_index_then_field(self):
        expr = rhs_of_let("let a: i32 = m[0][1].x")
        assert isinstance(expr, FieldAccess)
        assert isinstance(expr.object, ArrayAccess)
        assert isinstance(expr.object.array, ArrayAccess)

    def test_deep_mixed_chain(self):
        expr = rhs_of_let("let a: i32 = a.b[0].c.d[1].e")
        # ((((a.b)[0]).c).d)[1].e
        assert isinstance(expr, FieldAccess)
        assert expr.field == "e"
        assert isinstance(expr.object, ArrayAccess)
        assert isinstance(expr.object.array, FieldAccess)
        assert expr.object.array.field == "d"

    def test_paren_then_index_then_field(self):
        expr = rhs_of_let("let a: i32 = (p)[0].x")
        assert isinstance(expr, FieldAccess)
        assert isinstance(expr.object, ArrayAccess)

    def test_compound_assign_on_element_field(self):
        node = parse_stmt("opt[0].t += 1")
        assert isinstance(node, Assignment)
        assert isinstance(node.target_expr, FieldAccess)
        assert isinstance(node.target_expr.object, ArrayAccess)

    def test_comparison_not_broken(self):
        expr = rhs_of_let("let a: bool = x < y")
        # Must still parse as a comparison, not a generic instantiation
        from flow.parser import BinaryOperation

        assert isinstance(expr, BinaryOperation)
        assert expr.operator == "<"


# C generation for these shapes, and the run of both programs, lives in
# tests/cgen/postfix_chaining_ptr_struct and postfix_chaining_array_struct.
