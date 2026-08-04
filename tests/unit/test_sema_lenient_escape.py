"""Lenient mode remains a migration escape hatch for legacy soft rules."""

from tests.unit.compiler_helpers import errors


def test_lenient_allows_immutable_reassign():
    src = """
function main() -> i32 {
    let x: i32 = 1
    x = 2
    return x - 2
}
"""
    assert errors(src, strict=True)
    assert errors(src, strict=False) == []


def test_lenient_allows_numeric_if():
    src = """
function main() -> i32 {
    if 1 {
        return 0
    }
    return 1
}
"""
    assert errors(src, strict=True)
    assert errors(src, strict=False) == []


def test_lenient_allows_bool_to_i32_init():
    src = """
function main() -> i32 {
    let x: i32 = true
    return x - 1
}
"""
    assert errors(src, strict=True)
    assert errors(src, strict=False) == []
