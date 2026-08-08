#!/usr/bin/env python3
"""FIR-G Phase 2: experimental bulk analyses via MLX (Apple GPU) / NumPy.

Correctness contract
--------------------
Python CPU oracles in ``fir_analysis`` remain ground truth. Every MLX/NumPy
bulk path must match them bit-for-bit on the same ``FirG`` (see
``tests/unit/test_fir_mlx_oracle.py``).

MLX is for *throughput* on large graphs, never for profitability/ML decisions.
Routing (when to leave CPU) is measured, not guessed — see ``break_even_hint``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional, Sequence, Set, Tuple

from .fir_g import FirG

try:
    import mlx.core as mx

    HAS_MLX = True
except ImportError:  # pragma: no cover
    mx = None  # type: ignore
    HAS_MLX = False

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:  # pragma: no cover
    np = None  # type: ignore
    HAS_NUMPY = False


@dataclass
class BulkReport:
    backend: str
    effects: List[int]
    reachable: Set[int]
    elapsed_ms: float


def _ensure_csr(g: FirG) -> None:
    if not g.call_row_offsets:
        g.build_call_graph_csr()


def _adjacency_numpy(g: FirG):
    """Boolean caller×callee adjacency (edge presence), float32 for matmul."""
    assert HAS_NUMPY
    F = g.num_funcs()
    adj = np.zeros((F, F), dtype=np.float32)
    for f in range(F):
        lo = g.call_row_offsets[f]
        hi = g.call_row_offsets[f + 1]
        for ei in range(lo, hi):
            adj[f, g.call_columns[ei]] = 1.0
    return adj


def _pack_bit_planes(planes: List, *, backend: str) -> List[int]:
    """OR-pack 32 boolean float planes into uint32 effect words."""
    F = len(planes[0]) if planes else 0
    if F == 0:
        return []
    if backend == "numpy":
        out = np.zeros(F, dtype=np.uint32)
        for b, v in enumerate(planes):
            on = (np.asarray(v) > 0.0).astype(np.uint32)
            out |= on << np.uint32(b)
        return [int(x) for x in out.tolist()]
    # mlx → host list via numpy bridge
    assert HAS_MLX and HAS_NUMPY
    out = np.zeros(F, dtype=np.uint32)
    for b, v in enumerate(planes):
        mx.eval(v)
        on = (np.array(v.tolist(), dtype=np.float32) > 0.0).astype(np.uint32)
        out |= on << np.uint32(b)
    return [int(x) for x in out.tolist()]


def _propagate_effects_dense(
    bits0: Sequence[int], adj_np, *, backend: str, max_iters: int = 64
) -> List[int]:
    """Bit-sliced monotone OR: for each bit, v ← max(v, Adj @ v) until fixpoint."""
    F = len(bits0)
    if F == 0:
        return []
    bits_u = [int(b) & 0xFFFFFFFF for b in bits0]

    if backend == "numpy":
        assert HAS_NUMPY
        a = adj_np
        vs = [
            np.array([((bits_u[i] >> b) & 1) for i in range(F)], dtype=np.float32)
            for b in range(32)
        ]
        for _ in range(max_iters):
            changed = False
            nxt = []
            for v in vs:
                prop = a @ v
                merged = (np.maximum(v, prop) > 0.0).astype(np.float32)
                if not np.array_equal(merged, v):
                    changed = True
                nxt.append(merged)
            vs = nxt
            if not changed:
                break
        return _pack_bit_planes(vs, backend="numpy")

    assert backend == "mlx" and HAS_MLX and HAS_NUMPY
    a = mx.array(adj_np)
    vs = [
        mx.array(
            [float((bits_u[i] >> b) & 1) for i in range(F)],
            dtype=mx.float32,
        )
        for b in range(32)
    ]
    for _ in range(max_iters):
        changed = False
        nxt = []
        for v in vs:
            prop = a @ v
            merged = (mx.maximum(v, prop) > 0.0).astype(mx.float32)
            mx.eval(merged)
            if bool(mx.any(merged != v).item()):
                changed = True
            nxt.append(merged)
        vs = nxt
        if not changed:
            break
    return _pack_bit_planes(vs, backend="mlx")


def _reachable_dense(
    adj_np, roots: Sequence[int], *, backend: str, max_iters: int = 64
) -> Set[int]:
    """Forward reachability: R ← max(R, Adjᵀ @ R) from roots."""
    F = adj_np.shape[0]
    if F == 0:
        return set()
    a_t = adj_np.T

    if backend == "numpy":
        r = np.zeros(F, dtype=np.float32)
        for i in roots:
            if 0 <= i < F:
                r[i] = 1.0
        for _ in range(max_iters):
            nxt = (np.maximum(r, a_t @ r) > 0.0).astype(np.float32)
            if np.array_equal(nxt, r):
                r = nxt
                break
            r = nxt
        return {i for i, v in enumerate(r.tolist()) if v > 0.0}

    assert backend == "mlx" and HAS_MLX
    r = mx.zeros((F,), dtype=mx.float32)
    # seed roots (small; host loop is fine)
    seed = np.zeros(F, dtype=np.float32)
    for i in roots:
        if 0 <= i < F:
            seed[i] = 1.0
    r = mx.array(seed)
    at = mx.array(a_t)
    for _ in range(max_iters):
        nxt = mx.maximum(r, at @ r)
        nxt = (nxt > 0.0).astype(mx.float32)
        mx.eval(nxt)
        if bool(mx.all(nxt == r).item()):
            r = nxt
            break
        r = nxt
    return {i for i, v in enumerate(r.tolist()) if v > 0.0}


def resolve_backend(requested: str = "auto", g: Optional[FirG] = None) -> str:
    """Map --device=cpu|numpy|mlx|auto to an implementation name.

    ``auto`` without a graph stays on CPU (safe). Prefer
    ``fir_route.choose_analysis_backend`` when a ``FirG`` is available.
    """
    req = (requested or "auto").lower()
    if req == "cpu":
        return "cpu"
    if req == "numpy":
        if not HAS_NUMPY:
            raise RuntimeError("NumPy not available")
        return "numpy"
    if req == "mlx":
        if not HAS_MLX:
            raise RuntimeError("MLX not available")
        return "mlx"
    if req == "auto":
        if g is not None:
            from .fir_route import choose_analysis_backend

            return choose_analysis_backend(g, "auto")
        # Uncalibrated / no graph → never guess GPU.
        return "cpu"
    raise ValueError(f"unknown device: {requested}")


def propagate_effects_bulk(
    g: FirG, *, backend: str = "auto", max_iters: int = 64
) -> List[int]:
    """Bulk effect OR-propagation. Does not mutate ``g``."""
    _ensure_csr(g)
    be = resolve_backend(backend, g=g)
    if be == "cpu":
        from .fir_analysis import propagate_effects

        saved = list(g.func_effect_bits)
        out = propagate_effects(g, max_iters=max_iters)
        g.func_effect_bits = saved
        return list(out)

    if not HAS_NUMPY:
        raise RuntimeError("bulk backends require NumPy to build adjacency")
    adj = _adjacency_numpy(g)
    bits0 = list(g.func_effect_bits)
    return _propagate_effects_dense(bits0, adj, backend=be, max_iters=max_iters)


def reachable_functions_bulk(
    g: FirG,
    roots: Optional[List[str]] = None,
    *,
    backend: str = "auto",
    max_iters: int = 64,
) -> Set[int]:
    _ensure_csr(g)
    be = resolve_backend(backend, g=g)
    if roots is None:
        roots = ["main"]
    start: List[int] = []
    for name in roots:
        fid = g._func_by_name.get(name)
        if fid is not None:
            start.append(fid)
    if not start and g.num_funcs() > 0:
        start = [0]

    if be == "cpu":
        from .fir_analysis import reachable_functions

        return set(reachable_functions(g, roots))

    if not HAS_NUMPY:
        raise RuntimeError("bulk backends require NumPy to build adjacency")
    adj = _adjacency_numpy(g)
    return _reachable_dense(adj, start, backend=be, max_iters=max_iters)


def analyse_bulk(g: FirG, *, backend: str = "auto") -> BulkReport:
    """Run bulk effect + reachability; leave ``g.func_effect_bits`` unchanged."""
    be = resolve_backend(backend, g=g)
    t0 = time.perf_counter()
    effects = propagate_effects_bulk(g, backend=be)
    live = reachable_functions_bulk(g, backend=be)
    elapsed = (time.perf_counter() - t0) * 1000.0
    return BulkReport(backend=be, effects=effects, reachable=live, elapsed_ms=elapsed)


def break_even_hint(
    g: FirG,
    *,
    repeats: int = 5,
) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Rough wall-time compare CPU vs best bulk backend (ms). Not a product threshold.

    Returns (cpu_ms, bulk_ms, bulk_name) or Nones if bulk unavailable.
    """
    from .fir_analysis import propagate_effects, reachable_functions

    _ensure_csr(g)
    saved = list(g.func_effect_bits)

    def run_cpu() -> None:
        g.func_effect_bits = list(saved)
        propagate_effects(g)
        reachable_functions(g)
        g.func_effect_bits = list(saved)

    t0 = time.perf_counter()
    for _ in range(repeats):
        run_cpu()
    cpu_ms = (time.perf_counter() - t0) * 1000.0 / repeats

    bulk_name = "mlx" if HAS_MLX else ("numpy" if HAS_NUMPY else None)
    if bulk_name is None:
        return cpu_ms, None, None

    t1 = time.perf_counter()
    for _ in range(repeats):
        analyse_bulk(g, backend=bulk_name)
    bulk_ms = (time.perf_counter() - t1) * 1000.0 / repeats
    return cpu_ms, bulk_ms, bulk_name
