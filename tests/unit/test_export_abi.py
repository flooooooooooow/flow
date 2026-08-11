"""Tests for --export / --module-name C/WASM ABI (#396)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


SIMPLE = """
function add(a: i32, b: i32) -> i32 { return a + b }
function main() -> i32 { return add(1, 2) }
"""

VOID_FN = """
function greet() -> void { println("hello") }
function main() -> i32 { greet(); return 0 }
"""

NO_PARAMS = """
function answer() -> i32 { return 42 }
function main() -> i32 { return answer() }
"""


def test_export_alias_emitted():
    c = flow_to_c(parse_flow_code(SIMPLE), export_names=["add"])
    assert "flow_export_add" in c
    assert "visibility" in c


def test_export_alias_calls_mangled_name():
    c = flow_to_c(parse_flow_code(SIMPLE), export_names=["add"])
    # add(i32, i32) mangles to add_i32_i32
    assert "add_i32_i32(a, b)" in c


def test_no_export_when_not_requested():
    c = flow_to_c(parse_flow_code(SIMPLE))
    assert "flow_export" not in c


def test_export_void_function():
    c = flow_to_c(parse_flow_code(VOID_FN), export_names=["greet"])
    assert "flow_export_greet" in c
    # Void function should not have a return statement in the alias body
    assert "void flow_export_greet(void)" in c


def test_export_no_param_function():
    c = flow_to_c(parse_flow_code(NO_PARAMS), export_names=["answer"])
    assert "flow_export_answer" in c
    assert "answer()" in c


def test_export_missing_function_emits_comment():
    c = flow_to_c(parse_flow_code(SIMPLE), export_names=["nonexistent"])
    assert "not found" in c
    assert "flow_export_nonexistent" not in c


def test_export_multiple_functions():
    code = """
    function foo(a: i32) -> i32 { return a }
    function bar(b: i32) -> i32 { return b }
    function main() -> i32 { return foo(1) + bar(2) }
    """
    c = flow_to_c(parse_flow_code(code), export_names=["foo", "bar"])
    assert "flow_export_foo" in c
    assert "flow_export_bar" in c


def test_export_section_header():
    c = flow_to_c(parse_flow_code(SIMPLE), export_names=["add"])
    assert "Flow export aliases" in c
