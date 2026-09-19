"""Move inference for a returned record update (issue #696).

Flow structs have value semantics, so `Point { ..p, x: v }` copies the base
before overriding fields. When the update is returned and the base is a plain
local binding, the return is that binding's last use: nothing runs after a
return, so the base is dead. In that case the compiler builds the update in
place on the base and returns it, eliding the intermediate temporary and its
full-struct copy.

The move is withheld when it cannot be proven safe: when the base is read by
one of the update values (an in-place write would clobber a field before it is
read), and when the base outlives the update because a later statement reads it.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c

STRUCT = """
struct Point {
    x: i32,
    y: i32,
}
"""


def _gen(source: str) -> str:
    return flow_to_c(parse_flow_code(STRUCT + source))


def _body(c: str, fn_prefix: str) -> str:
    """Return the C source of the function whose name starts with fn_prefix."""
    marker = "\n" + fn_prefix
    start = c.index(marker)
    brace = c.index("{", start)
    depth = 0
    for i in range(brace, len(c)):
        if c[i] == "{":
            depth += 1
        elif c[i] == "}":
            depth -= 1
            if depth == 0:
                return c[brace:i + 1]
    raise AssertionError("function body not found for " + fn_prefix)


def test_returned_update_of_local_is_moved():
    """The last use of a local base becomes an in-place move, no copy."""
    c = _gen(
        """
function bump(p: Point) -> Point {
    return Point { ..p, x: 5 };
}
"""
    )
    body = _body(c, "Point bump")
    # No temporary and no full-struct copy of the base.
    assert "_flow_rupdate" not in body
    assert "Point _" not in body
    # The field is written straight onto the base, which is then returned.
    assert "p.x = 5;" in body
    assert "return p;" in body


def test_returned_update_reading_base_keeps_copy():
    """An update value that reads the base cannot move: the copy stays."""
    c = _gen(
        """
function shift(p: Point) -> Point {
    return Point { ..p, x: p.y };
}
"""
    )
    body = _body(c, "Point shift")
    # The value reads p.y, so building in place on p would clobber it. The
    # base must be copied first, which the record-update temporary provides.
    assert "_flow_rupdate" in body


def test_base_used_after_update_keeps_copy():
    """A base that outlives the update keeps its copy (negative case)."""
    c = _gen(
        """
function keep(p: Point) -> i32 {
    let q = Point { ..p, x: 5 };
    return p.x + q.x;
}
"""
    )
    body = _body(c, "int32_t keep")
    # `q` is a distinct copy of `p`; `p` is read again afterwards, so the copy
    # `Point q = p;` must remain.
    assert "Point q = p;" in body
    assert "q.x = 5;" in body
