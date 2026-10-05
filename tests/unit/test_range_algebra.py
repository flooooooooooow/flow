"""Range algebra folds to the same value the set itself sums to.

The closed forms in `range_sums` are easy to get subtly wrong (CRT offsets,
descending ranges, empty intersections), so these tests build the actual
element sets and compare, rather than asserting hand-computed constants.
"""

import itertools
import random

import pytest

from flow.parser import FlowSyntaxError, FunctionCall, Literal, parse_flow_code
from flow.range_sums import _union_sum, _union_terms


def elements(start, end, step):
    if step > 0:
        return set(range(start, end, step))
    return set(range(start, end, step))


def folded(source):
    """Parse `sum(<source>)` and return the folded literal, or None."""
    decls = parse_flow_code(f"function f() -> i32 {{ return sum({source}) }}")
    value = decls[0].body.statements[0].value
    return int(value.value) if isinstance(value, Literal) else None


def spelling(start, end, step):
    return f"{start}..{end} step {step}"


RANGES = [
    (0, 20, 3),
    (0, 20, 2),
    (1, 30, 4),
    (5, 5, 1),
    (7, 40, 6),
    (0, 1000, 3),
    (0, 1000, 5),
    (20, 0, -3),
    (19, -1, -2),
    (3, 3, 7),
]


@pytest.mark.parametrize("a,b", list(itertools.combinations(RANGES, 2)))
def test_union_and_intersection_match_the_actual_sets(a, b):
    set_a, set_b = elements(*a), elements(*b)
    assert folded(f"{spelling(*a)} | {spelling(*b)}") == sum(set_a | set_b)
    assert folded(f"{spelling(*a)} & {spelling(*b)}") == sum(set_a & set_b)


def test_intersection_binds_tighter_than_union():
    a, b, c = (0, 30, 2), (0, 30, 3), (0, 30, 5)
    got = folded(f"{spelling(*a)} | {spelling(*b)} & {spelling(*c)}")
    assert got == sum(elements(*a) | (elements(*b) & elements(*c)))


def test_three_way_union_uses_full_inclusion_exclusion():
    a, b, c = (0, 100, 3), (0, 100, 5), (0, 100, 7)
    got = folded(f"{spelling(*a)} | {spelling(*b)} | {spelling(*c)}")
    assert got == sum(elements(*a) | elements(*b) | elements(*c))


def test_randomized_two_range_algebra():
    rng = random.Random(20476)
    for _ in range(400):
        def pick():
            start = rng.randint(-15, 15)
            step = rng.choice([s for s in range(-9, 10) if s != 0])
            end = start + rng.randint(-40, 40)
            return (start, end, step)

        a, b = pick(), pick()
        set_a, set_b = elements(*a), elements(*b)
        assert folded(f"{spelling(*a)} | {spelling(*b)}") == sum(set_a | set_b), (a, b)
        assert folded(f"{spelling(*a)} & {spelling(*b)}") == sum(set_a & set_b), (a, b)


def test_runtime_bounds_lower_to_a_single_helper_call():
    decls = parse_flow_code(
        "function f(n: i32) -> i32 { return sum(0..n step 3 | 0..n step 5) }"
    )
    call = decls[0].body.statements[0].value
    assert isinstance(call, FunctionCall)
    assert call.name == "__flow_sum_range_union"
    # Six bounds, each written once, so each is evaluated once.
    assert len(call.arguments) == 6
    assert any(decl.name == "__flow_sum_range_isect" for decl in decls if hasattr(decl, "name"))


def test_step_still_parses_as_bitwise_or_outside_a_range():
    decls = parse_flow_code("function f(a: i32, b: i32) -> i32 { return a | b }")
    assert decls[0].body.statements[0].value.operator == "|"


def test_range_operator_needs_a_range_on_the_right():
    with pytest.raises(FlowSyntaxError, match="need a range on both sides"):
        parse_flow_code("function f(n: i32) -> i32 { return sum(0..10 step 2 | n) }")


def test_runtime_bounds_reject_deeper_algebra():
    with pytest.raises(FlowSyntaxError, match="combine the sums by hand"):
        parse_flow_code(
            "function f(n: i32) -> i32 "
            "{ return sum(0..n step 2 | 0..n step 3 | 0..n step 5) }"
        )


def test_plain_range_sum_is_unchanged():
    assert folded("0..10") == sum(range(0, 10))
    assert folded("0..1000 step 3") == sum(range(0, 1000, 3))
