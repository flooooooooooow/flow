"""Pin CF-dialect successor operand syntax for while loop-carried vars."""

import re

from flow.mlir_generator import MLIRGenerator
from tests.unit.compiler_helpers import parse


def test_while_cf_br_types_once_after_values():
    mlir = MLIRGenerator().generate_module(
        parse(
            """
function main() -> i32 {
    let mut i: i32 = 0
    let mut s: i32 = 0
    while i < 3 {
        s = s + i
        i = i + 1
    }
    return s
}
"""
        )
    )
    # CF dialect: (%a, %b : i32, i32) — not (%a : i32, %b : i32)
    assert re.search(r"cf\.br \^bb\d+\(%\d+, %\d+ : i32, i32\)", mlir), mlir
    assert not re.search(r"cf\.br \^bb\d+\(%\d+ : i32, %\d+ : i32\)", mlir), mlir
    # Exit edge must pass loop-carried args into the end block
    cond = re.search(
        r"cf\.cond_br [^,]+, (\^bb\d+\([^)]+\)), (\^bb\d+\([^)]+\))", mlir
    )
    assert cond is not None, mlir


def test_nested_while_propagates_outer_carried_ssa():
    mlir = MLIRGenerator().generate_module(
        parse(
            """
function main() -> i32 {
    let mut outer: i32 = 0
    let mut s: i32 = 0
    while outer < 3 {
        let mut inner: i32 = 0
        while inner < 4 {
            s = s + 1
            inner = inner + 1
        }
        outer = outer + 1
    }
    return s
}
"""
        )
    )
    # Back-edge to outer header must forward the post-inner-loop `s`, not the
    # body-entry SSA (regression: shallow scope pop discarded nested updates).
    back_edges = re.findall(r"cf\.br \^bb0\(([^)]+)\)", mlir)
    assert back_edges, mlir
    # Last back-edge is the loop latch; operands should not be the same SSA
    # twice for (s, outer) after increments (s updated inside nested while).
    latch = back_edges[-1]
    parts = [p.strip() for p in latch.split(":")[0].split(",")]
    assert len(parts) == 2, latch
    assert parts[0] != parts[1], latch


def test_memref_store_uses_fixed_shape():
    mlir = MLIRGenerator().generate_module(
        parse(
            """
function main() -> i32 {
    let mut xs: array<i32, 3> = [1, 2, 3]
    xs[1] = 9
    return xs[1]
}
"""
        )
    )
    store_lines = [ln for ln in mlir.splitlines() if "memref.store" in ln]
    assert store_lines, mlir
    assert any("memref<3xi32>" in ln for ln in store_lines), store_lines
    assert all("memref<?xi32>" not in ln for ln in store_lines), store_lines
