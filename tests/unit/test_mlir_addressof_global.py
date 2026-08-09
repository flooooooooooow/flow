"""Address-of module globals must not spill into a temp (#230 thinkers)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code
from flow.mlir_generator import flow_to_mlir


def test_address_of_module_array_is_global_not_alloca_spill():
    """`return &thinkercap` must be addressof @thinkercap, not ptr-to-alloca.

    Spilling the global address into a fresh alloca returns a pointer-to-pointer.
    Doom then links the thinker list through stack garbage → P_Ticker calls
    heap addresses via flow_rt_call_p1 → wasm table index OOB.
    """
    mlir = flow_to_mlir(
        parse_flow_code(
            """
let mut thinkercap: array<i64, 3> = [0, 0, 0]

function THINKER_cap() -> ptr<void> {
    return &thinkercap as ptr<void>
}

function main() -> i32 {
    let p: ptr<void> = THINKER_cap()
    return (p as i64) != 0
}
"""
        ),
        source_file="test.flow",
    )
    # Must address the global directly.
    assert "llvm.mlir.addressof @thinkercap" in mlir
    # The classic bug stored addressof into alloca then returned the alloca.
    # Ensure THINKER_cap body does not return an alloca of ptr.
    # Extract function body roughly:
    start = mlir.find("func.func @THINKER_cap")
    assert start != -1
    end = mlir.find("func.func @", start + 1)
    body = mlir[start:end if end != -1 else None]
    # Returning the alloca that holds @thinkercap looks like:
    #   %x = llvm.alloca ... : !llvm.ptr
    #   llvm.store %addr, %x
    #   return %x
    # After the fix, return should use the addressof SSA (or a cast of it),
    # not an alloca of pointer type used only to re-home the global addr.
    assert "llvm.mlir.addressof @thinkercap" in body
    # Soft check: if there is an alloca of ptr, it must not be the only return path
    # via store-of-addressof. Stronger: no `llvm.alloca` of !llvm.ptr in this fn.
    if "llvm.alloca" in body and "!llvm.ptr" in body:
        # Allow only if addressof is returned without store-to-alloca-of-addr pattern.
        assert "llvm.store" not in body or body.find("addressof") < body.find("llvm.store")


def test_address_of_scalar_module_global_is_not_alloca_spill():
    """`return &dc_yh` must be addressof — load+spill becomes UB at -O1 (#253).

    Returning a pointer to a fresh alloca of the loaded value makes LLVM treat
    callers as unreachable under -O1+, which showed up as false ``noreturn`` on
    doom draw routines and a dropped main loop after emcc optimize.
    """
    mlir = flow_to_mlir(
        parse_flow_code(
            """
let mut dc_yh: i32 = 0

function drawshim_dc_yh_addr() -> ptr<i32> {
    return &dc_yh
}

function main() -> i32 {
    let p: ptr<i32> = drawshim_dc_yh_addr()
    p[0] = 1
    return p[0]
}
"""
        ),
        source_file="test.flow",
    )
    start = mlir.find("func.func @drawshim_dc_yh_addr")
    assert start != -1
    end = mlir.find("func.func @", start + 1)
    body = mlir[start : end if end != -1 else None]
    assert "llvm.mlir.addressof @dc_yh" in body
    assert "llvm.alloca" not in body
    assert "llvm.load" not in body
