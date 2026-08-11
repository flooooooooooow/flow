"""Regression tests for MLIR const binary operation folding (#420).

Const declarations with BinaryOperation initializers (e.g. 0 - 1)
should fold to the correct value, not zero-initialize.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.mlir_generator import flow_to_mlir


def _gen_mlir(source: str) -> str:
    decls = parse_flow_code(source)
    return flow_to_mlir(decls)


def test_const_subtraction():
    """0 - 1 folds to -1."""
    mlir = _gen_mlir("const NEG_ONE: i32 = 0 - 1\n")
    assert "@NEG_ONE(-1" in mlir


def test_const_addition():
    """1 + 2 folds to 3."""
    mlir = _gen_mlir("const THREE: i32 = 1 + 2\n")
    assert "@THREE(3" in mlir


def test_const_multiplication():
    """65536 * 2 folds to 131072."""
    mlir = _gen_mlir("const BIG: i32 = 65536 * 2\n")
    assert "@BIG(131072" in mlir


def test_const_shift_left():
    """1 << 4 folds to 16."""
    mlir = _gen_mlir("const SHIFTED: i32 = 1 << 4\n")
    assert "@SHIFTED(16" in mlir


def test_const_subtraction_large():
    """0 - 2147483648 folds correctly."""
    mlir = _gen_mlir("const SIGNBIT: i32 = 0 - 2147483648\n")
    assert "@SIGNBIT(" in mlir
    assert "@SIGNBIT(0" not in mlir


def test_const_i64_subtraction():
    """0 - 1 for i64 folds to -1."""
    mlir = _gen_mlir("const NEG_I64: i64 = 0 - 1\n")
    assert "@NEG_I64(-1" in mlir


def test_const_bitwise_or():
    """1 | 2 folds to 3."""
    mlir = _gen_mlir("const OR_RESULT: i32 = 1 | 2\n")
    assert "@OR_RESULT(3" in mlir


def test_const_does_not_zero_init():
    """BinaryOperation const is not zero-initialized."""
    mlir = _gen_mlir("const X: i32 = 5 - 3\n")
    assert "@X(0" not in mlir
    assert "@X(2" in mlir
