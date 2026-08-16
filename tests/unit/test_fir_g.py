"""FIR-G Phase 1: dense graph store, graphify, CPU analyses."""

from __future__ import annotations

from pathlib import Path

import pytest

from flow.fir_analysis import analyse, propagate_effects, reachable_functions
from flow.fir_cli import build_fir_g
from flow.fir_g import EFF_IO, OpCode, FirG
from flow.fir_graphify import graphify
from flow.parser import FunctionDecl, Parameter, Type, Block, ReturnStatement, Literal, FunctionCall


def test_soa_ids_are_dense():
    g = FirG()
    f = g.add_function("f")
    b = g.add_block(f)
    tid = g.intern_type("i32")
    op, vals = g.add_op(OpCode.CONST, f, b, result_type_ids=[tid])
    assert op == 0
    assert vals == [0]
    assert g.num_funcs() == 1
    assert g.num_values() == 1


def test_graphify_call_and_effects():
    # Minimal synthetic decls: main -> print (extern)
    decls = [
        FunctionDecl(
            name="print",
            parameters=[Parameter("s", Type("string"))],
            return_type=Type("void"),
            body=Block([]),
            attributes=[],
            is_extern=True,
        ),
        FunctionDecl(
            name="main",
            parameters=[],
            return_type=Type("i32"),
            body=Block(
                [
                    FunctionCall("print", [Literal('"hi"', Type("string"))]),
                    ReturnStatement(Literal("0", Type("i32"))),
                ]
            ),
            attributes=[],
        ),
    ]
    g = graphify(decls)
    report = analyse(g)
    assert ("main", "print") in [(a, b) for a, b, _ in report["call_edges"]]
    assert report["effects"]["main"] & EFF_IO
    assert report["pure"]["print"] is False
    assert "main" in report["reachable"]


def test_dead_function_detection(tmp_path: Path):
    src = tmp_path / "dead.flow"
    src.write_text(
        """
function dead() -> i32 { return 1 }
function helper() -> i32 { return 2 }
function main() -> i32 {
    return helper()
}
"""
    )
    g = build_fir_g(str(src))
    report = analyse(g)
    assert "helper" in report["reachable"]
    assert "dead" in report["dead"]
    assert "main" in report["reachable"]


def test_effect_propagation_through_chain(tmp_path: Path):
    src = tmp_path / "eff.flow"
    src.write_text(
        """
extern {
    function printf(fmt: string, val: i32) -> i32
}
function leaf() -> i32 {
    return printf("x", 1)
}
function mid() -> i32 {
    return leaf()
}
function main() -> i32 {
    return mid()
}
"""
    )
    g = build_fir_g(str(src))
    bits = propagate_effects(g)
    mid = g._func_by_name["mid"]
    main = g._func_by_name["main"]
    assert bits[mid] & EFF_IO
    assert bits[main] & EFF_IO


def test_fir_g_cli_hello():
    root = Path(__file__).resolve().parents[2]
    hello = root / "examples" / "basics" / "hello_world.flow"
    if not hello.exists():
        pytest.skip("hello_world.flow missing")
    g = build_fir_g(str(hello))
    report = analyse(g)
    assert g.num_funcs() >= 1
    assert "main" in report["reachable"]

def test_call_graph_edges(tmp_path: Path):
    src = tmp_path / "edges.flow"
    src.write_text(
        """
function callee1() -> i32 { return 1 }
function callee2() -> i32 { return 2 }
function caller() -> i32 {
    callee1()
    callee2()
    return callee1()
}
"""
    )
    from flow.fir_analysis import call_graph_edges
    g = build_fir_g(str(src))
    edges = call_graph_edges(g)

    # We expect 'caller' to call 'callee1' (weight 2) and 'callee2' (weight 1)
    caller_edges = [e for e in edges if e[0] == "caller"]
    assert len(caller_edges) == 2

    # Verify the weights
    weights = {callee: weight for _, callee, weight in caller_edges}
    assert weights["callee1"] == 2
    assert weights["callee2"] == 1
