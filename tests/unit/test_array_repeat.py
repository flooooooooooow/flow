"""`[value; N]` is N copies of value (#585).

The documentation has presented this as ordinary Flow since the book was
written: `let mut signal: array<f32, 256> = [0.0; 256]`. The parser reported
`Expected TokenType.RBRACKET, got TokenType.SEMICOLON`.
"""

from __future__ import annotations

import pytest

from flow.parser import ArrayLiteral, FlowSyntaxError, Literal, parse_flow_code


def first_initializer(source: str):
    decls = parse_flow_code(source)
    return decls[0].body.statements[0].initializer


def test_a_repeat_expands_to_that_many_elements():
    lit = first_initializer(
        "function main() -> i32 {\n"
        "    let zeros: array<i32, 4> = [0; 4]\n"
        "    return 0\n"
        "}"
    )
    assert isinstance(lit, ArrayLiteral)
    assert len(lit.elements) == 4
    assert all(isinstance(e, Literal) and e.value == "0" for e in lit.elements)


def test_a_float_repeat_keeps_its_type():
    lit = first_initializer(
        "function main() -> i32 {\n"
        "    let s: array<f32, 3> = [0.5; 3]\n"
        "    return 0\n"
        "}"
    )
    assert [e.value for e in lit.elements] == ["0.5"] * 3


def test_a_negative_value_repeats():
    lit = first_initializer(
        "function main() -> i32 {\n"
        "    let s: array<i32, 2> = [-2; 2]\n"
        "    return 0\n"
        "}"
    )
    assert len(lit.elements) == 2


def test_an_ordinary_array_literal_still_parses():
    lit = first_initializer(
        "function main() -> i32 {\n"
        "    let s: array<i32, 3> = [1, 2, 3]\n"
        "    return 0\n"
        "}"
    )
    assert [e.value for e in lit.elements] == ["1", "2", "3"]


def test_a_computed_value_is_refused():
    """The elements are written out, so a call would run once per element."""
    with pytest.raises(FlowSyntaxError, match="must be a literal"):
        parse_flow_code(
            "function compute() -> i32 { return 1 }\n"
            "function main() -> i32 {\n"
            "    let s: array<i32, 4> = [compute(); 4]\n"
            "    return 0\n"
            "}"
        )


def test_a_runtime_length_is_refused():
    with pytest.raises(FlowSyntaxError, match="must be an integer literal"):
        parse_flow_code(
            "function main() -> i32 {\n"
            "    let n: i32 = 4\n"
            "    let s: array<i32, 4> = [0; n]\n"
            "    return 0\n"
            "}"
        )


def test_a_negative_length_says_so():
    with pytest.raises(FlowSyntaxError, match="cannot be negative"):
        parse_flow_code(
            "function main() -> i32 {\n"
            "    let s: array<i32, 4> = [0; -1]\n"
            "    return 0\n"
            "}"
        )


def test_an_absurd_length_is_refused_rather_than_materialized():
    with pytest.raises(FlowSyntaxError, match="limited to"):
        parse_flow_code(
            "function main() -> i32 {\n"
            "    let s: array<i32, 4> = [0; 1000000]\n"
            "    return 0\n"
            "}"
        )
