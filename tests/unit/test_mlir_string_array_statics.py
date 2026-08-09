"""Static string-array globals must initialize (doom-flow #254 / #230)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code
from flow.mlir_generator import flow_to_mlir, MLIRGenerator


def test_emit_static_llvm_array_global_api_exists():
    """doom-flow build_wasm.sh gates on this method existing."""
    assert hasattr(MLIRGenerator, "_emit_static_llvm_array_global")


def test_string_array_static_is_initialized_not_undef():
    mlir = flow_to_mlir(
        parse_flow_code(
            """
let mut names: array<string, 3> = ["use_mouse", "mouse_sensitivity", "sfx_volume"]

function main() -> i32 {
    return 0
}
"""
        ),
        source_file="test.flow",
    )
    assert "llvm.mlir.global internal @names()" in mlir
    assert "llvm.return" in mlir
    assert "llvm.insertvalue" in mlir
    assert "llvm.mlir.addressof" in mlir
    # No bare undef one-liner for @names.
    for line in mlir.splitlines():
        if "llvm.mlir.global internal @names()" in line and "{" not in line:
            assert "undef" not in line
