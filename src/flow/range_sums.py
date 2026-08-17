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
    IfExpression,
    Literal,
    RangeExpression,
    Type,
    UnaryOperation,
)


def _i32(value: int) -> Literal:
    return Literal(str(value), Type("i32"))


def _bin(left, operator: str, right):
    return BinaryOperation(left, operator, right)


def _count_positive(rng: RangeExpression):
    # ceil((end - start) / step), valid in the positive-direction branch.
    distance = _bin(rng.end, "-", rng.start)
    numerator = _bin(_bin(distance, "+", rng.step), "-", _i32(1))
    return _bin(numerator, "/", rng.step)


def _count_negative(rng: RangeExpression):
    # ceil((start - end) / abs(step)), valid in the negative-direction branch.
    magnitude = UnaryOperation("-", rng.step)
    distance = _bin(rng.start, "-", rng.end)
    numerator = _bin(_bin(distance, "+", magnitude), "-", _i32(1))
    return _bin(numerator, "/", magnitude)


def _sum_for_count(rng: RangeExpression, count):
    # n * (2*start + (n-1)*step) / 2
    doubled_start = _bin(_i32(2), "*", rng.start)
    tail_offset = _bin(_bin(count, "-", _i32(1)), "*", rng.step)
    endpoints = _bin(doubled_start, "+", tail_offset)
    return _bin(_bin(count, "*", endpoints), "/", _i32(2))


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
    """Lower an exclusive-end arithmetic range sum to O(1) arithmetic.

    Literal ranges fold immediately to a single literal. Runtime positive and
    negative steps preserve ``for`` range semantics. A literal zero step is
    rejected at compile time; a runtime zero step evaluates to zero rather
    than introducing a divide-by-zero path.
    """

    constant = _constant_range_sum(rng)
    if constant is not None:
        return constant

    zero = _i32(0)
    positive_count = _count_positive(rng)
    negative_count = _count_negative(rng)
    positive_sum = _sum_for_count(rng, positive_count)
    negative_sum = _sum_for_count(rng, negative_count)

    positive_direction = _bin(
        _bin(rng.step, ">", zero),
        "&&",
        _bin(rng.start, "<", rng.end),
    )
    negative_direction = _bin(
        _bin(rng.step, "<", zero),
        "&&",
        _bin(rng.start, ">", rng.end),
    )

    return IfExpression(
        positive_direction,
        positive_sum,
        IfExpression(negative_direction, negative_sum, zero),
    )
