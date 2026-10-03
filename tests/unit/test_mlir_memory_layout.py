"""
Unit tests for MLIR memory layout transformations:
- AoSoA (Array of Structs of Arrays) memref transformations
- Conflict-free 2D/3D stride padding (bank conflicts & 4K aliasing)
- Swizzled memory indexing for non-major dimension accesses
"""

from pathlib import Path
import tempfile
import pytest

from flow.mlir_optimizer import (
    MLIROptimizer,
    transform_aosoa_memref,
    apply_conflict_padding,
    apply_swizzled_indexing,
)


def test_aosoa_memref_transformation_2d():
    mlir_in = """module {
  func.func @test(%a: memref<1024x4xf32>, %i: index, %f: index) {
    %v = memref.load %a[%i, %f] : memref<1024x4xf32>
    memref.store %v, %a[%i, %f] : memref<1024x4xf32>
    return
  }
}"""
    out = transform_aosoa_memref(mlir_in, tile_size=16)
    assert "memref<64x4x16xf32>" in out
    assert "arith.divui" in out
    assert "arith.remui" in out
    assert "%aosoa_outer_i" in out
    assert "%aosoa_inner_i" in out


def test_aosoa_memref_transformation_1d():
    mlir_in = """module {
  func.func @test(%a: memref<1024xf32>, %i: index) {
    %v = memref.load %a[%i] : memref<1024xf32>
    return
  }
}"""
    out = transform_aosoa_memref(mlir_in, tile_size=16)
    assert "memref<64x16xf32>" in out
    assert "arith.divui" in out
    assert "arith.remui" in out


def test_aosoa_memref_skips_small_or_non_multiples():
    mlir_in = """module {
  func.func @test(%a: memref<8x4xf32>, %i: index) {
    return
  }
}"""
    out = transform_aosoa_memref(mlir_in, tile_size=16)
    assert "memref<8x4xf32>" in out
    assert "arith.divui" not in out


def test_conflict_padding_2d():
    mlir_in = """module {
  func.func @test(%a: memref<32x32xf32>) {
    %v = memref.load %a[%c0, %c0] : memref<32x32xf32>
    return
  }
}"""
    out = apply_conflict_padding(mlir_in, pad_amount=1, min_stride_multiple=16)
    assert "memref<32x33xf32>" in out
    assert "memref<32x32xf32>" not in out


def test_conflict_padding_3d():
    mlir_in = """module {
  func.func @test(%a: memref<16x16x16xf32>) {
    return
  }
}"""
    out = apply_conflict_padding(mlir_in, pad_amount=2, min_stride_multiple=16)
    assert "memref<16x16x18xf32>" in out


def test_conflict_padding_skips_unaligned_stride():
    mlir_in = """module {
  func.func @test(%a: memref<32x15xf32>) {
    return
  }
}"""
    out = apply_conflict_padding(mlir_in, pad_amount=1, min_stride_multiple=16)
    assert "memref<32x15xf32>" in out


def test_swizzled_indexing_nonmajor():
    mlir_in = """module {
  func.func @test(%a: memref<32x32xf32>, %r: index, %c: index) {
    %v = memref.load %a[%r, %c] : memref<32x32xf32> // swizzle nonmajor
    return
  }
}"""
    out = apply_swizzled_indexing(mlir_in, tile_width=16)
    assert "arith.andi" in out
    assert "arith.xori" in out
    assert "%swiz_col_c" in out


def test_mlir_optimizer_integration_layout_passes():
    mlir_in = """module {
  func.func @test(%a: memref<1024x4xf32>, %b: memref<32x32xf32>, %i: index, %r: index, %c: index) {
    %v = memref.load %a[%i, %c0] : memref<1024x4xf32>
    %v2 = memref.load %b[%r, %c] : memref<32x32xf32> // swizzle
    return
  }
}"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        in_file = Path(tmp_dir) / "in.mlir"
        out_file = Path(tmp_dir) / "out.mlir"
        in_file.write_text(mlir_in)

        opt = MLIROptimizer()
        res = opt.optimize(
            str(in_file),
            str(out_file),
            enable_aosoa=True,
            enable_conflict_padding=True,
            enable_swizzling=True,
            aosoa_tile_size=16,
            padding_amount=1,
            min_stride_multiple=16,
            swizzle_tile_width=16,
        )
        assert res == 0
        out = out_file.read_text()
        # AoSoA creates 64x4x16xf32, and conflict padding pads inner tile 16 -> 17
        assert "memref<64x4x17xf32>" in out
        assert "arith.divui" in out
        assert "arith.remui" in out


def test_layout_passes_disabled_by_default():
    mlir_in = """module {
  func.func @test(%a: memref<1024x4xf32>, %b: memref<32x32xf32>) {
    return
  }
}"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        in_file = Path(tmp_dir) / "in.mlir"
        out_file = Path(tmp_dir) / "out.mlir"
        in_file.write_text(mlir_in)

        opt = MLIROptimizer()
        res = opt.optimize(
            str(in_file),
            str(out_file),
            enable_aosoa=False,
            enable_conflict_padding=False,
            enable_swizzling=False,
        )
        assert res == 0
        out = out_file.read_text()
        assert "memref<1024x4xf32>" in out
        assert "memref<32x32xf32>" in out
        assert "memref<64x4x16xf32>" not in out
        assert "memref<32x33xf32>" not in out
