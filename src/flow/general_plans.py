"""Implementation registry for non-sorting constructs (#147).

Generalises the intent/implementation/cost split beyond sort and search.
The selector in plan_selector.py is already construct-agnostic; this module
registers implementations for:

* `matmul`: naive triple-loop vs cache-blocked tiling.
  The constraint that flips the choice is matrix dimension. Small matrices
  use naive (less loop overhead). Large matrices use blocked (better cache
  locality).

* `reduce`: sequential scan vs parallel-tree reduction.
  The constraint that flips is element count plus a `prefer parallel`
  soft preference. Small arrays use sequential. Large arrays, or any array
  with `prefer parallel`, use the tree reduction.

Fact keys used by these implementations:

    n            element count (one dimension for matmul, total for reduce)
    prefer       soft preference string: "latency", "energy", "memory", "parallel"
    require_*    hard constraints: require_memory_bytes, require_latency_budget
    backend      "cpu", "simd", "gpu" (from policies)
"""

from __future__ import annotations

from typing import Optional

from .plan_selector import Facts, Implementation, register

__all__ = ["MATMUL_BLOCK_THRESHOLD", "REDUCE_TREE_THRESHOLD"]


# Below this matrix dimension, the naive triple loop wins. The blocked
# version pays loop overhead for the tile boundaries that is not amortised
# when the whole matrix fits in L1.
MATMUL_BLOCK_THRESHOLD = 64

# Below this element count, a sequential scan is cheaper than a tree
# reduction. The tree pays for log2(n) passes with extra memory traffic.
REDUCE_TREE_THRESHOLD = 1024


# ---------------------------------------------------------------------------
# matmul
# ---------------------------------------------------------------------------


def _matmul_naive_applicable(facts: Facts) -> Optional[str]:
    require_memory = facts.get("require_memory_bytes")
    if require_memory is not None:
        # Naive matmul uses no scratch.
        if require_memory < 0:
            return f"memory requirement {require_memory} is negative"
    backend = facts.get("backend", "cpu")
    if backend == "gpu":
        return "naive triple loop has no GPU lowering"
    return None


def _matmul_naive_cost(facts: Facts) -> float:
    n = float(facts.n)
    return n * n * n


register(
    Implementation(
        name="naive",
        construct="matmul",
        summary="triple nested loop, no scratch, wins when the matrix fits in L1",
        applicable=_matmul_naive_applicable,
        cost=_matmul_naive_cost,
        scratch=lambda f: 0,
        rank=10,
        resolution="use a smaller matrix or allow scratch for the blocked version",
    )
)


def _matmul_blocked_applicable(facts: Facts) -> Optional[str]:
    require_memory = facts.get("require_memory_bytes")
    if require_memory is not None:
        # Blocked matmul needs a tile buffer (block_size^2 * 8 bytes).
        block = 32
        need = block * block * 8
        if need > require_memory:
            return (
                f"tile buffer needs {need} bytes but the site requires "
                f"at most {require_memory} bytes of scratch"
            )
    backend = facts.get("backend", "cpu")
    if backend == "gpu":
        return "blocked tiling has no GPU lowering (use a GPU-native plan)"
    return None


def _matmul_blocked_cost(facts: Facts) -> float:
    n = float(facts.n)
    if n < MATMUL_BLOCK_THRESHOLD:
        # Loop overhead dominates when the matrix is small.
        return n * n * n * 1.3
    # Model cache benefit: blocked version pays ~0.7x the naive cost
    # because of fewer cache misses.
    return n * n * n * 0.7


def _matmul_blocked_scratch(facts: Facts) -> int:
    block = 32
    return block * block * 8


register(
    Implementation(
        name="blocked",
        construct="matmul",
        summary="cache-blocked tiling with a 32x32 tile buffer, wins for large matrices",
        applicable=_matmul_blocked_applicable,
        cost=_matmul_blocked_cost,
        scratch=_matmul_blocked_scratch,
        rank=11,
        resolution="allow more scratch memory or use a smaller matrix",
    )
)


# ---------------------------------------------------------------------------
# reduce
# ---------------------------------------------------------------------------


def _reduce_sequential_applicable(facts: Facts) -> Optional[str]:
    backend = facts.get("backend", "cpu")
    if backend == "gpu":
        return "sequential scan has no GPU lowering"
    return None


def _reduce_sequential_cost(facts: Facts) -> float:
    return float(facts.n)


register(
    Implementation(
        name="sequential",
        construct="reduce",
        summary="single-pass accumulation from index 0, no scratch",
        applicable=_reduce_sequential_applicable,
        cost=_reduce_sequential_cost,
        scratch=lambda f: 0,
        rank=20,
        resolution="use a larger array or add `prefer parallel`",
    )
)


def _reduce_tree_applicable(facts: Facts) -> Optional[str]:
    backend = facts.get("backend", "cpu")
    if backend == "gpu":
        return "tree reduction has no GPU lowering (use a GPU-native plan)"
    return None


def _reduce_tree_cost(facts: Facts) -> float:
    n = float(facts.n)
    prefer = facts.get("prefer", "")
    if prefer == "parallel":
        # Caller asked for parallel. The tree is log2(n) depth, but the
        # total work is still n. Model it as cheaper because the caller
        # probably has threads to overlap the passes.
        return n * 0.8
    if n < REDUCE_TREE_THRESHOLD:
        # Tree overhead (extra passes, memory traffic) is not amortised.
        return n * 1.5
    # For large n, the tree wins on pipeline utilisation: the sequential
    # scan has one long dependency chain, while the tree has log2(n) short
    # ones that the CPU can overlap.
    return n * 0.85


def _reduce_tree_scratch(facts: Facts) -> int:
    # Tree reduction needs a second buffer of the same size.
    elem_bytes = int(facts.get("elem_bytes", 8))
    return facts.n * elem_bytes


register(
    Implementation(
        name="parallel_tree",
        construct="reduce",
        summary="log2(n)-depth tree reduction with a second buffer, wins for large n or `prefer parallel`",
        applicable=_reduce_tree_applicable,
        cost=_reduce_tree_cost,
        scratch=_reduce_tree_scratch,
        rank=21,
        resolution="use a larger array or add `prefer parallel`",
    )
)
