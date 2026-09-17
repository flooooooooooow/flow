"""Loop-invariant span `.len` hoisting (#729).

A loop written as `for i in 0 to xs.len { ... xs[i] ... }` reloads the span
length field on every iteration test. When the bound is `<span>.len` for a
local span that is provably not rebound in the loop body, the length is loaded
once into a temp and the bound (and any in-loop `xs.len` read) reads the temp.

The unsafe case (the span is rebound in the body) keeps reloading the field.
That is the same conservative condition used for bounds-check elision.
"""

from __future__ import annotations

import re

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def _c(source: str) -> str:
    return flow_to_c(parse_flow_code(source))


SAFE = """
function sumspan(xs: span<i32>) -> i32 {
    let mut total: i32 = 0
    for i in 0 to xs.len {
        total = total + xs[i]
    }
    return total
}
"""

REBOUND = """
function f(xs: span<i32>, ys: span<i32>) -> i32 {
    let mut total: i32 = 0
    for i in 0 to xs.len {
        xs = ys
        total = total + i
    }
    return total
}
"""

INLOOP_LEN = """
function g(xs: span<i32>) -> i32 {
    let mut total: i32 = 0
    for i in 0 to xs.len {
        total = total + xs.len
    }
    return total
}
"""


def _hoist_temp(c: str):
    """Return the hoisted length temp name, or None if nothing was hoisted."""
    m = re.search(r"const int64_t (__flow_len_\d+) = \(xs\)\.len;", c)
    return m.group(1) if m else None


def test_safe_span_len_bound_is_loaded_once():
    c = _c(SAFE)
    temp = _hoist_temp(c)
    assert temp is not None, "expected the span length to be hoisted into a temp"

    # The temp is declared exactly once, before the loop.
    assert c.count(f"const int64_t {temp} = (xs).len;") == 1

    # The loop condition reads the temp for its bound. The span length field
    # is never reloaded inside the condition.
    cond = next(ln for ln in c.splitlines() if "for (int32_t i" in ln)
    assert temp in cond
    assert "(xs).len" not in cond and "xs.len" not in cond


def test_unsafe_rebound_span_is_not_hoisted():
    c = _c(REBOUND)
    # The span is rebound in the body, so no length temp is emitted and the
    # field is reloaded. The loop stays as it was.
    assert _hoist_temp(c) is None
    assert "__flow_len_" not in c
    cond = next(ln for ln in c.splitlines() if "for (int32_t i" in ln)
    assert "xs.len" in cond


def test_inloop_len_read_reuses_the_hoisted_temp():
    c = _c(INLOOP_LEN)
    temp = _hoist_temp(c)
    assert temp is not None

    # The in-loop `xs.len` read resolves to the temp. No fresh field load is
    # emitted in the loop body.
    body_line = next(ln for ln in c.splitlines() if "total = (total +" in ln)
    assert temp in body_line
    assert ".len" not in body_line
