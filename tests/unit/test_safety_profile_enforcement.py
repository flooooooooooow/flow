"""Safety profile enforcement: recursion (MISRA 17.2) and loop bounds (MISRA 17.4).

Under --profile safety/flight, the type checker rejects:
- Unbounded recursion (direct or transitive)
- while loops without @max_iterations(N)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


def _check_with_profile(source: str, profile: str):
    prev = os.environ.get("FLOW_PROFILE")
    os.environ["FLOW_PROFILE"] = profile
    try:
        tc = TypeChecker()
        return tc.check(parse_flow_code(source))
    finally:
        if prev is None:
            os.environ.pop("FLOW_PROFILE", None)
        else:
            os.environ["FLOW_PROFILE"] = prev


# --- Recursion detection (MISRA 17.2) ---

def test_direct_recursion_rejected():
    result = _check_with_profile(
        """
        function boom(n: i32) -> i32 {
            if n <= 0 { return 0 }
            return boom(n - 1)
        }
        function main() -> i32 { return boom(3) }
        """,
        "safety",
    )
    assert any("recursion" in e and "boom" in e for e in result.errors)


def test_mutual_recursion_rejected():
    result = _check_with_profile(
        """
        function is_even(n: i32) -> i32 {
            if n == 0 { return 1 }
            return is_odd(n - 1)
        }
        function is_odd(n: i32) -> i32 {
            if n == 0 { return 0 }
            return is_even(n - 1)
        }
        function main() -> i32 { return is_even(4) }
        """,
        "safety",
    )
    assert any("recursion" in e and "is_even" in e for e in result.errors)
    assert any("recursion" in e and "is_odd" in e for e in result.errors)


def test_no_recursion_passes():
    result = _check_with_profile(
        """
        function add(a: i32, b: i32) -> i32 { return a + b }
        function main() -> i32 { return add(1, 2) }
        """,
        "safety",
    )
    assert not any("recursion" in e for e in result.errors)


def test_recursion_allowed_under_default_profile():
    result = _check_with_profile(
        """
        function boom(n: i32) -> i32 {
            if n <= 0 { return 0 }
            return boom(n - 1)
        }
        function main() -> i32 { return boom(3) }
        """,
        "default",
    )
    assert not any("recursion" in e for e in result.errors)


# --- Loop bound detection (MISRA 17.4) ---

def test_unbounded_while_rejected():
    result = _check_with_profile(
        """
        function main() -> i32 {
            let mut i: i32 = 0
            while i < 10 {
                i = i + 1
            }
            return i
        }
        """,
        "safety",
    )
    assert any("while" in e and "17.4" in e for e in result.errors)


def test_bounded_while_with_max_iterations_passes():
    result = _check_with_profile(
        """
        function main() -> i32 {
            let mut i: i32 = 0
            @max_iterations(100)
            while i < 10 {
                i = i + 1
            }
            return i
        }
        """,
        "safety",
    )
    assert not any("17.4" in e for e in result.errors)


def test_counted_for_loop_passes():
    result = _check_with_profile(
        """
        function main() -> i32 {
            let mut sum: i32 = 0
            for i in 0 to 10 {
                sum = sum + i
            }
            return sum
        }
        """,
        "safety",
    )
    assert not any("17.4" in e for e in result.errors)


def test_while_allowed_under_default_profile():
    result = _check_with_profile(
        """
        function main() -> i32 {
            let mut i: i32 = 0
            while i < 10 {
                i = i + 1
            }
            return i
        }
        """,
        "default",
    )
    assert not any("17.4" in e for e in result.errors)
