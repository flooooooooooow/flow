"""Copy elision for `let` bindings of record updates (#732).

`let q = Struct { ..base, f: v }` used to lower to a statement expression that
copied `base` into an intermediate `_flow_rupdate` temporary and then copied
that temporary into `q`. The new binding needs its own copy of `base` anyway,
so we build the update in place: `T q = base; q.f = v;`. That removes one full
struct copy while keeping value semantics, because `q` stays distinct from
`base`.

A returned record update goes one step further under move inference (#696):
when the base is a plain local, the return is its last use, so the update is
built in place on the base and returned, eliding the temporary. A returned
update whose value reads the base keeps the temporary, because an in-place
write would clobber a field before it is read.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def _gen_c(source: str) -> str:
    return flow_to_c(parse_flow_code(source))


def test_let_record_update_builds_in_place() -> None:
    """A `let` bound to a record update constructs into the variable directly."""
    c = _gen_c(
        """
struct Vec3 { x: f64, y: f64, z: f64 }
function tweak(p: Vec3) -> f64 {
    let q = Vec3 { ..p, x: 9.0 }
    return q.x + p.y
}
"""
    )
    # No intermediate record-update temporary for the let binding.
    assert "_flow_rupdate" not in c
    # The binding is the required base copy, then an in-place field write.
    assert re.search(r"Vec3\s+q\s*=\s*p\s*;", c)
    assert re.search(r"\bq\.x\s*=\s*9\.0\s*;", c)


def test_let_record_update_keeps_base_copy() -> None:
    """The base is copied into a distinct variable, so value semantics hold.

    `p` is still read after the update, so the generated C must keep its own
    copy (`q = p`) rather than aliasing `p`. `p` still appears in the return.
    """
    c = _gen_c(
        """
struct Vec3 { x: f64, y: f64, z: f64 }
function tweak(p: Vec3) -> f64 {
    let q = Vec3 { ..p, x: 9.0 }
    return q.x + p.y
}
"""
    )
    assert re.search(r"Vec3\s+q\s*=\s*p\s*;", c)
    # `p` is untouched by the update and read afterwards.
    assert "p.y" in c
    assert not re.search(r"\bp\.x\s*=", c)


def test_let_record_update_array_field_in_place() -> None:
    """An array-typed field update memcpys straight into the declared variable."""
    c = _gen_c(
        """
struct Grid { cells: array<i32, 4>, tag: i32 }
function relabel(g: Grid) -> i32 {
    let h = Grid { ..g, tag: 7 }
    return h.tag
}
"""
    )
    assert "_flow_rupdate" not in c
    assert re.search(r"Grid\s+h\s*=\s*g\s*;", c)
    assert re.search(r"\bh\.tag\s*=\s*7\s*;", c)


def test_return_record_update_moves_local_base() -> None:
    """A returned update of a local base is moved: no temporary, no copy (#696)."""
    c = _gen_c(
        """
struct Vec3 { x: f64, y: f64, z: f64 }
function bump(p: Vec3) -> Vec3 {
    return Vec3 { ..p, x: 1.0 }
}
"""
    )
    # The return is the last use of `p`, so the update is built in place on `p`
    # and `p` is returned, eliding the statement-expression temporary and the
    # full-struct copy it carried.
    assert "_flow_rupdate" not in c
    assert re.search(r"\bp\.x\s*=\s*1\.0\s*;", c)
    assert re.search(r"return\s+p\s*;", c)


def test_return_record_update_reading_base_keeps_temporary() -> None:
    """A returned update whose value reads the base keeps its value temporary."""
    c = _gen_c(
        """
struct Vec3 { x: f64, y: f64, z: f64 }
function shift(p: Vec3) -> Vec3 {
    return Vec3 { ..p, x: p.y }
}
"""
    )
    # `p.y` is read by the update, so an in-place write onto `p` could clobber
    # it. The statement-expression temporary copies the base first.
    assert "_flow_rupdate" in c
    assert re.search(r"Vec3\s+_flow_rupdate_\d+\s*=\s*p\s*;", c)
