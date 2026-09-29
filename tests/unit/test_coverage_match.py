"""Coverage tests for advanced match patterns (flow-test-coverage).

Extends tests/unit/test_match_exhaustiveness.py and the
tests/core/test_match_*.flow corpus with interactions those files do not
touch: guards combined with or-patterns, 3-deep nested struct patterns,
string-literal patterns and their strcmp lowering, exhaustiveness
warning message text, and struct patterns mixing literals with bindings.
The C lowering checks are the golden tests/cgen/cov_match_patterns.
"""

from __future__ import annotations

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


def check(source: str):
    return TypeChecker().check(parse_flow_code(source))


class TestGuardOrPatternInteraction:
    def test_guarded_or_pattern_still_warns_without_wildcard(self):
        result = check(
            """
            function f(x: i32) -> i32 {
                match x {
                    1 | 2 | 3 if x == 2 => { return 100 }
                    4 | 5 => { return 200 }
                }
                return -1
            }
            """
        )
        assert result.errors == []
        assert any("Non-exhaustive match" in w for w in result.warnings)

    def test_guarded_or_pattern_with_wildcard_is_quiet(self):
        result = check(
            """
            function f(x: i32) -> i32 {
                match x {
                    1 | 2 | 3 if x == 2 => { return 100 }
                    _ => { return 200 }
                }
                return -1
            }
            """
        )
        assert result.errors == []
        assert result.warnings == []

    def test_bool_or_pattern_covering_both_values_is_exhaustive(self):
        result = check(
            """
            function f(b: bool) -> i32 {
                match b {
                    true | false => { return 1 }
                }
                return -1
            }
            """
        )
        assert result.errors == []
        assert result.warnings == []

class TestExhaustivenessMessageText:
    """The warning text is part of the developer contract: it must name
    what is missing and say how to fix it."""

    def test_integer_warning_names_the_fix(self):
        result = check(
            """
            function f(x: i32) -> i32 {
                match x {
                    0 => { return 0 }
                }
                return -1
            }
            """
        )
        [warning] = [w for w in result.warnings if "Non-exhaustive" in w]
        assert "integer literal patterns" in warning
        assert "add `_` or `default`" in warning

    def test_bool_warning_names_both_values_and_the_fix(self):
        result = check(
            """
            function f(b: bool) -> i32 {
                match b {
                    false => { return 0 }
                }
                return -1
            }
            """
        )
        [warning] = [w for w in result.warnings if "Non-exhaustive" in w]
        assert "bool patterns" in warning
        assert "`true` and `false`" in warning
        assert "`_`/`default`" in warning

    def test_enum_warning_lists_every_missing_variant(self):
        result = check(
            """
            enum Direction {
                North,
                South,
                East,
                West
            }

            function f(d: Direction) -> i32 {
                match d.tag {
                    Direction_North => { return 1 }
                }
                return -1
            }
            """
        )
        [warning] = [w for w in result.warnings if "Non-exhaustive" in w]
        assert "enum 'Direction'" in warning
        # All three missing variants are named; the covered one is not.
        for variant in ("South", "East", "West"):
            assert variant in warning
        assert "North" not in warning.split("cover")[1]
        assert "add the missing variant(s)" in warning


class TestStringLiteralPatterns:
    STRING_MATCH = """
    function classify(s: string) -> i32 {
        match s {
            "on" => { return 1 }
            "off" => { return 0 }
            _ => { return -1 }
        }
        return -1
    }
    function main() -> i32 { return classify("on") - 1 }
    """

    def test_string_match_type_checks_clean(self):
        result = check(self.STRING_MATCH)
        assert result.errors == []

    def test_string_match_has_no_exhaustiveness_tier(self):
        # Strings are outside the documented three tiers (enum, bool,
        # integer literal), so a match without a wildcard must not warn.
        result = check(
            """
            function f(s: string) -> i32 {
                match s {
                    "a" => { return 1 }
                }
                return -1
            }
            """
        )
        assert result.errors == []
        assert result.warnings == []


class TestDeepNestedStructPatterns:
    THREE_DEEP = """
    struct Leaf { v: i32, }
    struct Mid { leaf: Leaf, m: i32, }
    struct Top { mid: Mid, t: i32, }

    function f(x: Top) -> i32 {
        match x {
            Top(Mid(Leaf(0), m), t) => { return 1 }
            Top(Mid(Leaf(v), 0), t) => { return 2 }
            Top(Mid(Leaf(v), m), t) if v > t => { return 3 }
            _ => { return 4 }
        }
        return -1
    }

    function main() -> i32 {
        let x: Top = Top { mid: Mid { leaf: Leaf { v: 0 }, m: 1 }, t: 2 }
        return f(x) - 1
    }
    """

    def test_three_deep_pattern_type_checks_clean(self):
        result = check(self.THREE_DEEP)
        assert result.errors == []

    def test_literal_and_binding_mix_binds_only_named_fields(self):
        result = check(
            """
            struct Pair { a: i32, b: i32, }
            function f(p: Pair) -> i32 {
                match p {
                    Pair(0, b) => { return b }
                    Pair(a, 0) => { return a }
                    Pair(a, b) => { return a + b }
                }
                return -1
            }
            function main() -> i32 {
                let p: Pair = Pair { a: 0, b: 7 }
                return f(p) - 7
            }
            """
        )
        assert result.errors == []
