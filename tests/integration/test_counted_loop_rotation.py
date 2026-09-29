"""Counted-loop rotation (#473) in the MLIR lowering.

The run checks for the loop shapes this rewrite targets live in
tests/lang/test_counted_loop_rotation.flow. What stays here is the shape of
the MLIR the rotated loop lowers to.
"""

from __future__ import annotations

from pathlib import Path

from flow.mlir_generator import MLIRGenerator
from flow.parser import parse_flow_code


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "counted_loop_rotation.flow"


def test_doom_shaped_fixture_lowers_to_a_latch_compare() -> None:
    mlir = MLIRGenerator().generate_module(parse_flow_code(FIXTURE.read_text()))
    hot = mlir.split("func.func @draw_column")[1].split("\n  func.func")[0]
    # One test, at the latch, driving the loop.
    assert hot.count("cf.cond_br") == 1, hot
    assert "arith.cmpi ne" in hot, hot
    # #474: the accessor call inside the hot loop is gone.
    assert "func.call @dc_iscale_value" not in hot, hot
    assert hot.count("llvm.mlir.addressof @dc_iscale") == 2, hot
