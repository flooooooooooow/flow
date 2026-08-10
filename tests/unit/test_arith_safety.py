"""MISRA Phase 0 arithmetic safety (#264 / #265).

Division-by-zero and invalid shifts must be rejected at type-check time when
operands are literals, and the C generator must emit runtime handlers for
dynamic cases.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c
from flow.type_checker import TypeChecker


def _check(source: str):
    return TypeChecker().check(parse_flow_code(source))


def _c(source: str) -> str:
    return flow_to_c(parse_flow_code(source))


def test_literal_div_by_zero_rejected():
    result = _check(
        """
        function main() -> i32 {
            return 10 / 0
        }
        """
    )
    assert any("Division/modulo by zero" in e for e in result.errors)


def test_literal_mod_by_zero_rejected():
    result = _check(
        """
        function main() -> i32 {
            return 10 % 0
        }
        """
    )
    assert any("Division/modulo by zero" in e for e in result.errors)


def test_literal_shift_out_of_range_rejected():
    result = _check(
        """
        function main() -> i32 {
            return 1 << 32
        }
        """
    )
    assert any("Shift amount" in e for e in result.errors)


def test_literal_negative_left_shift_rejected():
    result = _check(
        """
        function main() -> i32 {
            return -1 << 1
        }
        """
    )
    assert any("Left shift of a negative" in e for e in result.errors)


def test_c_emits_div0_handler():
    c = _c(
        """
        function main() -> i32 {
            let a: i32 = 10
            let b: i32 = 2
            return a / b
        }
        """
    )
    assert "flow_div_by_zero_handler" in c
    assert "FLOW_CHECKED_DIV" in c
    assert "flow_shift_ub_handler" in c


def test_c_emits_shift_guard():
    c = _c(
        """
        function main() -> i32 {
            let a: i32 = 1
            let b: i32 = 3
            return a << b
        }
        """
    )
    assert "flow_shift_ub_handler" in c
    assert "FLOW_CHECKED_SHL" in c
    assert "sizeof" in c


def test_float_div_has_no_div0_guard():
    c = _c(
        """
        function main() -> i32 {
            let a: f64 = 1.0
            let b: f64 = 0.0
            let c: f64 = a / b
            return 0
        }
        """
    )
    # Handler helpers are present for the TU; the / expression itself must
    # remain a raw float divide (IEEE Inf), not wrapped in FLOW_CHECKED_DIV.
    assert "FLOW_CHECKED_DIV((a), (b))" not in c
    assert "a / b" in c or "(a / b)" in c


def test_c_emits_overflow_handler():
    """Signed integer +,-,* must emit FLOW_CHECKED_* macros (#263)."""
    c = _c(
        """
        function main() -> i32 {
            let a: i32 = 100
            let b: i32 = 200
            let s: i32 = a + b
            let d: i32 = a - b
            let p: i32 = a * b
            return s + d + p
        }
        """
    )
    assert "flow_overflow_handler" in c
    assert "FLOW_CHECKED_ADD" in c
    assert "FLOW_CHECKED_SUB" in c
    assert "FLOW_CHECKED_MUL" in c


def test_float_arith_has_no_overflow_guard():
    """Float +,-,* must not get overflow checks (IEEE, not UB)."""
    c = _c(
        """
        function main() -> i32 {
            let a: f64 = 1.0
            let b: f64 = 2.0
            let c: f64 = a + b
            return 0
        }
        """
    )
    # The handler is emitted for the TU, but the float + must stay raw.
    assert "FLOW_CHECKED_ADD((a), (b))" not in c
    assert "a + b" in c or "(a + b)" in c


def test_unsigned_arith_has_no_overflow_guard():
    """Unsigned wraparound is well-defined in C, not UB; skip the check."""
    c = _c(
        """
        function main() -> i32 {
            let a: u32 = 100
            let b: u32 = 200
            let c: u32 = a + b
            return 0
        }
        """
    )
    assert "FLOW_CHECKED_ADD((a), (b))" not in c
