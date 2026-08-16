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


def test_analyse_comprehensive():
    # Use graphify to create a realistic graph instead of hand-building one
    decls = [
        FunctionDecl(
            name="helper",
            parameters=[],
            return_type=Type("i32"),
            body=Block([ReturnStatement(Literal("42", Type("i32")))]),
            attributes=[],
        ),
        FunctionDecl(
            name="dead_func",
            parameters=[],
            return_type=Type("void"),
            body=Block([]),
            attributes=[],
        ),
        FunctionDecl(
            name="main",
            parameters=[],
            return_type=Type("i32"),
            body=Block(
                [
                    ReturnStatement(FunctionCall("helper", [])),
                ]
            ),
            attributes=[],
        ),
    ]
    g = graphify(decls)

    # We will manually set an effect bit just to see it propagates
    helper_id = g._func_by_name["helper"]
    g.func_effect_bits[helper_id] |= 1  # some custom effect (non-dirty)

    report = analyse(g)

    # Assert all keys are present
    assert "summary" in report
    assert "call_edges" in report
    assert "effects" in report
    assert "pure" in report
    assert "reachable" in report
    assert "dead" in report
    assert "num_call_ops" in report

    # Assert values are as expected
    assert report["num_call_ops"] == 1

    edges = [(caller, callee) for caller, callee, _ in report["call_edges"]]
    assert ("main", "helper") in edges

    assert "main" in report["reachable"]
    assert "helper" in report["reachable"]

    assert "dead_func" in report["dead"]
    assert "dead_func" not in report["reachable"]

    assert report["pure"]["helper"] is True # 1 is not in dirty mask, so pure is True
    assert report["effects"]["main"] & 1


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
