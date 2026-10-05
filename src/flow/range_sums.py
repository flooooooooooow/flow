"""Closed-form lowering for arithmetic range sums.

The parser recognizes range syntax inside ``sum(...)`` and hands the resulting
``RangeExpression`` (or a ``RangeSetOperation`` tree, for range algebra) to
this module. It is rewritten into ordinary Flow AST nodes immediately, so type
checking and every backend see only existing constructs: a literal when the
bounds are literals, otherwise one call to a generated helper.
"""

from __future__ import annotations

import math

from .parser import (
    FlowSyntaxError,
    FunctionCall,
    Literal,
    RangeExpression,
    RangeSetOperation,
    Type,
    UnaryOperation,
)


HELPER_NAME = "__flow_sum_range"
SUM_HELPER_NAME = HELPER_NAME
UNION_HELPER_NAME = "__flow_sum_range_union"
ISECT_HELPER_NAME = "__flow_sum_range_isect"
SET_HELPER_NAMES = frozenset({UNION_HELPER_NAME, ISECT_HELPER_NAME})

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
    # `-7` is unary minus over a literal, not a negative literal, so a descending
    # range folds only if this unwraps it.
    if isinstance(expr, UnaryOperation) and expr.operator in ("-", "+"):
        inner = _literal_int(expr.operand)
        if inner is None:
            return None
        return -inner if expr.operator == "-" else inner
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
    total = _progression_sum(_normalize(start, end, step))
    result_type = getattr(rng.start, "type", None) or Type("i32")
    return Literal(str(total), result_type)


# --- range algebra -----------------------------------------------------------
#
# A range is an arithmetic progression. The intersection of two progressions is
# itself a progression (or empty), found by CRT: the step is lcm(pa, pb) and the
# first common element comes from a modular inverse. Everything else follows:
#
#     sum(A | B) = sum(A) + sum(B) - sum(A & B)
#
# Unions of more than two ranges use the same identity applied over every
# non-empty subset, which is why the folded path is capped below.

MAX_UNION_TERMS = 8

# Two `&` operands can each be a union, so `(A|B) & C` has to distribute into
# `(A&C) | (B&C)` before inclusion-exclusion applies. `_union_terms` does that
# distribution and returns the progressions whose union the node denotes.
_EMPTY = (0, 0, 1)


def _normalize(start: int, end: int, step: int):
    """Describe a literal range as an ascending (first, count, step)."""
    if step == 0:
        raise FlowSyntaxError("sum(range) step must not be zero")
    if step > 0:
        if start >= end:
            return _EMPTY
        count = (end - start + step - 1) // step
        return (start, count, step)
    magnitude = -step
    if start <= end:
        return _EMPTY
    count = (start - end + magnitude - 1) // magnitude
    return (start + (count - 1) * step, count, magnitude)


def _intersect(a, b):
    first_a, count_a, step_a = a
    first_b, count_b, step_b = b
    if count_a <= 0 or count_b <= 0:
        return _EMPTY

    common = math.gcd(step_a, step_b)
    offset = first_b - first_a
    if offset % common:
        return _EMPTY

    modulus = step_b // common
    step = step_a * modulus
    index = 0
    if modulus > 1:
        inverse = pow((step_a // common) % modulus, -1, modulus)
        index = ((offset // common) % modulus) * inverse % modulus
    value = first_a + index * step_a

    low = max(first_a, first_b)
    high = min(first_a + (count_a - 1) * step_a, first_b + (count_b - 1) * step_b)
    if value < low:
        value += -((value - low) // step) * step
    if value > high:
        return _EMPTY
    return (value, (high - value) // step + 1, step)


def _progression_sum(progression) -> int:
    first, count, step = progression
    if count <= 0:
        return 0
    return count * (2 * first + (count - 1) * step) // 2


def _union_terms(node):
    """Progressions whose union `node` denotes, or None if a bound is not literal."""
    if isinstance(node, RangeExpression):
        start = _literal_int(node.start)
        end = _literal_int(node.end)
        step = _literal_int(node.step)
        if start is None or end is None or step is None:
            return None
        return [_normalize(start, end, step)]

    left = _union_terms(node.left)
    right = _union_terms(node.right)
    if left is None or right is None:
        return None
    if node.operator == "|":
        return left + right
    return [_intersect(a, b) for a in left for b in right]


def _union_sum(terms) -> int:
    """Inclusion-exclusion over the union of a list of progressions."""
    live = [term for term in terms if term[1] > 0]
    if not live:
        return 0
    total = 0
    for mask in range(1, 1 << len(live)):
        combined = None
        for index in range(len(live)):
            if not mask & (1 << index):
                continue
            combined = live[index] if combined is None else _intersect(combined, live[index])
            if combined[1] <= 0:
                break
        sign = -1 if bin(mask).count("1") % 2 == 0 else 1
        total += sign * _progression_sum(combined)
    return total


def _leaf_type(node) -> Type:
    while isinstance(node, RangeSetOperation):
        node = node.left
    return getattr(node.start, "type", None) or Type("i32")


def _set_helper_call(node):
    """Lower a two-range set operation to one call, each bound evaluated once."""
    left, right = node.left, node.right
    if not isinstance(left, RangeExpression) or not isinstance(right, RangeExpression):
        raise FlowSyntaxError(
            "range algebra over more than two ranges needs literal bounds; "
            "with runtime bounds, combine the sums by hand: "
            "sum(A) + sum(B) - sum(A & B)"
        )
    name = UNION_HELPER_NAME if node.operator == "|" else ISECT_HELPER_NAME
    return FunctionCall(
        name,
        [left.start, left.end, left.step, right.start, right.end, right.step],
    )


def lower_range_sum(rng):
    """Lower a range sum, returning the expression and the helpers it needs.

    A tree whose bounds are all literals folds to one literal at parse time,
    however deeply nested. Anything else becomes a single helper call, so each
    bound is evaluated exactly once and the arithmetic stays O(1).
    """
    if isinstance(rng, RangeExpression):
        constant = _constant_range_sum(rng)
        if constant is not None:
            return constant, None
        return FunctionCall(HELPER_NAME, [rng.start, rng.end, rng.step]), "sum"

    terms = _union_terms(rng)
    if terms is not None:
        if len(terms) > MAX_UNION_TERMS:
            raise FlowSyntaxError(
                f"sum(range algebra) is limited to {MAX_UNION_TERMS} ranges; "
                f"this expression has {len(terms)}"
            )
        return Literal(str(_union_sum(terms)), _leaf_type(rng)), None
    return _set_helper_call(rng), "set"


SET_HELPER_SOURCE = """
function __flow_range_gcd(a: i64, b: i64) -> i64 {
    let mut x: i64 = a
    let mut y: i64 = b
    if x < 0 { x = 0 - x }
    if y < 0 { y = 0 - y }
    while y != 0 {
        let t: i64 = x % y
        x = y
        y = t
    }
    return x
}

function __flow_range_modinv(a: i64, m: i64) -> i64 {
    if m <= 1 {
        return 0
    }
    let mut old_r: i64 = a % m
    if old_r < 0 {
        old_r = old_r + m
    }
    let mut r: i64 = m
    let mut old_s: i64 = 1
    let mut s: i64 = 0
    while r != 0 {
        let q: i64 = old_r / r
        let next_r: i64 = old_r - q * r
        old_r = r
        r = next_r
        let next_s: i64 = old_s - q * s
        old_s = s
        s = next_s
    }
    let mut inv: i64 = old_s % m
    if inv < 0 {
        inv = inv + m
    }
    return inv
}

function __flow_range_count(start: i64, limit: i64, stride: i64) -> i64 {
    if stride == 0 {
        return 0
    }
    if stride > 0 {
        if start >= limit {
            return 0
        }
        return (limit - start + stride - 1) / stride
    }
    let up: i64 = 0 - stride
    if start <= limit {
        return 0
    }
    return (start - limit + up - 1) / up
}

function __flow_progression_sum(first: i64, count: i64, stride: i64) -> i64 {
    if count <= 0 {
        return 0
    }
    let endpoints: i64 = 2 * first + (count - 1) * stride
    if count % 2 == 0 {
        return (count / 2) * endpoints
    }
    return count * (endpoints / 2)
}

function __flow_sum_range_isect(sa: i32, ea: i32, pa: i32, sb: i32, eb: i32, pb: i32) -> i32 {
    let count_a: i64 = __flow_range_count(sa as i64, ea as i64, pa as i64)
    let count_b: i64 = __flow_range_count(sb as i64, eb as i64, pb as i64)
    if count_a <= 0 {
        return 0
    }
    if count_b <= 0 {
        return 0
    }

    let mut first_a: i64 = sa as i64
    let mut step_a: i64 = pa as i64
    if step_a < 0 {
        first_a = first_a + (count_a - 1) * step_a
        step_a = 0 - step_a
    }
    let mut first_b: i64 = sb as i64
    let mut step_b: i64 = pb as i64
    if step_b < 0 {
        first_b = first_b + (count_b - 1) * step_b
        step_b = 0 - step_b
    }

    let common: i64 = __flow_range_gcd(step_a, step_b)
    let offset: i64 = first_b - first_a
    if offset % common != 0 {
        return 0
    }

    let modulus: i64 = step_b / common
    let step: i64 = step_a * modulus
    let mut index: i64 = 0
    if modulus > 1 {
        let inverse: i64 = __flow_range_modinv((step_a / common) % modulus, modulus)
        let mut scaled: i64 = (offset / common) % modulus
        if scaled < 0 {
            scaled = scaled + modulus
        }
        index = (scaled * inverse) % modulus
    }
    let mut value: i64 = first_a + index * step_a

    let mut low: i64 = first_a
    if first_b > low {
        low = first_b
    }
    let mut high: i64 = first_a + (count_a - 1) * step_a
    let last_b: i64 = first_b + (count_b - 1) * step_b
    if last_b < high {
        high = last_b
    }

    if value < low {
        let gap: i64 = low - value
        value = value + ((gap + step - 1) / step) * step
    }
    if value > high {
        return 0
    }

    let count: i64 = (high - value) / step + 1
    return __flow_progression_sum(value, count, step) as i32
}

function __flow_sum_range_union(sa: i32, ea: i32, pa: i32, sb: i32, eb: i32, pb: i32) -> i32 {
    let only_a: i32 = __flow_sum_range(sa, ea, pa)
    let only_b: i32 = __flow_sum_range(sb, eb, pb)
    let both: i32 = __flow_sum_range_isect(sa, ea, pa, sb, eb, pb)
    return only_a + only_b - both
}
"""


def set_helper_declarations():
    """The range-sum helper plus the set-algebra helpers it builds on."""
    from .parser import parse_flow_code

    return parse_flow_code(HELPER_SOURCE + SET_HELPER_SOURCE)
