"""FIR-G Phase 2: bulk MLX/NumPy analyses must match CPU oracles."""

from __future__ import annotations

from pathlib import Path

import pytest

from flow.fir_analysis import propagate_effects, reachable_functions
from flow.fir_cli import build_fir_g
from flow.fir_g import EFF_IO, FirG, OpCode
from flow.fir_mlx import (
    HAS_MLX,
    HAS_NUMPY,
    analyse_bulk,
    propagate_effects_bulk,
    reachable_functions_bulk,
    resolve_backend,
)


pytestmark = pytest.mark.skipif(not HAS_NUMPY, reason="NumPy required for bulk FIR-G")


def _chain_program(n: int, *, dirty_leaf: bool = True) -> str:
    """main → f_{n-1} → … → f_0; f_0 optionally does IO via printf."""
    lines = []
    if dirty_leaf:
        lines.append(
            """
extern {
    function printf(fmt: string, val: i32) -> i32
}
"""
        )
        lines.append(
            """
function f_0() -> i32 {
    return printf("x", 1)
}
"""
        )
    else:
        lines.append(
            """
function f_0() -> i32 {
    return 1
}
"""
        )
    for i in range(1, n):
        lines.append(
            f"""
function f_{i}() -> i32 {{
    return f_{i - 1}()
}}
"""
        )
    lines.append(
        f"""
function main() -> i32 {{
    return f_{n - 1}()
}}
function dead_orphan() -> i32 {{
    return 0
}}
"""
    )
    return "\n".join(lines)


def _assert_oracle_match(g: FirG, backend: str) -> None:
    saved = list(g.func_effect_bits)
    cpu_bits = propagate_effects(g)
    cpu_live = reachable_functions(g)
    g.func_effect_bits = list(saved)

    bulk_bits = propagate_effects_bulk(g, backend=backend)
    bulk_live = reachable_functions_bulk(g, backend=backend)

    assert bulk_bits == list(cpu_bits), f"{backend} effects diverged"
    assert bulk_live == set(cpu_live), f"{backend} reachability diverged"


def test_numpy_matches_cpu_chain(tmp_path: Path):
    src = tmp_path / "chain.flow"
    src.write_text(_chain_program(8))
    g = build_fir_g(str(src))
    _assert_oracle_match(g, "numpy")
    # IO should reach main through the chain
    bits = propagate_effects_bulk(g, backend="numpy")
    assert bits[g._func_by_name["main"]] & EFF_IO


def test_numpy_matches_cpu_hello():
    root = Path(__file__).resolve().parents[2]
    hello = root / "examples" / "basics" / "hello_world.flow"
    if not hello.exists():
        pytest.skip("hello_world.flow missing")
    g = build_fir_g(str(hello))
    _assert_oracle_match(g, "numpy")


@pytest.mark.skipif(not HAS_MLX, reason="MLX not installed")
def test_mlx_matches_cpu_chain(tmp_path: Path):
    src = tmp_path / "chain_mlx.flow"
    src.write_text(_chain_program(12))
    g = build_fir_g(str(src))
    _assert_oracle_match(g, "mlx")


@pytest.mark.skipif(not HAS_MLX, reason="MLX not installed")
def test_analyse_bulk_mlx_report(tmp_path: Path):
    src = tmp_path / "bulk.flow"
    src.write_text(_chain_program(5))
    g = build_fir_g(str(src))
    saved = list(g.func_effect_bits)
    cpu_bits = list(propagate_effects(g))
    cpu_live = set(reachable_functions(g))
    g.func_effect_bits = saved

    rep = analyse_bulk(g, backend="mlx")
    assert rep.backend == "mlx"
    assert rep.effects == cpu_bits
    assert rep.reachable == cpu_live
    assert g.func_effect_bits == saved  # non-mutating


def test_resolve_backend_cpu():
    assert resolve_backend("cpu") == "cpu"


def test_synthetic_dense_graph_numpy():
    """Hand-built FirG (no parser) — larger fan-out for adjacency matmul path."""
    g = FirG()
    n = 40
    ids = [g.add_function(f"f{i}") for i in range(n)]
    main = g.add_function("main")
    # star: main → each f_i; f_i → f_0; f_0 dirty
    g.func_effect_bits[ids[0]] = EFF_IO
    # Use add_op CALL to build edges the graphify way
    b_main = g.add_block(main)
    for i in range(n):
        g.add_op(OpCode.CALL, main, b_main, callee=ids[i])
    for i in range(1, n):
        bi = g.add_block(ids[i])
        g.add_op(OpCode.CALL, ids[i], bi, callee=ids[0])
    g.build_call_graph_csr()
    _assert_oracle_match(g, "numpy")
    bits = propagate_effects_bulk(g, backend="numpy")
    assert bits[main] & EFF_IO
    live = reachable_functions_bulk(g, backend="numpy")
    assert main in live and ids[0] in live
