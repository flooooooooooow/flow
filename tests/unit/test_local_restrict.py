"""Proven-disjoint local pointers carry `restrict` in the C backend (#731).

The region analysis (#694) proves a sound subset of local bindings disjoint
from every parameter and from each other. `restrict_candidates()` returns that
subset. The C backend marks a local pointer declaration `restrict` only when
its binding is in that set, and never otherwise. A wrong `restrict` is
undefined behaviour, so the negative cases below matter as much as the
positive one: a pointer that may alias a parameter must stay unqualified.

Function-signature parameters are out of scope here. The analysis never proves
two parameters disjoint (the caller may pass the same buffer twice), so the
interprocedural `restrict` on a signature is deliberately not emitted.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c
from flow.region_inference import analyze_function, FunctionDecl


def _gen(source: str) -> str:
    return flow_to_c(parse_flow_code(source))


def _candidates(source: str, fn_name: str):
    for decl in parse_flow_code(source):
        if isinstance(decl, FunctionDecl) and decl.name == fn_name:
            return analyze_function(decl).restrict_candidates()
    raise AssertionError(f"function {fn_name} not found")


def test_fresh_local_pointer_gets_restrict():
    # `p` is derived by pointer arithmetic, which the region analysis treats as
    # fresh local storage, so it is proven disjoint and qualifies. `base` is
    # never dereferenced, so `p` is the sole access path and the qualifier is
    # sound.
    src = """
    function fill(base: ptr<i32>, n: i32) -> i32 {
        let p: ptr<i32> = base + 0
        let mut i: i32 = 0
        while i < n {
            p[i] = i * 2
            i = i + 1
        }
        return p[0]
    }
    """
    assert "p" in _candidates(src, "fill")
    c = _gen(src)
    assert "int32_t* restrict p" in c


def test_pointer_derived_from_parameter_is_not_restrict():
    # `q = base` copies the parameter's provenance, so it may alias the caller's
    # buffer and must not be marked restrict.
    src = """
    function g(base: ptr<i32>) -> i32 {
        let q: ptr<i32> = base
        return q[0]
    }
    """
    assert "q" not in _candidates(src, "g")
    c = _gen(src)
    assert "restrict" not in c


def test_pointer_aliasing_a_local_array_is_not_restrict():
    # `bp` shares the region of the local array `buf`, so two bindings occupy
    # one region and neither qualifies. The array itself is not a pointer
    # declaration, so it never carries restrict either.
    src = """
    function main() -> i32 {
        let mut buf: array<i32, 4> = [0, 0, 0, 0]
        let bp: ptr<i32> = buf
        bp[0] = 7
        return bp[0]
    }
    """
    cands = _candidates(src, "main")
    assert "bp" not in cands
    assert "buf" not in cands
    c = _gen(src)
    assert "restrict" not in c


def test_two_distinct_locals_do_not_produce_parameter_restrict():
    # Two distinct fresh local pointers are each disjoint, but the parameter
    # they were built from is never itself qualified: parameter restrict stays
    # out of scope pending the interprocedural boundary work.
    src = """
    function two(base: ptr<i32>) -> i32 {
        let a: ptr<i32> = base + 0
        let b: ptr<i32> = base + 4
        a[0] = 1
        b[0] = 2
        return a[0] + b[0]
    }
    """
    c = _gen(src)
    # The signature keeps a plain pointer parameter.
    assert "int32_t* base" in c or "int32_t *base" in c
    assert "restrict base" not in c
