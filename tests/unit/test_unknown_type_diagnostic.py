"""An undeclared type name is reported as undeclared, not as a self-mismatch.

A SemanticType renders by its name, so an undeclared `Point` annotation and a
`Point` struct literal produced "initialized with Point but annotated as Point":
a message describing a type as failing to match itself. Found by running the
documentation examples, where six blocks failed this way.
"""

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


def check(source: str):
    checker = TypeChecker()
    checker.strict = True
    return checker.check(parse_flow_code(source))


def test_undeclared_annotation_names_the_type():
    errors = check(
        "function main() -> i32 {\n"
        "    let p: Point = Point { x: 3, y: 4 }\n"
        "    return 0\n"
        "}"
    ).errors
    assert any("unknown type 'Point'" in e for e in errors), errors
    assert not any("annotated as Point" in e for e in errors), errors


def test_undeclared_return_type_names_the_type():
    errors = check("function f() -> Widget { return 5 }").errors
    assert any("unknown type 'Widget'" in e for e in errors), errors
    assert not any("should return Widget" in e for e in errors), errors


def test_a_real_mismatch_still_reads_as_a_mismatch():
    """Both types declared, so the original wording is the right one."""
    errors = check("struct P { x: i32 }\nfunction f() -> P { return 5 }").errors
    assert any("returns i32 but should return P" in e for e in errors), errors


def test_a_real_variable_mismatch_is_unchanged():
    errors = check(
        "function main() -> i32 {\n"
        "    let n: i32 = \"hello\"\n"
        "    return 0\n"
        "}"
    ).errors
    assert any("annotated as i32" in e for e in errors), errors


def test_declared_struct_assigns_cleanly():
    errors = check(
        "struct Point { x: i32, y: i32 }\n"
        "function main() -> i32 {\n"
        "    let p: Point = Point { x: 3, y: 4 }\n"
        "    return 0\n"
        "}"
    ).errors
    assert errors == []
