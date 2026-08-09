"""Module-scope pointer statics + short-circuit and/or (#230)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code
from flow.mlir_generator import flow_to_mlir


def _mlir(src: str) -> str:
    return flow_to_mlir(parse_flow_code(src), source_file="test.flow")


def test_scalar_ptr_static_is_null_initialized():
    mlir = _mlir(
        """
let mut p: ptr<i32> = null

function main() -> i32 {
  return 0
}
"""
    )
    assert "llvm.mlir.global internal @p()" in mlir
    assert "llvm.mlir.zero : !llvm.ptr" in mlir


def test_or_short_circuits_before_rhs_load():
    mlir = _mlir(
        """
extern { function getenv(name: string) -> ptr<u8> }

function main() -> i32 {
  let p: ptr<u8> = getenv("X")
  if ((p as i64) == 0 or p[0] as i32 == 0) {
    return 1
  }
  return 0
}
"""
    )
    assert "scf.if" in mlir
    _head, _sep, tail = mlir.partition("scf.if")
    else_region = tail.split("else", 1)[1]
    assert "llvm.load" in else_region
