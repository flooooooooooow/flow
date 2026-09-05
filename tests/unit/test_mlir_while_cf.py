"""Pin CF and alloca lowering for while loops, using mutable slots."""

from flow.mlir_generator import MLIRGenerator
from tests.unit.compiler_helpers import parse


def test_while_cf_uses_alloca_slots_not_ssa_args():
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
    # Mutables are stack slots; CF edges are plain labels (no successor args).
    assert "llvm.alloca" in mlir, mlir
    assert "cf.br ^bb0" in mlir, mlir
    assert "cf.cond_br" in mlir, mlir
    assert "cf.br ^bb0(" not in mlir, mlir
    assert "llvm.store" in mlir and "llvm.load" in mlir, mlir


def test_nested_while_updates_outer_slot():
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
    # Nested loops still terminate via plain CF edges back to headers.
    assert mlir.count("cf.br ^bb0") >= 1, mlir
    assert "cf.br ^bb3" in mlir, mlir
    assert "llvm.alloca" in mlir, mlir
    # Inner body must still store into the shared `s` slot.
    store_lines = [ln for ln in mlir.splitlines() if "llvm.store" in ln]
    assert len(store_lines) >= 4, store_lines


def test_array_store_uses_fixed_shape():
    """A known-size array is addressed at its declared size.

    This checked `memref<3xi32>` over `memref<?xi32>` when arrays lowered
    through memref. They lower to llvm.alloca now, and the same property is
    that the GEPs carry `!llvm.array<3 x i32>`: an index is scaled by the real
    element size rather than walked as raw bytes.
    """
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
    gep_lines = [ln for ln in mlir.splitlines() if "llvm.getelementptr" in ln]
    assert gep_lines, mlir
    assert all("!llvm.array<3 x i32>" in ln for ln in gep_lines), gep_lines
    assert all("!llvm.array<? x i32>" not in ln for ln in gep_lines), gep_lines

    store_lines = [ln for ln in mlir.splitlines() if "llvm.store" in ln]
    assert store_lines, mlir
