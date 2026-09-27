"""If-expressions: `let x = if cond { a } else { b }` (#252)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code, IfExpression
from flow.c_generator import flow_to_c


def test_parse_if_expression():
    decls = parse_flow_code(
        """
function main() -> i32 {
    let x: i32 = if 1 == 1 { 3 } else { 4 }
    return x
}
"""
    )
    main = decls[0]
    body = main.body.statements
    assign = body[0]
    assert isinstance(assign.initializer, IfExpression)
    assert assign.initializer.then_expr.value == "3"
    assert assign.initializer.else_expr.value == "4"


def test_if_expression_c_codegen_ternary():
    c = flow_to_c(
        parse_flow_code(
            """
function main() -> i32 {
    let x: i32 = if 1 != 0 { 10 } else { 20 }
    return x
}
"""
        )
    )
    assert "? (" in c or "?(" in c
    assert "10" in c and "20" in c


# test_if_expression_runs -> tests/lang/test_if_expression.flow.
