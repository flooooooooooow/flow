"""`span.data` is emitted by the C generator, so the type checker must know it.

Every FFI call needs the data pointer, and the checker rejected the field
while the generator happily emitted it. Strict checking and `flow explain`
were therefore unusable on any module that talks to C, which for numerical
work is all of them. See issue #628.
"""

from __future__ import annotations

from flow.parser import Lexer, Parser
from flow.type_checker import TypeChecker

SOURCE = """
extern {
    function malloc(size: i64) -> ptr<void>
    function printf(fmt: string, a: f64) -> i32
}

function main() -> i32 {
    let raw: ptr<f64> = malloc(24)
    let view: span<mut f64> = raw[0..3]
    view[0] = 7.0
    let back: ptr<f64> = view.data
    printf("%.1f\\n", back[0])
    return 0
}
"""


def check(source: str) -> list:
    checker = TypeChecker()
    assert checker.strict, "these assertions only mean something under strict"
    return checker.check(Parser(Lexer(source)).parse()).errors


def test_span_data_is_a_pointer_to_the_element_type():
    assert check(SOURCE) == []


def test_an_unknown_span_field_is_still_rejected():
    source = SOURCE.replace("view.data", "view.capacity")
    errors = check(source)
    assert any("capacity" in e for e in errors), errors
