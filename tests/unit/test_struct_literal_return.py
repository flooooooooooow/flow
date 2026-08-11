"""Regression tests for struct literal return with embedded calls (#409).

Returning a struct literal where fields are initialized with function
calls should compile and produce correct results.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def _gen_c(source: str) -> str:
    decls = parse_flow_code(source)
    return flow_to_c(decls)


def test_struct_literal_return_with_binary_ops():
    """Struct literal with binary operation field values."""
    c = _gen_c("""
struct Foo { x: i32, y: i32 }
function make_foo(a: i32, b: i32) -> Foo {
    return Foo { x: a + 1, y: b * 2 }
}
""")
    assert "make_foo" in c


def test_struct_literal_return_with_function_calls():
    """Struct literal with function call field values."""
    c = _gen_c("""
struct Foo { x: i32, y: i32 }
function inc(n: i32) -> i32 { return n + 1 }
function dbl(n: i32) -> i32 { return n * 2 }
function make_foo(a: i32, b: i32) -> Foo {
    return Foo { x: inc(a), y: dbl(b) }
}
""")
    assert "make_foo" in c
    assert "inc_" in c
    assert "dbl_" in c


def test_struct_literal_return_with_pointer_field():
    """Struct literal with pointer-returning function call."""
    c = _gen_c("""
struct Foo { x: ptr<i32>, n: i32 }
function make_array(n: i32) -> ptr<i32> { return null }
function make_foo(n: i32) -> Foo {
    return Foo { x: make_array(n), n: n }
}
""")
    assert "make_foo" in c
    assert "make_array" in c


def test_struct_literal_return_with_nested_struct():
    """Struct literal with nested struct-returning function call."""
    c = _gen_c("""
struct Matrix { data: ptr<f32>, rows: i32, cols: i32 }
struct Foo { x: Matrix, n: i32 }
function make_matrix(r: i32, c: i32) -> Matrix {
    return Matrix { data: null, rows: r, cols: c }
}
function make_foo(r: i32, c: i32) -> Foo {
    return Foo { x: make_matrix(r, c), n: r * c }
}
""")
    assert "make_foo" in c
    assert "make_matrix" in c


def test_struct_literal_with_mixed_calls_and_literals():
    """Struct literal mixing function calls and plain literals."""
    c = _gen_c("""
struct Foo { a: i32, b: i32, c: i32 }
function f(x: i32) -> i32 { return x }
function make() -> Foo {
    return Foo { a: f(1), b: 2, c: f(3) }
}
""")
    assert "make" in c
