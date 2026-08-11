"""Tests for taking address of a pointer parameter (#423)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


def _check(source: str):
    decls = parse_flow_code(source)
    tc = TypeChecker()
    tc.check(decls)
    return tc.errors


def test_address_of_pointer_rejected():
    """Taking & of a ptr<T> parameter is a type error."""
    errors = _check("""
struct Parser { x: i32 }
function callee(p: ptr<Parser>) -> i32 { return 0 }
function caller(p: ptr<Parser>) -> i32 {
    return callee(&p)
}
""")
    assert any("address of a pointer" in e for e in errors)


def test_address_of_struct_allowed():
    """Taking & of a struct variable is allowed."""
    errors = _check("""
struct Parser { x: i32 }
function callee(p: ptr<Parser>) -> i32 { return 0 }
function caller() -> i32 {
    let s: Parser = Parser { x: 0 }
    return callee(&s)
}
""")
    assert not any("address of a pointer" in e for e in errors)


def test_address_of_int_allowed():
    """Taking & of an integer variable is allowed."""
    errors = _check("""
function foo(p: ptr<i32>) -> i32 { return 0 }
function main() -> i32 {
    let x: i32 = 0
    return foo(&x)
}
""")
    assert not any("address of a pointer" in e for e in errors)


def test_pass_pointer_directly_allowed():
    """Passing a pointer directly is allowed."""
    errors = _check("""
struct Parser { x: i32 }
function callee(p: ptr<Parser>) -> i32 { return 0 }
function caller(p: ptr<Parser>) -> i32 {
    return callee(p)
}
""")
    assert not any("address of a pointer" in e for e in errors)
