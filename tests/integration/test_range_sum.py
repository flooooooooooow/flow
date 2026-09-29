"""Parser folding of `sum(range)`.

The closed-form C lowering is checked in tests/cgen/range_sum_closed_form and
the values in tests/lang/test_range_sum_step.flow.
"""

from __future__ import annotations

import pytest

from flow.parser import FlowSyntaxError, Literal, ReturnStatement, parse_flow_code


def test_literal_sum_range_folds_during_parsing() -> None:
    declarations = parse_flow_code(
        """
function folded() -> i32 {
    return sum(0..1000 step 3)
}
"""
    )
    return_statement = declarations[0].body.statements[0]
    assert isinstance(return_statement, ReturnStatement)
    assert isinstance(return_statement.value, Literal)
    assert return_statement.value.value == "166833"


def test_sum_range_rejects_literal_zero_step() -> None:
    with pytest.raises(FlowSyntaxError, match="step must not be zero"):
        parse_flow_code(
            """
function bad() -> i32 {
    return sum(0..10 step 0)
}
"""
        )
