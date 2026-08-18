"""Closed-form lowering for arithmetic range sums.

The parser recognizes range syntax inside ``sum(...)`` and hands the resulting
``RangeExpression`` to this module. The range is immediately rewritten into
ordinary Flow AST nodes, so type checking and every backend see only existing
arithmetic/comparison/if-expression constructs.
"""

from __future__ import annotations

from .parser import (
    BinaryOperation,
    FlowSyntaxError,
    FunctionCall,
    Literal,
    RangeExpression,
    Type,
)


def _i32(value: int) -> Literal:
    return Literal(str(value), Type("i32"))


def _bin(left, operator: str, right):
    return BinaryOperation(left, operator, right)


HELPER_NAME = "__flow_sum_range"

# Lowered once per module rather than inlined at each call site. Inlining meant
# the bounds appeared many times in the generated expression and were therefore
# evaluated many times: for `sum(a_start(0)..an_end(1000) step a_step(3))` the
# three calls ran 5, 4 and 11 times. A `for` loop over the same range evaluates
# each bound once, and so does this.
#
# Having a body also means the count can go in a local, so the parity split
# that keeps the arithmetic inside i32 costs one branch instead of duplicating
# the whole expression.
HELPER_SOURCE = """
function __flow_sum_range(start: i32, limit: i32, step: i32) -> i32 {
    if step == 0 {
        return 0
    }
    let mut count: i32 = 0
    if step > 0 {
        if start >= limit {
            return 0
        }
        count = (limit - start + step - 1) / step
    } else {
        if start <= limit {
            return 0
        }
        count = (start - limit + (0 - step) - 1) / (0 - step)
    }
    let endpoints: i32 = 2 * start + (count - 1) * step
    if count % 2 == 0 {
        return (count / 2) * endpoints
    }
    return count * (endpoints / 2)
}
"""


def helper_declarations():
    """Parse the helper into declarations the module can carry.

    Parsed from source rather than assembled node by node: the body is the
    clearest statement of the identity, and it stays readable next to the
    comment explaining why the arithmetic is arranged the way it is.
    """
    from .parser import parse_flow_code

    return parse_flow_code(HELPER_SOURCE)


def _literal_int(expr) -> int | None:
    if not isinstance(expr, Literal):
        return None
    if getattr(expr.type, "name", None) not in (
        "i8", "u8", "i16", "u16", "i32", "u32", "i64", "u64"
    ):
        return None
    try:
        return int(str(expr.value), 0)
    except (TypeError, ValueError):
        return None


def _constant_range_sum(rng: RangeExpression) -> Literal | None:
    start = _literal_int(rng.start)
    end = _literal_int(rng.end)
    step = _literal_int(rng.step)
    if start is None or end is None or step is None:
        return None
    if step == 0:
        raise FlowSyntaxError("sum(range) step must not be zero")

    if (step > 0 and start >= end) or (step < 0 and start <= end):
        total = 0
    elif step > 0:
        count = (end - start + step - 1) // step
        total = count * (2 * start + (count - 1) * step) // 2
    else:
        magnitude = -step
        count = (start - end + magnitude - 1) // magnitude
        total = count * (2 * start + (count - 1) * step) // 2

    result_type = getattr(rng.start, "type", None) or Type("i32")
    return Literal(str(total), result_type)


def lower_range_sum(rng: RangeExpression):
    """Lower an exclusive-end arithmetic range sum.

    A range whose bounds are all literals folds to one literal at parse time.
    Anything else becomes a call to the helper above, so the bounds are
    evaluated exactly once and the arithmetic stays O(1).
    """
    constant = _constant_range_sum(rng)
    if constant is not None:
        return constant
    return FunctionCall(HELPER_NAME, [rng.start, rng.end, rng.step])
