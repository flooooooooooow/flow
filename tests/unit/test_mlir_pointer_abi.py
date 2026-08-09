"""Target pointer width for MLIR layouts under --wasm32 (#255)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code, StructDecl
from flow.mlir_generator import MLIRGenerator, flow_to_mlir


def _struct_decl(src: str):
    decls = parse_flow_code(src)
    for d in decls:
        if isinstance(d, StructDecl) and d.name == "S":
            return d
    raise AssertionError("struct S not found")


def test_pointer_bytes_follow_size_t_bits():
    assert MLIRGenerator("t.flow", size_t_bits=64)._pointer_bytes() == 8
    assert MLIRGenerator("t.flow", size_t_bits=32)._pointer_bytes() == 4


def test_sizeof_ptr_mangled_sizes():
    """``sizeof_ptr`` intrinsic width follows ABI (#255)."""
    g64 = MLIRGenerator("t.flow", size_t_bits=64)
    g32 = MLIRGenerator("t.flow", size_t_bits=32)
    assert g64._sizeof_bytes_for_mangled("ptr") == 8
    assert g32._sizeof_bytes_for_mangled("ptr") == 4
    assert g32._sizeof_bytes_for_mangled("i32") == 4


def test_sizeof_ptr_call_inlines_wasm32_width():
    """Calls to ``sizeof_ptr()`` lower to a 4-byte constant under ILP32."""
    mlir = flow_to_mlir(
        parse_flow_code(
            """
function sizeof_ptr() -> i64 { return 8 }
function main() -> i32 {
    return sizeof_ptr() as i32
}
"""
        ),
        source_file="t.flow",
        size_t_bits=32,
    )
    # Call site must not use the stub body value 8.
    assert "arith.constant 4 : i64" in mlir


def test_struct_layout_pointer_field_is_ilp32_under_wasm32():
    decl = _struct_decl(
        """
struct S { p: ptr<void>, x: i32 }
function main() -> i32 { return 0 }
"""
    )
    g64 = MLIRGenerator("t.flow", size_t_bits=64)
    g32 = MLIRGenerator("t.flow", size_t_bits=32)
    g64._layout_one_struct(decl)
    g32._layout_one_struct(decl)
    assert g64.struct_layouts["S"]["p"]["size"] == 8
    assert g64.struct_layouts["S"]["x"]["offset"] == 8
    assert g32.struct_layouts["S"]["p"]["size"] == 4
    assert g32.struct_layouts["S"]["x"]["offset"] == 4
