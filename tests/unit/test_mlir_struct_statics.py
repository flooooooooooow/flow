"""Module-scope struct / struct-array statics must not lower to undef (#230)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code
from flow.mlir_generator import flow_to_mlir


def _mlir(src: str) -> str:
    return flow_to_mlir(parse_flow_code(src), source_file="test.flow")


def test_struct_array_static_is_initialized_not_undef():
    mlir = _mlir(
        """
struct IwadEntry {
    name: string,
    mission: i32,
    mode: i32,
    description: string
}

let mut iwads: array<IwadEntry, 2> = [
    IwadEntry { name: "doom1.wad", mission: 0, mode: 0, description: "Doom Shareware" },
    IwadEntry { name: "doom.wad", mission: 0, mode: 3, description: "Doom" }
]

function main() -> i32 {
    return 0
}
"""
    )
    assert "llvm.mlir.global internal @iwads()" in mlir
    # Must have an init region — bare `() : !llvm.array<…>` lowers to undef.
    assert "llvm.return" in mlir
    assert "llvm.insertvalue" in mlir
    assert "llvm.mlir.addressof" in mlir
    # Negative: no bare undef-typed global without body for @iwads.
    for line in mlir.splitlines():
        if "llvm.mlir.global internal @iwads()" in line and "{" not in line:
            # Single-line form without region would be undef.
            assert "llvm.mlir.zero" in line or False, line


def test_struct_array_folds_binop_field_inits():
    mlir = _mlir(
        """
struct MenuItem {
    status: i32,
    name: string,
    routine: i32,
    alpha_key: i32
}

let mut items: array<MenuItem, 1> = [
    MenuItem { status: 0 - 1, name: "", routine: 0, alpha_key: 0 }
]

function main() -> i32 {
    return 0
}
"""
    )
    assert "llvm.mlir.constant(-1 : i32)" in mlir


def test_scalar_struct_static_is_zero_or_literal_init():
    mlir = _mlir(
        """
struct DivLine {
    x: i32,
    y: i32,
    dx: i32,
    dy: i32
}

let mut maputl_trace: DivLine = DivLine { x: 1, y: 2, dx: 3, dy: 4 }

function main() -> i32 {
    return 0
}
"""
    )
    assert "llvm.mlir.global internal @maputl_trace()" in mlir
    assert "llvm.insertvalue" in mlir
    assert "llvm.mlir.constant(1 : i32)" in mlir


@pytest.mark.skipif(
    subprocess.run(["which", "mlir-opt"], capture_output=True).returncode != 0
    or subprocess.run(["which", "mlir-translate"], capture_output=True).returncode != 0,
    reason="mlir-opt/mlir-translate not on PATH",
)
def test_struct_array_static_translates_without_undef():
    mlir = _mlir(
        """
struct E {
    a: i32,
    b: string
}

let mut tab: array<E, 1> = [
    E { a: 7, b: "hi" }
]

function main() -> i32 {
    return 0
}
"""
    )
    path = Path("/tmp/test_struct_static.mlir")
    path.write_text(mlir)
    # Match the Flow JIT/wasm lowering path: convert arith/func before translate.
    opt = subprocess.run(
        [
            "mlir-opt",
            str(path),
            "--convert-arith-to-llvm",
            "--convert-func-to-llvm",
            "--reconcile-unrealized-casts",
        ],
        capture_output=True,
        text=True,
    )
    assert opt.returncode == 0, opt.stderr
    lowered = Path("/tmp/test_struct_static_lowered.mlir")
    lowered.write_text(opt.stdout)
    result = subprocess.run(
        ["mlir-translate", "--mlir-to-llvmir", str(lowered)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    ll = result.stdout
    assert "@tab = internal global" in ll
    tab_line = [ln for ln in ll.splitlines() if ln.startswith("@tab =")][0]
    assert "undef" not in tab_line
    assert "i32 7" in tab_line
