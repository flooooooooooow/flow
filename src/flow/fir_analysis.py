#!/usr/bin/env python3
"""CPU reference analyses over FIR-G (Phase 1).

Deterministic fixed-point propagations. Future GPU/MLX ports must match these
oracles bit-for-bit on the same graphs (differential tests).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from .fir_g import (
    EFF_ALLOCATES,
    EFF_FFI,
    EFF_GPU,
    EFF_IO,
    EFF_UNKNOWN,
    EFF_WRITES_MEMORY,
    FirG,
    OpCode,
)


def propagate_effects(g: FirG, *, max_iters: int = 64) -> List[int]:
    """Monotone call-graph effect OR-propagation.

    X^{t+1}[f] = X^t[f] ∨ ⋃_{c ∈ callees(f)} X^t[c]
    until fixpoint. Returns per-function effect bitvectors.
    """
    F = g.num_funcs()
    bits = list(g.func_effect_bits)
    if not g.call_row_offsets:
        g.build_call_graph_csr()

    for _ in range(max_iters):
        changed = False
        for f in range(F):
            lo = g.call_row_offsets[f]
            hi = g.call_row_offsets[f + 1]
            acc = bits[f]
            for ei in range(lo, hi):
                cal = g.call_columns[ei]
                acc |= bits[cal]
            if acc != bits[f]:
                bits[f] = acc
                changed = True
        if not changed:
            break

    g.func_effect_bits = bits
    return bits


def reachable_functions(g: FirG, roots: Optional[List[str]] = None) -> Set[int]:
    """Forward reachability on the call graph from roots (default: main)."""
    if not g.call_row_offsets:
        g.build_call_graph_csr()
    if roots is None:
        roots = ["main"]
    start: List[int] = []
    for name in roots:
        fid = g._func_by_name.get(name)
        if fid is not None:
            start.append(fid)
    if not start and g.num_funcs() > 0:
        start = [0]

    seen: Set[int] = set()
    stack = list(start)
    while stack:
        f = stack.pop()
        if f in seen:
            continue
        seen.add(f)
        lo = g.call_row_offsets[f]
        hi = g.call_row_offsets[f + 1]
        for ei in range(lo, hi):
            cal = g.call_columns[ei]
            if cal not in seen:
                stack.append(cal)
    return seen


def dead_functions(g: FirG, roots: Optional[List[str]] = None) -> List[str]:
    live = reachable_functions(g, roots)
    return [g.func_name[i] for i in range(g.num_funcs()) if i not in live]


def call_graph_edges(g: FirG) -> List[Tuple[str, str, int]]:
    """Extract call graph edges with weights."""
    if not g.call_row_offsets:
        g.build_call_graph_csr()

    # Count occurrences of (caller, callee) to represent weights
    from collections import Counter
    counts = Counter()
    for f in range(g.num_funcs()):
        lo = g.call_row_offsets[f]
        hi = g.call_row_offsets[f + 1]
        for ei in range(lo, hi):
            counts[(g.func_name[f], g.func_name[g.call_columns[ei]])] += 1

    out: List[Tuple[str, str, int]] = []
    for (caller, callee), weight in counts.items():
        out.append((caller, callee, weight))
    return out


def purity_flags(g: FirG) -> Dict[str, bool]:
    """Coarse purity: no IO/FFI/alloc/write/unknown/gpu bits after propagation."""
    dirty = (
        EFF_IO
        | EFF_FFI
        | EFF_ALLOCATES
        | EFF_WRITES_MEMORY
        | EFF_UNKNOWN
        | EFF_GPU
    )
    return {
        g.func_name[i]: (g.func_effect_bits[i] & dirty) == 0
        for i in range(g.num_funcs())
    }


def analyse(g: FirG) -> dict:
    """Run Phase 1 CPU analysis suite; mutates g.func_effect_bits."""
    propagate_effects(g)
    live = reachable_functions(g)
    return {
        "summary": g.summary(),
        "call_edges": call_graph_edges(g),
        "effects": {
            g.func_name[i]: int(g.func_effect_bits[i]) for i in range(g.num_funcs())
        },
        "pure": purity_flags(g),
        "reachable": sorted(g.func_name[i] for i in live),
        "dead": dead_functions(g),
        "num_call_ops": sum(1 for op in g.op_opcode if op == OpCode.CALL),
    }
