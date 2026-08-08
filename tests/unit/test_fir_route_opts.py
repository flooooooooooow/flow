"""FIR-G Phase 3–4: routing calibration + opt candidates."""

from __future__ import annotations

from pathlib import Path

import pytest

from flow.fir_analysis import analyse
from flow.fir_cli import build_fir_g
from flow.fir_g import EFF_IO
from flow.fir_opts import discover_candidates
from flow.fir_route import (
    NEVER_BULK,
    RouteThresholds,
    calibrate_routing,
    choose_analysis_backend,
    load_thresholds,
    save_thresholds,
    synthetic_call_graph,
)


def test_uncalibrated_auto_stays_cpu(tmp_path: Path):
    g = synthetic_call_graph(32)
    missing = tmp_path / "no_such_route.json"
    assert choose_analysis_backend(g, "auto", thresholds_path=missing) == "cpu"


def test_thresholds_force_bulk_when_large(tmp_path: Path):
    g = synthetic_call_graph(40)
    th = RouteThresholds(
        bulk_backend="numpy",
        min_funcs=10,
        min_edges=10,
        host="test",
        samples=[],
    )
    path = tmp_path / "route.json"
    save_thresholds(th, path)
    loaded = load_thresholds(path)
    assert loaded is not None
    assert choose_analysis_backend(g, "auto", thresholds=loaded) == "numpy"
    tiny = synthetic_call_graph(2)
    # synthetic_call_graph(2) → f0,f1,main = 3 funcs; still may exceed min_funcs=10? No, 3 < 10
    assert choose_analysis_backend(tiny, "auto", thresholds=loaded) == "cpu"


def test_explicit_mlx_or_cpu():
    g = synthetic_call_graph(8)
    assert choose_analysis_backend(g, "cpu") == "cpu"
    # numpy always available in CI for this project
    be = choose_analysis_backend(g, "numpy")
    assert be == "numpy"


def test_calibrate_writes_file(tmp_path: Path):
    # Small/fast sweep for unit test
    th = calibrate_routing(sizes=(8, 16), repeats=2)
    path = tmp_path / "fir_g_route.json"
    save_thresholds(th, path)
    loaded = load_thresholds(path)
    assert loaded is not None
    assert loaded.bulk_backend in ("mlx", "numpy", "cpu")
    assert len(loaded.samples) == 2
    assert loaded.min_funcs >= 1


def test_never_bulk_stays_cpu():
    g = synthetic_call_graph(100)
    th = RouteThresholds(
        bulk_backend="mlx",
        min_funcs=NEVER_BULK,
        min_edges=NEVER_BULK,
    )
    assert choose_analysis_backend(g, "auto", thresholds=th) == "cpu"


def test_dead_elim_candidate(tmp_path: Path):
    src = tmp_path / "dead.flow"
    src.write_text(
        """
function dead() -> i32 { return 1 }
function helper() -> i32 { return 2 }
function main() -> i32 {
    return helper()
}
"""
    )
    g = build_fir_g(str(src))
    analyse(g)
    cands = discover_candidates(g)
    kinds = {(c.kind, c.target) for c in cands}
    assert ("dead_elim", "dead") in kinds
    assert ("dead_elim", "helper") not in kinds
    assert ("dead_elim", "main") not in kinds


def test_inline_candidate_small_pure(tmp_path: Path):
    src = tmp_path / "inl.flow"
    src.write_text(
        """
function add1(x: i32) -> i32 {
    return x
}
function main() -> i32 {
    return add1(1)
}
"""
    )
    g = build_fir_g(str(src))
    analyse(g)
    cands = discover_candidates(g)
    inline = [c for c in cands if c.kind == "inline" and c.target == "add1"]
    assert inline, f"expected inline candidate, got {cands}"
    assert inline[0].caller == "main"
    assert inline[0].score > 0


def test_synthetic_graph_has_io_root():
    g = synthetic_call_graph(5)
    assert g.func_effect_bits[g._func_by_name["f0"]] & EFF_IO
    assert len(g.call_columns) > 0
