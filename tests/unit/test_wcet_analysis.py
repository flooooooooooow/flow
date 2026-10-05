"""Tests for WCET and stack depth analysis (#282)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.wcet_analysis import (
    analyze_flow_source,
    _collect_functions,
    compute_stack_depth,
    compute_wcet,
    TYPE_SIZES,
)


SIMPLE = """
function helper(x: i32) -> i32 {
    let y: i32 = x * 2
    return y + 1
}

function compute(n: i32) -> i32 {
    let mut sum: i32 = 0
    for i in 0 to n {
        sum = sum + helper(i)
    }
    return sum
}

function main() -> i32 {
    let result: i32 = compute(10)
    return 0
}
"""

NO_CALLS = """
function main() -> i32 {
    let x: i32 = 42
    return x
}
"""

WITH_WHILE = """
function loop_fn(n: i32) -> i32 {
    let mut i: i32 = 0
    @max_iterations(100)
    while i < n {
        i = i + 1
    }
    return i
}

function main() -> i32 {
    return loop_fn(50)
}
"""


def _get_funcs(source: str):
    decls = analyze_flow_source(source)
    return _collect_functions(decls)


def test_stack_depth_simple():
    funcs = _get_funcs(SIMPLE)
    results = compute_stack_depth(funcs)
    by_name = {r.function: r for r in results}
    # helper has 1 local (y: i32 = 4 bytes)
    assert by_name["helper"].value == 4
    # compute has 1 local (sum: i32 = 4 bytes) + helper (4) = 8
    assert by_name["compute"].value == 8
    # main has 1 local (result: i32 = 4) + compute chain
    assert by_name["main"].value >= 12


def test_stack_depth_no_calls():
    funcs = _get_funcs(NO_CALLS)
    results = compute_stack_depth(funcs)
    by_name = {r.function: r for r in results}
    # main has 1 local (x: i32 = 4 bytes), no callees
    assert by_name["main"].value == 4


def test_stack_depth_chain():
    funcs = _get_funcs(SIMPLE)
    results = compute_stack_depth(funcs)
    main_result = [r for r in results if r.function == "main"][0]
    assert "main" in main_result.chain
    assert "compute" in main_result.chain


def test_wcet_simple():
    funcs = _get_funcs(SIMPLE)
    results = compute_wcet(funcs)
    by_name = {r.function: r for r in results}
    # helper has a return and a declare, so cost > 0
    assert by_name["helper"].value > 0
    # compute calls helper, so compute cost > helper cost
    assert by_name["compute"].value > by_name["helper"].value


def test_wcet_while_with_max_iterations():
    funcs = _get_funcs(WITH_WHILE)
    results = compute_wcet(funcs)
    by_name = {r.function: r for r in results}
    # loop_fn has a while with @max_iterations(100), so cost should be high
    assert by_name["loop_fn"].value > 100


def test_wcet_no_calls():
    funcs = _get_funcs(NO_CALLS)
    results = compute_wcet(funcs)
    by_name = {r.function: r for r in results}
    # main has a declare + return, no calls
    assert by_name["main"].value > 0
    assert by_name["main"].value < 20


def test_type_sizes_complete():
    """Ensure common Flow types have size entries."""
    for t in ["i32", "i64", "f32", "f64", "bool", "ptr"]:
        assert t in TYPE_SIZES
        assert TYPE_SIZES[t] > 0


def test_extern_function_has_fixed_cost():
    source = """
    extern "C" {
        function foo(x: i32) -> i32
    }
    function main() -> i32 { return foo(1) }
    """
    funcs = _get_funcs(source)
    results = compute_stack_depth(funcs)
    by_name = {r.function: r for r in results}
    # main calls extern foo, which gets a fixed 64-byte estimate
    assert by_name["main"].value >= 64


def test_results_sorted_by_value():
    funcs = _get_funcs(SIMPLE)
    results = compute_stack_depth(funcs)
    values = [r.value for r in results]
    assert values == sorted(values, reverse=True)
