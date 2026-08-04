"""Unit tests for the match exhaustiveness warning stub."""

from __future__ import annotations

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


def _check(source: str):
    decls = parse_flow_code(source)
    return TypeChecker().check(decls)


def test_non_exhaustive_integer_literals_warn():
    result = _check(
        """
        function f(x: i32) -> i32 {
            match x {
                0 => { return 0 }
                1 => { return 1 }
            }
            return -1
        }
        """
    )
    assert result.errors == []
    assert any("Non-exhaustive match" in w for w in result.warnings)


def test_wildcard_arm_suppresses_warning():
    result = _check(
        """
        function f(x: i32) -> i32 {
            match x {
                0 => { return 0 }
                _ => { return 1 }
            }
            return -1
        }
        """
    )
    assert result.errors == []
    assert not any("Non-exhaustive match" in w for w in result.warnings)


def test_default_case_suppresses_warning():
    result = _check(
        """
        function f(x: i32) -> i32 {
            match x {
                0 => { return 0 }
                default {
                    return 1
                }
            }
            return -1
        }
        """
    )
    assert result.errors == []
    assert not any("Non-exhaustive match" in w for w in result.warnings)


def test_or_pattern_integer_literals_warn():
    result = _check(
        """
        function f(x: i32) -> i32 {
            match x {
                1 | 2 | 3 => { return 1 }
            }
            return -1
        }
        """
    )
    assert result.errors == []
    assert any("Non-exhaustive match" in w for w in result.warnings)


def test_integer_gap_inside_span_is_reported():
    result = _check(
        """
        function f(x: i32) -> i32 {
            match x {
                0 | 1 | 3 => { return 1 }
            }
            return -1
        }
        """
    )
    assert result.errors == []
    joined = " | ".join(result.warnings)
    assert "gaps in [0, 3]" in joined
    assert "2" in joined


def test_integer_contiguous_span_still_warns_outside():
    result = _check(
        """
        function f(x: i32) -> i32 {
            match x {
                0 => { return 0 }
                1 => { return 1 }
                2 => { return 2 }
            }
            return -1
        }
        """
    )
    assert result.errors == []
    joined = " | ".join(result.warnings)
    assert "contiguous cover [0, 2]" in joined
    assert "outside that span" in joined


def test_guarded_integer_arm_does_not_cover():
    result = _check(
        """
        function f(x: i32) -> i32 {
            match x {
                0 if x >= 0 => { return 0 }
                1 => { return 1 }
            }
            return -1
        }
        """
    )
    assert result.errors == []
    # Only unguarded `1` counts; still non-exhaustive (and 0 is a gap if
    # another unguarded value expands the span — here span is just {1}).
    assert any("Non-exhaustive match" in w for w in result.warnings)


def test_bool_match_missing_false_warns():
    result = _check(
        """
        function f(b: bool) -> i32 {
            match b {
                true => { return 1 }
            }
            return -1
        }
        """
    )
    assert result.errors == []
    assert any("do not cover both" in w for w in result.warnings)


def test_bool_match_both_values_is_exhaustive():
    # Unlike integers, bool has exactly two inhabitants - covering both
    # `true` and `false` is genuinely exhaustive, even without a wildcard.
    result = _check(
        """
        function f(b: bool) -> i32 {
            match b {
                true => { return 1 }
                false => { return 0 }
            }
            return -1
        }
        """
    )
    assert result.errors == []
    assert result.warnings == []


_ENUM_SRC = """
enum Color {
    Red,
    Green,
    Blue
}

function classify(c: Color) -> i32 {
    match c.tag {
        %s
    }
    return -1
}
"""


def test_enum_match_missing_variant_warns():
    result = _check(
        _ENUM_SRC % """
        Color_Red => { return 1 }
        Color_Green => { return 2 }
        """
    )
    assert result.errors == []
    assert any(
        "Non-exhaustive match: enum 'Color'" in w and "Blue" in w
        for w in result.warnings
    )


def test_enum_match_all_variants_is_exhaustive():
    result = _check(
        _ENUM_SRC % """
        Color_Red => { return 1 }
        Color_Green => { return 2 }
        Color_Blue => { return 3 }
        """
    )
    assert result.errors == []
    assert result.warnings == []


def test_enum_match_wildcard_suppresses_warning():
    result = _check(
        _ENUM_SRC % """
        Color_Red => { return 1 }
        _ => { return -1 }
        """
    )
    assert result.errors == []
    assert not any("Non-exhaustive match" in w for w in result.warnings)


def test_enum_match_default_case_suppresses_warning():
    result = _check(
        """
        enum Color {
            Red,
            Green,
            Blue
        }

        function classify(c: Color) -> i32 {
            match c.tag {
                Color_Red => { return 1 }
                default {
                    return -1
                }
            }
            return -1
        }
        """
    )
    assert result.errors == []
    assert not any("Non-exhaustive match" in w for w in result.warnings)


def test_enum_match_directly_on_value_checks_variants():
    # Matching on the enum value itself (not just `.tag`) should also be
    # checked for exhaustiveness, using the same path/const patterns.
    result = _check(
        """
        enum Option_i32 {
            Some(i32),
            None
        }

        function is_some(opt: Option_i32) -> bool {
            match opt {
                Option_i32_Some => { return true }
            }
            return false
        }
        """
    )
    assert result.errors == []
    assert any(
        "Non-exhaustive match: enum 'Option_i32'" in w and "None" in w
        for w in result.warnings
    )


def test_enum_match_guarded_arm_does_not_count_as_covered():
    # A guarded arm may not actually fire for that variant, so it shouldn't
    # count towards exhaustiveness on its own.
    result = _check(
        _ENUM_SRC % """
        Color_Red if 1 == 2 => { return 1 }
        Color_Green => { return 2 }
        Color_Blue => { return 3 }
        """
    )
    assert result.errors == []
    assert any(
        "Non-exhaustive match: enum 'Color'" in w and "Red" in w
        for w in result.warnings
    )


def test_enum_match_unrelated_binding_pattern_does_not_false_positive():
    # A plain identifier binding mixed in with variant patterns means we
    # can't attribute coverage reliably - don't guess, don't warn.
    result = _check(
        _ENUM_SRC % """
        Color_Red => { return 1 }
        other => { return other }
        """
    )
    assert result.errors == []
    assert not any("Non-exhaustive match" in w for w in result.warnings)
