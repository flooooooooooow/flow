"""Known bugs found while expanding coverage (flow-test-coverage).

Each test asserts the CORRECT behavior and is marked strict xfail, so it
starts failing loudly the moment the bug is fixed and the mark should be
removed.
"""

import pytest

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


def check(source: str):
    return TypeChecker().check(parse_flow_code(source))


EFFECT_PRELUDE = """
effect Scale {
    apply(x: i32) -> i32,
}

capability Doubler {
    effect Scale,
    function apply(x: i32) -> i32 {
        return x * 2
    },
}
"""


@pytest.mark.xfail(
    reason=(
        "Guarded bool literal arms count as coverage in the bool "
        "exhaustiveness tier: `true if g => ...` plus `false => ...` "
        "produces no warning, although the guard may fail at runtime and "
        "leave `true` unmatched. The enum tier already excludes guarded "
        "arms from coverage (see test_enum_match_guarded_arm_does_not_"
        "count_as_covered); the bool tier in _warn_match_exhaustiveness_"
        "stub updates covered_bools without consulting case.guard."
    ),
    strict=True,
)
def test_guarded_bool_arm_should_not_count_as_coverage():
    result = check(
        """
        function f(b: bool) -> i32 {
            match b {
                true if 1 == 2 => { return 1 }
                false => { return 0 }
            }
            return -1
        }
        """
    )
    assert result.errors == []
    # Correct behavior: the guarded `true` arm does not guarantee
    # coverage, so this match is non-exhaustive and must warn.
    assert any("do not cover both" in w for w in result.warnings)


@pytest.mark.xfail(
    reason=(
        "The type checker rejects effect-operation calls lexically outside "
        "a handle block: `Scale.apply(1)` at function top level errors with "
        "\"Undefined function 'apply'\" (and a follow-on void-assignment "
        "error), although the C generator fully supports such calls via "
        "dynamic vtable dispatch with a default return - the zero-cost "
        "substitution feature's own codegen tests exercise exactly this "
        "(test_dynamic_dispatch_outside_handle_block). Lenient mode "
        "compiles and runs the same program fine."
    ),
    strict=True,
)
def test_effect_call_outside_handle_block_should_type_check():
    result = check(
        EFFECT_PRELUDE
        + """
        function main() -> i32 {
            let a: i32 = Scale.apply(1)
            return 0
        }
        """
    )
    assert result.errors == []


def test_unhandled_effect_call_inside_any_handle_block_is_accepted():
    """Companion to the xfail above, asserting CURRENT behavior so a fix
    that changes it is noticed: a call to an effect that is NOT handled
    anywhere is accepted by the checker as long as it sits lexically
    inside a handle block for a DIFFERENT effect. Whichever way the
    outside-block rule is resolved, these two behaviors should end up
    consistent with each other.
    """
    result = check(
        EFFECT_PRELUDE
        + """
        effect Offset {
            shift(x: i32) -> i32,
        }

        function main() -> i32 {
            handle Scale with Doubler {
                let b: i32 = Offset.shift(1)
            }
            return 0
        }
        """
    )
    assert result.errors == []
