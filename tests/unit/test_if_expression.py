"""If-expressions: `let x = if cond { a } else { b }` (#252)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code, IfExpression


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


# C lowering -> tests/cgen/if_expression_ternary.
# test_if_expression_runs -> tests/lang/test_if_expression.flow.
