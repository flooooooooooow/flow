"""Regression tests for the parser nesting-depth guard (flow-fuzz-deep-expr-recursion).

A fuzzer-found crash: ~70 nested parens exhausted Python's recursion limit
(each parenthesized expression level costs ~13.5 interpreter frames in the
recursive-descent precedence chain). The parser now tracks combined
expression/statement nesting depth and rejects pathologically deep input
with a clean FlowSyntaxError instead of a RecursionError.
"""

import pytest

from flow.parser import FlowSyntaxError, Parser, parse_flow_code


LIMIT = Parser.MAX_NESTING_DEPTH
DEEP = LIMIT + 10


def _expr_prog(expr: str) -> str:
    return f"function f() -> i32 {{\n    return {expr}\n}}\n"


DEEP_PROGRAMS = [
    ("nested parens", _expr_prog("(" * DEEP + "1" + ")" * DEEP)),
    ("nested brackets", _expr_prog("[" * DEEP + "1" + "]" * DEEP)),
    ("unary chain", _expr_prog("-" * (DEEP * 20) + "1")),
    ("unbalanced open parens", _expr_prog("(" * 1000 + "1")),
    (
        "nested if statements",
        "function f() -> i32 {\n"
        + "if 1 {\n" * DEEP
        + "return 0\n"
        + "}\n" * DEEP
        + "}\n",
    ),
]


@pytest.mark.parametrize(
    "src", [s for _, s in DEEP_PROGRAMS], ids=[i for i, _ in DEEP_PROGRAMS]
)
def test_deep_nesting_is_clean_syntax_error(src):
    with pytest.raises(FlowSyntaxError) as ei:
        parse_flow_code(src)
    err = ei.value
    assert "nesting too deep" in str(err)
    assert err.line is not None and err.line >= 1
    assert err.column is not None and err.column >= 1


def test_very_deep_input_never_raises_recursion_error():
    src = _expr_prog("(" * 5000 + "1" + ")" * 5000)
    with pytest.raises(SyntaxError):  # and specifically NOT RecursionError
        parse_flow_code(src)


def test_reasonable_nesting_still_parses():
    depth = 20
    parse_flow_code(_expr_prog("(" * depth + "1" + ")" * depth))
    parse_flow_code(
        "function f(a: i32) -> i32 {\n"
        + "if a > 0 {\n" * 10
        + "return 1\n"
        + "}\n" * 10
        + "return ((a + 1) * (a - 1)) / -a\n}\n"
    )


def test_depth_counter_resets_between_sibling_expressions():
    # Many sequential (non-nested) statements/expressions must not accumulate
    # depth: the guard tracks nesting, not totals.
    lines = ["function f() -> i32 {"]
    for i in range(200):
        lines.append(f"    let v{i}: i32 = ((({i} + 1)))")
    lines.append("    return 0")
    lines.append("}")
    parse_flow_code("\n".join(lines))
