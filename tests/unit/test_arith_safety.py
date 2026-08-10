"""Arithmetic safety checks (#264 / #265).

Division-by-zero and invalid shifts are rejected at type-check time when
operands are literals.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


def _check(source: str):
    return TypeChecker().check(parse_flow_code(source))


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
