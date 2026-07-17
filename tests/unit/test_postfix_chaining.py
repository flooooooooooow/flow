"""
Regression tests for postfix expression chaining (flow-ptr-field-parse).

The parser must chain index, field-access, and method-call postfix operators
arbitrarily: ptr[0].field, a.b[0].c, f()[1].x, pts[0].method(), (p)[0].x.
The C generator must produce valid C for the resulting AST shapes.
"""

import shutil
import subprocess

import pytest

from flow.parser import (
    parse_flow_code,
    Lexer,
    Parser,
    ArrayAccess,
    FieldAccess,
    FunctionCall,
    MethodCall,
    Variable,
    Assignment,
)
from flow.c_generator import flow_to_c


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


POINTER_STRUCT_PROGRAM = """
extern {
    function malloc(size: i64) -> ptr<Body>
    function free(p: ptr<Body>)
}

struct Vec2 {
    x: f32,
    y: f32
}

struct Body {
    pos: Vec2,
    mass: f32,
    id: i32
}

function get_mass(b: Body) -> f32 {
    return b.mass
}

function main() -> i32 {
    let bodies: ptr<Body> = malloc(64)
    bodies[0].id = 1
    bodies[0].mass = 2.5
    bodies[0].pos.x = 1.5
    bodies[0].pos.y = 0.5
    bodies[1].id = 2
    bodies[1].mass = 4.0
    let total: f32 = bodies[0].mass + bodies[1].mass + bodies[0].pos.x + bodies[0].pos.y
    let m: f32 = bodies[0].get_mass()
    free(bodies)
    if total == 8.5 {
        if m == 2.5 {
            print("PASS")
            return 0
        }
    }
    print("FAIL")
    return 1
}
"""

ARRAY_OF_STRUCTS_PROGRAM = """
struct Note {
    pitch: i32,
    duration: i32
}

function main() -> i32 {
    let melody: array<Note, 4> = [
        Note { pitch: 60, duration: 1 },
        Note { pitch: 62, duration: 2 },
        Note { pitch: 64, duration: 3 },
        Note { pitch: 65, duration: 4 }
    ]
    let mut total: i32 = 0
    for i in 0 to 4 {
        total = total + melody[i].duration
    }
    if total == 10 {
        print("PASS")
        return 0
    }
    print("FAIL")
    return 1
}
"""


def generate_c(program: str) -> str:
    ast = parse_flow_code(program)
    return flow_to_c(ast)


class TestPostfixChainingCodegen:
    """C generation for chained postfix AST shapes."""

    def test_pointer_struct_element_field_c(self):
        c_code = generate_c(POINTER_STRUCT_PROGRAM)
        assert "bodies[0].mass" in c_code
        assert "bodies[0].pos.x" in c_code
        # Method call desugars to a plain call with receiver first
        # (name may be overload-mangled, e.g. get_mass_Body)
        assert "(bodies[0])" in c_code and "get_mass" in c_code
        # No stray arrow on the value produced by indexing
        assert "bodies[0]->" not in c_code

    def test_array_of_structs_element_field_c(self):
        c_code = generate_c(ARRAY_OF_STRUCTS_PROGRAM)
        # Element access may be wrapped in a bounds-check ternary; the field
        # access must still be applied to the element expression.
        assert "melody[i]" in c_code
        assert ".duration)" in c_code or "melody[i].duration" in c_code

    @pytest.mark.skipif(shutil.which("clang") is None, reason="clang not available")
    @pytest.mark.parametrize(
        "program", [POINTER_STRUCT_PROGRAM, ARRAY_OF_STRUCTS_PROGRAM]
    )
    def test_generated_c_compiles_and_passes(self, program, tmp_path):
        c_code = generate_c(program)
        c_file = tmp_path / "prog.c"
        exe_file = tmp_path / "prog"
        c_file.write_text(c_code)
        compile_result = subprocess.run(
            ["clang", "-Wno-everything", str(c_file), "-o", str(exe_file)],
            capture_output=True,
            text=True,
        )
        assert compile_result.returncode == 0, compile_result.stderr
        run_result = subprocess.run(
            [str(exe_file)], capture_output=True, text=True, timeout=30
        )
        assert run_result.returncode == 0, run_result.stdout + run_result.stderr
        assert "PASS" in run_result.stdout
