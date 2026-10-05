#!/usr/bin/env python3
"""FIR-G Phase 4 (start): batched optimisation *candidates* + deterministic costs.

Profitability only — proposals never rewrite the graph or bypass semantic checks.
Transforms that would change meaning stay gated on the trusted compiler path.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from .fir_analysis import purity_flags, reachable_functions
from .fir_g import FirG, OpCode


# Heuristic knobs (deterministic, documented — not learned).
INLINE_MAX_CALLEE_OPS = 16
INLINE_SINGLE_SITE_BONUS = 2.0
INLINE_PURE_BONUS = 1.5
DEAD_ELIM_BASE_SCORE = 10.0


@dataclass(frozen=True)
class OptCandidate:
    kind: str  # "dead_elim" | "inline"
    target: str
    score: float  # higher = more profitable to consider
    reason: str
    caller: Optional[str] = None
    callsite_op: Optional[int] = None
    callee_ops: Optional[int] = None
    call_sites: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)


def func_op_count(g: FirG, fid: int) -> int:
    total = 0
    first = g.func_first_block[fid]
    nblocks = g.func_block_count[fid]
    for bi in range(first, first + nblocks):
        total += g.block_op_count[bi]
    return total


def _callee_call_sites(g: FirG) -> Dict[int, List[int]]:
    """Map callee func id → list of CALL op ids."""
    if not g.call_row_offsets:
        g.build_call_graph_csr()
    sites: Dict[int, List[int]] = {}
    for op in range(g.num_ops()):
        if g.op_opcode[op] != OpCode.CALL:
            continue
        cal = g.op_callee[op]
        if cal < 0:
            continue
        sites.setdefault(cal, []).append(op)
    return sites


def discover_candidates(
    g: FirG,
    *,
    roots: Optional[List[str]] = None,
    inline_max_ops: int = INLINE_MAX_CALLEE_OPS,
) -> List[OptCandidate]:
    """Scan FIR-G for dead-elim and inline candidates; score deterministically."""
    if not g.call_row_offsets:
        g.build_call_graph_csr()
    # Effects/purity should reflect propagated bits when available.
    pure = purity_flags(g)
    live = reachable_functions(g, roots)
    sites_by_callee = _callee_call_sites(g)
    out: List[OptCandidate] = []

    for fid in range(g.num_funcs()):
        name = g.func_name[fid]
        if fid in live:
            continue
        if name == "main":
            continue
        # Unreachable from roots → dead code elimination candidate.
        out.append(
            OptCandidate(
                kind="dead_elim",
                target=name,
                score=DEAD_ELIM_BASE_SCORE + float(func_op_count(g, fid)),
                reason="unreachable from roots",
                callee_ops=func_op_count(g, fid),
            )
        )

    for cal, sites in sites_by_callee.items():
        if cal not in live:
            continue
        if g.func_is_extern[cal]:
            continue
        ops = func_op_count(g, cal)
        if ops <= 0 or ops > inline_max_ops:
            continue
        name = g.func_name[cal]
        is_pure = pure.get(name, False)
        n_sites = len(sites)
        # Smaller body, fewer sites, purity → higher score.
        score = (inline_max_ops - ops + 1) / float(n_sites)
        if n_sites == 1:
            score *= INLINE_SINGLE_SITE_BONUS
        if is_pure:
            score *= INLINE_PURE_BONUS
        for op in sites:
            caller = g.func_name[g.op_function[op]]
            reason = f"callee_ops={ops} sites={n_sites} pure={is_pure}"
            out.append(
                OptCandidate(
                    kind="inline",
                    target=name,
                    score=round(score, 4),
                    reason=reason,
                    caller=caller,
                    callsite_op=op,
                    callee_ops=ops,
                    call_sites=n_sites,
                )
            )

    out.sort(key=lambda c: (-c.score, c.kind, c.target, c.callsite_op or -1))
    return out


def summarise_candidates(cands: List[OptCandidate], *, limit: int = 32) -> dict:
    by_kind: Dict[str, int] = {}
    for c in cands:
        by_kind[c.kind] = by_kind.get(c.kind, 0) + 1
    return {
        "total": len(cands),
        "by_kind": by_kind,
        "top": [c.to_dict() for c in cands[:limit]],
    }
