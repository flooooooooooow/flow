#!/usr/bin/env python3
"""FIR-G Phase 3: measured CPU vs bulk analysis routing.

Thresholds are never guessed. ``calibrate_routing`` sweeps synthetic call-graph
sizes, times CPU vs MLX/NumPy, and persists the first size where bulk wins.
Uncalibrated ``--device=auto`` stays on CPU (safe default).
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from .fir_g import EFF_IO, FirG, OpCode

try:
    from .fir_mlx import HAS_MLX, HAS_NUMPY, analyse_bulk
except ImportError:  # pragma: no cover
    HAS_MLX = False
    HAS_NUMPY = False
    analyse_bulk = None  # type: ignore

DEFAULT_SIZES: tuple = (8, 16, 32, 64, 128, 256, 512, 1024)
# If bulk never wins in the sweep, keep auto on CPU forever for this machine.
NEVER_BULK = 10**9


@dataclass
class Sample:
    n_funcs: int
    n_edges: int
    cpu_ms: float
    bulk_ms: float
    bulk_backend: str


@dataclass
class RouteThresholds:
    bulk_backend: str
    min_funcs: int
    min_edges: int
    host: str = ""
    samples: List[Dict[str, Any]] = field(default_factory=list)

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, data: dict) -> "RouteThresholds":
        return cls(
            bulk_backend=str(data["bulk_backend"]),
            min_funcs=int(data["min_funcs"]),
            min_edges=int(data.get("min_edges", data["min_funcs"])),
            host=str(data.get("host", "")),
            samples=list(data.get("samples") or []),
        )


def default_thresholds_path() -> Path:
    env = os.environ.get("FLOW_FIR_G_THRESHOLDS")
    if env:
        return Path(env)
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg) / "flow" / "fir_g_route.json"
    return Path.home() / ".cache" / "flow" / "fir_g_route.json"


def load_thresholds(path: Optional[Path] = None) -> Optional[RouteThresholds]:
    p = path or default_thresholds_path()
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text())
        return RouteThresholds.from_json(data)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


def save_thresholds(th: RouteThresholds, path: Optional[Path] = None) -> Path:
    p = path or default_thresholds_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(th.to_json(), indent=2) + "\n")
    return p


def synthetic_call_graph(n_funcs: int, *, fanout: int = 2) -> FirG:
    """Build a dense-ish synthetic FirG for calibration (no parser).

    Layout: ``main`` calls ``f0..f{n-1}``; each ``fi`` (i>0) calls ``f0`` and
    up to ``fanout`` earlier siblings — enough edges for Adj matmul cost to show.
    ``f0`` is marked IO so effect propagation has work to do.
    """
    g = FirG()
    if n_funcs < 1:
        return g
    ids = [g.add_function(f"f{i}") for i in range(n_funcs)]
    main = g.add_function("main")
    g.func_effect_bits[ids[0]] = EFF_IO
    b_main = g.add_block(main)
    for i in range(n_funcs):
        g.add_op(OpCode.CALL, main, b_main, callee=ids[i])
    for i in range(1, n_funcs):
        bi = g.add_block(ids[i])
        g.add_op(OpCode.CALL, ids[i], bi, callee=ids[0])
        for k in range(1, min(fanout, i) + 1):
            g.add_op(OpCode.CALL, ids[i], bi, callee=ids[i - k])
    g.build_call_graph_csr()
    return g


def _best_bulk_name() -> Optional[str]:
    if HAS_MLX:
        return "mlx"
    if HAS_NUMPY:
        return "numpy"
    return None


def _time_cpu(g: FirG, repeats: int) -> float:
    from .fir_analysis import propagate_effects, reachable_functions

    saved = list(g.func_effect_bits)

    def once() -> None:
        g.func_effect_bits = list(saved)
        propagate_effects(g)
        reachable_functions(g)
        g.func_effect_bits = list(saved)

    once()  # warmup
    t0 = time.perf_counter()
    for _ in range(repeats):
        once()
    return (time.perf_counter() - t0) * 1000.0 / repeats


def _time_bulk(g: FirG, backend: str, repeats: int) -> float:
    assert analyse_bulk is not None
    analyse_bulk(g, backend=backend)  # warmup
    t0 = time.perf_counter()
    for _ in range(repeats):
        analyse_bulk(g, backend=backend)
    return (time.perf_counter() - t0) * 1000.0 / repeats


def calibrate_routing(
    *,
    sizes: Sequence[int] = DEFAULT_SIZES,
    repeats: int = 5,
    margin: float = 1.05,
) -> RouteThresholds:
    """Sweep sizes; first N where bulk_ms * margin < cpu_ms becomes the threshold.

    ``margin`` requires bulk to beat CPU by ~5% so noise does not flip routing.
    """
    bulk = _best_bulk_name()
    if bulk is None:
        return RouteThresholds(
            bulk_backend="cpu",
            min_funcs=NEVER_BULK,
            min_edges=NEVER_BULK,
            host=_host_tag(),
            samples=[],
        )

    samples: List[Sample] = []
    min_funcs = NEVER_BULK
    min_edges = NEVER_BULK
    for n in sizes:
        g = synthetic_call_graph(int(n))
        cpu_ms = _time_cpu(g, repeats)
        bulk_ms = _time_bulk(g, bulk, repeats)
        n_edges = len(g.call_columns)
        samples.append(
            Sample(
                n_funcs=g.num_funcs(),
                n_edges=n_edges,
                cpu_ms=cpu_ms,
                bulk_ms=bulk_ms,
                bulk_backend=bulk,
            )
        )
        if min_funcs == NEVER_BULK and bulk_ms * margin < cpu_ms:
            min_funcs = g.num_funcs()
            min_edges = n_edges

    return RouteThresholds(
        bulk_backend=bulk,
        min_funcs=min_funcs,
        min_edges=min_edges,
        host=_host_tag(),
        samples=[asdict(s) for s in samples],
    )


def _host_tag() -> str:
    import platform

    return f"{platform.system()}-{platform.machine()}-mlx={HAS_MLX}-np={HAS_NUMPY}"


def graph_stats(g: FirG) -> tuple:
    if not g.call_row_offsets:
        g.build_call_graph_csr()
    return g.num_funcs(), len(g.call_columns)


def choose_analysis_backend(
    g: FirG,
    requested: str = "auto",
    *,
    thresholds: Optional[RouteThresholds] = None,
    thresholds_path: Optional[Path] = None,
) -> str:
    """Pick cpu|numpy|mlx. ``auto`` uses measured thresholds; uncalibrated → cpu."""
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
    if req != "auto":
        raise ValueError(f"unknown device: {requested}")

    th = thresholds if thresholds is not None else load_thresholds(thresholds_path)
    if th is None or th.min_funcs >= NEVER_BULK:
        return "cpu"
    n_funcs, n_edges = graph_stats(g)
    if n_funcs >= th.min_funcs or n_edges >= th.min_edges:
        be = th.bulk_backend
        if be == "mlx" and not HAS_MLX:
            return "numpy" if HAS_NUMPY else "cpu"
        if be == "numpy" and not HAS_NUMPY:
            return "cpu"
        return be
    return "cpu"
