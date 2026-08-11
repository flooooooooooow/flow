"""Regression tests for string concatenation with + operator (#412).

String + string should concatenate and produce a new string.
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


def test_string_concat_two_literals():
    """Concatenating two string literals."""
    c = _gen_c('function main() -> i32 { let s: string = "ab" + "cd" ; print(s) ; return 0 }')
    assert "flow_strcat" in c


def test_string_concat_variable_and_literal():
    """Concatenating a string variable with a string literal."""
    c = _gen_c("""
function main() -> i32 {
    let prefix: string = "ab"
    let indent: string = prefix + "cd"
    print(indent)
    return 0
}
""")
    assert "flow_strcat" in c


def test_string_concat_three_parts():
    """Concatenating three strings."""
    c = _gen_c("""
function main() -> i32 {
    let s: string = "a" + "b" + "c"
    print(s)
    return 0
}
""")
    assert "flow_strcat" in c


def test_string_concat_in_print():
    """String concatenation directly in a print call."""
    c = _gen_c('function main() -> i32 { print("hello" + " " + "world") ; return 0 }')
    assert "flow_strcat" in c


def test_string_concat_in_function_return():
    """String concatenation in a function return."""
    c = _gen_c("""
function greet(name: string) -> string {
    return "Hello, " + name + "!"
}
""")
    assert "flow_strcat" in c
    assert "greet" in c
