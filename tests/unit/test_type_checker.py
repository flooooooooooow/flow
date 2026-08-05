"""Type-checker matrix — C-compiler-grade semantic regressions.

Tests pin current rejection behavior. Gaps that *should* reject but do not
yet are marked xfail so they fail loudly when fixed (then drop the mark).
"""

import pytest

from tests.unit.compiler_helpers import errors, typecheck, warnings


# ---------------------------------------------------------------------------
# Currently enforced
# ---------------------------------------------------------------------------


def test_undeclared_variable_rejected():
    errs = errors("function main() -> i32 { return x }")
    assert any("Undefined variable 'x'" in e for e in errs), errs


def test_call_arity_mismatch_rejected():
    errs = errors(
        """
function add(a: i32, b: i32) -> i32 { return a + b }
function main() -> i32 { return add(1) }
"""
    )
    assert any("No matching overload" in e and "add" in e for e in errs), errs


def test_call_argument_type_mismatch_rejected():
    errs = errors(
        """
function add(a: i32, b: i32) -> i32 { return a + b }
function main() -> i32 { return add(1, true) }
"""
    )
    assert any("No matching overload" in e for e in errs), errs


def test_unknown_struct_field_rejected():
    errs = errors(
        """
struct Point { x: i32, y: i32 }
function main() -> i32 {
    let p: Point = Point { x: 1, y: 2 }
    return p.z
}
"""
    )
    assert any("Field 'z'" in e for e in errs), errs


def test_duplicate_struct_rejected():
    errs = errors(
        """
struct A { x: i32 }
struct A { y: i32 }
function main() -> i32 { return 0 }
"""
    )
    assert any("already defined" in e for e in errs), errs


def test_return_type_void_vs_value_rejected():
    errs = errors(
        """
function f() -> void { return 1 }
function main() -> i32 { return 0 }
"""
    )
    assert any("should return void" in e for e in errs), errs


def test_unknown_function_rejected():
    errs = errors("function main() -> i32 { return nope(1) }")
    assert any(
        "Undefined" in e or "Unknown" in e or "No matching" in e or "nope" in e.lower()
        for e in errs
    ), errs


def test_valid_program_has_no_errors():
    result = typecheck(
        """
struct Point { x: i32, y: i32 }
function add(a: i32, b: i32) -> i32 { return a + b }
function main() -> i32 {
    let p: Point = Point { x: 1, y: 2 }
    return add(p.x, p.y) - 3
}
"""
    )
    assert result.errors == []


def test_lenient_vs_strict_unknown_type_annotation():
    src = """
function main() -> i32 {
    let p: Nope = Nope { x: 1 }
    return 0
}
"""
    strict_errs = errors(src, strict=True)
    lenient_errs = errors(src, strict=False)
    assert strict_errs, "strict should reject unknown type annotations"
    # Lenient may soft-accept; pin the difference so we notice if it flips.
    assert len(strict_errs) >= len(lenient_errs)


# ---------------------------------------------------------------------------
# Strict-mode hardening (lenient still soft-accepts for corpus migration)
# ---------------------------------------------------------------------------


def test_assignment_type_mismatch_rejected_strict():
    errs = errors(
        """
function main() -> i32 {
    let x: i32 = true
    return 0
}
"""
    )
    assert errs, "expected type error for i32 = bool"
    assert not errors(
        """
function main() -> i32 {
    let x: i32 = true
    return 0
}
""",
        strict=False,
    ), "lenient should still allow bool→i32"


def test_immutable_reassign_rejected_strict():
    errs = errors(
        """
function main() -> i32 {
    let x: i32 = 1
    x = 2
    return x
}
"""
    )
    assert any("immutable" in e for e in errs), errs
    # let mut is fine
    assert (
        errors(
            """
function main() -> i32 {
    let mut x: i32 = 1
    x = 2
    return x - 2
}
"""
        )
        == []
    )


def test_if_condition_non_bool_rejected_strict():
    errs = errors(
        """
function main() -> i32 {
    if 1 {
        return 0
    }
    return 1
}
"""
    )
    assert any("must be bool" in e for e in errs), errs
    assert not errors(
        """
function main() -> i32 {
    if 1 {
        return 0
    }
    return 1
}
""",
        strict=False,
    )


def test_return_type_mismatch_rejected_strict():
    errs = errors("function main() -> i32 { return true }")
    assert errs, "expected error returning bool from i32 function"
