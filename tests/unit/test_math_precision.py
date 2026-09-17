"""Precision-correct libm intrinsic selection for f32 (issue #734).

A single-precision math call should lower to the `*f` libm entry point
(`sqrtf`, `expf`) rather than the bare double-precision name, which widens
f32 to f64 and back. An f64 argument keeps the double-precision call, and a
mixed call keeps it too.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def _gen(source: str) -> str:
    return flow_to_c(parse_flow_code(source))


def _return_lines(source: str):
    return [l.strip() for l in _gen(source).splitlines() if "return" in l]


def test_f32_math_uses_single_precision_intrinsics():
    src = """
    import math
    function f(x: f32) -> f32 {
        return sqrt(x) + sin(x) + cos(x) + exp(x) + log(x) + fabs(x)
    }
    """
    line = " ".join(_return_lines(src))
    for fn in ("sqrtf(", "sinf(", "cosf(", "expf(", "logf(", "fabsf("):
        assert fn in line, (fn, line)
    # No bare double-precision call slipped through.
    for bare in ("sqrt(x)", "sin(x)", "cos(x)", "exp(x)", "log(x)", "fabs(x)"):
        assert bare not in line, (bare, line)


def test_f32_pow_two_args_uses_powf():
    src = """
    import math
    function f(x: f32, y: f32) -> f32 { return pow(x, y) }
    """
    line = " ".join(_return_lines(src))
    assert "powf(" in line and "pow(x" not in line.replace("powf(", ""), line


def test_f64_math_keeps_double_precision():
    src = """
    import math
    function g(x: f64) -> f64 {
        return sqrt(x) + sin(x) + exp(x)
    }
    """
    line = " ".join(_return_lines(src))
    for fn in ("sqrt(x)", "sin(x)", "exp(x)"):
        assert fn in line, (fn, line)
    for widened in ("sqrtf(", "sinf(", "expf("):
        assert widened not in line, (widened, line)


def test_mixed_precision_pow_stays_double():
    src = """
    import math
    function m(x: f32, y: f64) -> f64 { return pow(x, y) }
    """
    line = " ".join(_return_lines(src))
    assert "pow(" in line and "powf(" not in line, line


def test_integer_abs_is_not_given_a_float_suffix():
    # `abs`/`labs` are integer-only and have no `*f` variant.
    src = """
    function a(n: i32) -> i32 { return abs(n) }
    """
    line = " ".join(_return_lines(src))
    assert "absf(" not in line, line
