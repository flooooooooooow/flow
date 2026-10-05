"""Regression tests for array/vector size literals in types (flow-fuzz-float-array-size).

A fuzzer-found crash: `function f(x: [i32; 0.0]) { }` escaped as a raw
ValueError from int() inside parse_type. Any non-integer, negative, or
oversized size in a type must be rejected with a clean FlowSyntaxError
carrying line/column -- never a Python exception.
"""

import pytest

from flow.parser import FlowSyntaxError, parse_flow_code


BAD_SIZES = [
    ("float size in [T; N]", "function f(x: [i32; 0.0]) { }"),
    ("float size in [T; N] variant", "function f(x: [f64; 2.5]) { }"),
    ("exponent size in [T; N]", "function f(x: [i32; 1e3]) { }"),
    ("negative size in [T; N]", "function f(x: [i32; -1]) { }"),
    ("identifier size in [T; N]", "function f(x: [i32; n]) { }"),
    ("string size in [T; N]", 'function f(x: [i32; "4"]) { }'),
    ("huge size in [T; N]", "function f(x: [i32; 99999999999999999999]) { }"),
    ("float size in array<T, N>", "function f(x: array<i32, 2.5>) { }"),
    ("identifier size in array<T, N>", "function f(x: array<i32, n>) { }"),
    ("float size after vec", "function f(x: vec 1.5 i32) { }"),
]


@pytest.mark.parametrize(
    "src", [s for _, s in BAD_SIZES], ids=[i for i, _ in BAD_SIZES]
)
def test_bad_array_size_is_clean_syntax_error(src):
    with pytest.raises(FlowSyntaxError) as ei:
        parse_flow_code(src)
    err = ei.value
    assert "size" in str(err)
    assert err.line == 1
    assert err.column is not None and err.column > 0


def test_float_array_size_message_and_location():
    with pytest.raises(FlowSyntaxError) as ei:
        parse_flow_code("function f(x: [i32; 0.0]) { }")
    err = ei.value
    assert "array size must be an integer literal" in str(err)
    assert err.line == 1
    assert err.column == 21  # points at the 0.0 token


GOOD_SIZES = [
    ("[T; N] literal", "function f(x: [i32; 4]) { }"),
    ("[T; 0] zero size", "function f(x: [i32; 0]) { }"),
    ("[T; N] hex literal", "function f(x: [i32; 0x10]) { }"),
    ("array<T, N>", "function f(x: array<i32, 4>) { }"),
    ("vec N T", "function f(x: vec 4 f32) { }"),
]


@pytest.mark.parametrize(
    "src", [s for _, s in GOOD_SIZES], ids=[i for i, _ in GOOD_SIZES]
)
def test_valid_array_sizes_still_parse(src):
    parse_flow_code(src)  # must not raise
