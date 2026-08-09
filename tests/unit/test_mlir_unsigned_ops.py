"""Unsigned / % must use remui/divui (#230 doom hash table)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code
from flow.mlir_generator import flow_to_mlir


def test_u32_modulo_uses_remui_not_remsi():
    """W_LumpNameHash returns u32; `hash % n` must be unsigned.

    Signed srem on large hashes yields negative indices; GEP then writes
    before the calloc'd table and corrupts the heap (FILE*, zone, …).
    """
    mlir = flow_to_mlir(
        parse_flow_code(
            """
function hash_name(s: ptr<u8>) -> u32 {
    return 5381
}

let mut n: u32 = 10

function main() -> i32 {
    let h: u32 = hash_name(null)
    let i: u32 = h % n
    return i as i32
}
"""
        ),
        source_file="test.flow",
    )
    assert "arith.remui" in mlir
    assert "arith.remsi" not in mlir


def test_u32_div_uses_divui():
    mlir = flow_to_mlir(
        parse_flow_code(
            """
function main() -> i32 {
    let a: u32 = 100
    let b: u32 = 7
    return (a / b) as i32
}
"""
        ),
        source_file="test.flow",
    )
    assert "arith.divui" in mlir
    assert "arith.divsi" not in mlir
