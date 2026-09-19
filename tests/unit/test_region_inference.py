"""Local region inference / non-aliasing proofs (#694).

These tests pin the soundness contract of the conservative slice: the analysis
claims disjointness only when it can prove it, and declines otherwise. Each
positive case proves a non-aliasing fact; each negative case checks the
analysis refuses to claim disjointness where aliasing is possible.
"""

from flow.parser import parse_flow_code, FunctionDecl, Variable, SliceExpr
from flow.region_inference import RegionInference, LOCAL, PARAM, UNKNOWN


def _analyze(source: str, fn_name: str = "f") -> RegionInference:
    decls = parse_flow_code(source)
    func = next(
        d for d in decls if isinstance(d, FunctionDecl) and d.name == fn_name
    )
    return RegionInference(func)


def _slices(source: str, fn_name: str = "f"):
    """Every SliceExpr initializer in a function body, in source order."""
    decls = parse_flow_code(source)
    func = next(
        d for d in decls if isinstance(d, FunctionDecl) and d.name == fn_name
    )
    out = []
    for stmt in func.body.statements:
        init = getattr(stmt, "initializer", None)
        if isinstance(init, SliceExpr):
            out.append(init)
    return out


# --- positive: distinct owned locals are provably disjoint -----------------

def test_two_distinct_local_arrays_do_not_alias():
    ri = _analyze(
        """
function f() -> i32 {
    let a = [1, 2, 3, 4]
    let b = [5, 6, 7, 8]
    let s = a[0..2]
    let t = b[0..2]
    return 0
}
"""
    )
    # The two owned locals get distinct LOCAL regions.
    assert ri.region_of["a"].kind == LOCAL
    assert ri.region_of["b"].kind == LOCAL
    assert ri.region_of["a"] != ri.region_of["b"]
    # A borrow of a and a borrow of b are proven disjoint.
    assert ri.provably_disjoint(Variable("a"), Variable("b"))
    # The same holds for the slice views taken over them.
    s, t = _slices(
        """
function f() -> i32 {
    let a = [1, 2, 3, 4]
    let b = [5, 6, 7, 8]
    let s = a[0..2]
    let t = b[0..2]
    return 0
}
"""
    )
    assert ri.provably_disjoint(s, t)


# --- positive: a fresh local does not alias a parameter --------------------

def test_fresh_local_does_not_alias_parameter():
    ri = _analyze(
        """
function f(p: array<i32, 4>) -> i32 {
    let a = [1, 2, 3, 4]
    return 0
}
"""
    )
    assert ri.region_of["p"].kind == PARAM
    assert ri.region_of["a"].kind == LOCAL
    assert ri.provably_disjoint(Variable("a"), Variable("p"))


# --- negative: two parameters may be aliased by the caller -----------------

def test_two_parameters_may_alias():
    ri = _analyze(
        """
function f(p: array<i32, 4>, q: array<i32, 4>) -> i32 {
    return 0
}
"""
    )
    assert ri.region_of["p"].kind == PARAM
    assert ri.region_of["q"].kind == PARAM
    # The caller can pass the same buffer for p and q, so we must NOT claim
    # disjointness.
    assert not ri.provably_disjoint(Variable("p"), Variable("q"))
    assert ri.may_alias(Variable("p"), Variable("q"))


# --- negative: two borrows of the same local may alias ---------------------

def test_two_views_of_same_local_may_alias():
    ri = _analyze(
        """
function f() -> i32 {
    let a = [1, 2, 3, 4]
    return 0
}
"""
    )
    # Overlapping (or not) views of one buffer are not proven disjoint here.
    assert not ri.provably_disjoint(Variable("a"), Variable("a"))


# --- negative: a reassigned binding has an ambiguous region ----------------

def test_reassigned_binding_is_not_proven_disjoint():
    ri = _analyze(
        """
function f(p: array<i32, 4>) -> i32 {
    let a = [1, 2, 3, 4]
    let mut r = a[0..2]
    r = p[0..2]
    return 0
}
"""
    )
    # r is retargeted from a to p, so its region is TOP and it may alias both.
    assert ri.region_of["r"].kind == UNKNOWN
    assert not ri.provably_disjoint(Variable("r"), Variable("a"))
    assert not ri.provably_disjoint(Variable("r"), Variable("p"))


# --- negative: a call result has unknown provenance ------------------------

def test_call_result_has_unknown_provenance():
    ri = _analyze(
        """
function g(x: array<i32, 4>) -> array<i32, 4> { return x }
function f(p: array<i32, 4>) -> i32 {
    let a = g(p)
    return 0
}
"""
    )
    # g may return a borrow into p; we cannot claim a is disjoint from p.
    assert ri.region_of["a"].kind == UNKNOWN
    assert not ri.provably_disjoint(Variable("a"), Variable("p"))


# --- restrict candidates (the #731 hook) -----------------------------------

def test_restrict_candidates_are_only_disjoint_locals():
    ri = _analyze(
        """
function f(p: array<i32, 4>) -> i32 {
    let a = [1, 2, 3, 4]
    let b = [5, 6, 7, 8]
    let c = b
    return 0
}
"""
    )
    cand = ri.restrict_candidates()
    # a is a fresh, uniquely-owned local: safe to restrict.
    assert "a" in cand
    # p is a parameter: never a local restrict candidate.
    assert "p" not in cand
    # b and c share a region (c copies b conservatively), so neither is a
    # sole owner and neither is claimed.
    assert "b" not in cand
    assert "c" not in cand


# --- regression: pointer arithmetic derives from its base, not fresh -------

def test_pointer_arithmetic_is_not_a_restrict_candidate():
    # `base + off` points into `base`'s storage, so it must not be treated as
    # fresh disjoint storage. Marking it restrict would be undefined behaviour.
    # Guards the region_inference soundness fix.
    ri = _analyze(
        """
function f(base: ptr<i32>, n: i32) -> i32 {
    let p: ptr<i32> = base + 0
    let q: ptr<i32> = base + n
    return 0
}
"""
    )
    cand = ri.restrict_candidates()
    assert "p" not in cand, cand
    assert "q" not in cand, cand


def test_literal_arithmetic_stays_fresh():
    # Arithmetic over pure literals allocates a fresh value with no operand
    # provenance, so it remains a distinct local.
    ri = _analyze(
        """
function f() -> i32 {
    let x: i32 = 2 + 3
    return x
}
"""
    )
    assert "x" in ri.restrict_candidates()
