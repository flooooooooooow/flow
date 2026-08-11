"""Regression tests for inline exp() in nested while loops (#421).

Calling exp() inline inside a nested while loop should not cause a bus
error. The bug was likely caused by unsafe vectorization pragmas (#414)
or error suppression (#413).
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


def test_inline_exp_in_nested_while_compiles():
    """Inline exp() in nested while loop compiles without error."""
    c = _gen_c("""
function buggy() -> void {
    let mut i: i32 = 0
    while i < 10 {
        let mut k: i32 = 0
        while k < 10 {
            let z: f32 = 0.0
            let p: f32 = 1.0 / (1.0 + exp((-z) as f64) as f32)
            k = k + 1
        }
        i = i + 1
    }
}
function main() -> i32 { return 0 }
""")
    assert "buggy" in c
    assert "exp" in c


def test_inline_exp_in_for_loop_compiles():
    """Inline exp() in a for loop compiles without error."""
    c = _gen_c("""
function sigmoid_loop(n: i32) -> void {
    for i in 0 to n {
        let z: f32 = 0.5
        let p: f32 = 1.0 / (1.0 + exp((-z) as f64) as f32)
    }
}
function main() -> i32 { return 0 }
""")
    assert "sigmoid_loop" in c
    assert "exp" in c


def test_sigmoid_function_compiles():
    """The sigmoid helper function compiles correctly."""
    c = _gen_c("""
function _sigmoid(z: f32) -> f32 {
    let result: f32 = 1.0 / (1.0 + exp((-z) as f64) as f32)
    return result
}
""")
    assert "_sigmoid" in c
    assert "exp" in c


def test_nested_while_no_vectorization_pragma():
    """Nested while loops do not get vectorization pragmas."""
    c = _gen_c("""
function f() -> void {
    let mut i: i32 = 0
    while i < 10 {
        let mut k: i32 = 0
        while k < 10 {
            let z: f32 = exp(0.0 as f64) as f32
            k = k + 1
        }
        i = i + 1
    }
}
""")
    assert "ivdep" not in c
    assert "vectorize" not in c
