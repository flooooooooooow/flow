"""Tests for multi-implementation selection beyond sort (#147).

Tests that the general plan selector picks the right implementation for
non-sort constructs (matmul, reduce) and that require/prefer constraints
flip the choice.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

# Import ordering_plans first so the sort/search registry is populated.
from flow import ordering_plans  # noqa: F401
from flow import general_plans  # noqa: F401
from flow.plan_selector import Facts, select, NoImplementation
from flow.constraints import parse_require, parse_prefer, constraints_to_facts


# ---------------------------------------------------------------------------
# matmul
# ---------------------------------------------------------------------------


def test_matmul_small_picks_naive():
    facts = Facts(construct="matmul", n=16, data={"backend": "cpu"})
    sel = select(facts, location="test", detail="small matmul")
    assert sel.chosen == "naive"


def test_matmul_large_picks_blocked():
    facts = Facts(construct="matmul", n=256, data={"backend": "cpu"})
    sel = select(facts, location="test", detail="large matmul")
    assert sel.chosen == "blocked"


def test_matmul_require_memory_rejects_blocked():
    # Blocked needs 32*32*8 = 8192 bytes of scratch.
    # require(memory < 4096) should reject it.
    facts = Facts(
        construct="matmul",
        n=256,
        data={"backend": "cpu", "require_memory_bytes": 4096},
    )
    sel = select(facts, location="test", detail="memory-constrained matmul")
    assert sel.chosen == "naive"
    # blocked should be rejected
    blocked_cand = [c for c in sel.candidates if c.name == "blocked"][0]
    assert blocked_cand.rejected is not None
    assert "4096" in blocked_cand.rejected


def test_matmul_require_memory_allows_blocked_when_sufficient():
    facts = Facts(
        construct="matmul",
        n=256,
        data={"backend": "cpu", "require_memory_bytes": 16384},
    )
    sel = select(facts, location="test", detail="memory-sufficient matmul")
    assert sel.chosen == "blocked"


def test_matmul_gpu_rejects_both():
    facts = Facts(construct="matmul", n=256, data={"backend": "gpu"})
    try:
        select(facts, location="test", detail="gpu matmul")
        assert False, "should have raised NoImplementation"
    except NoImplementation:
        pass


# ---------------------------------------------------------------------------
# reduce
# ---------------------------------------------------------------------------


def test_reduce_small_picks_sequential():
    facts = Facts(construct="reduce", n=100, data={"backend": "cpu"})
    sel = select(facts, location="test", detail="small reduce")
    assert sel.chosen == "sequential"


def test_reduce_large_picks_tree():
    facts = Facts(construct="reduce", n=10000, data={"backend": "cpu"})
    sel = select(facts, location="test", detail="large reduce")
    assert sel.chosen == "parallel_tree"


def test_reduce_prefer_parallel_flips_small():
    # Small array, but prefer(parallel) should pick the tree.
    facts = Facts(
        construct="reduce",
        n=100,
        data={"backend": "cpu", "prefer": "parallel"},
    )
    sel = select(facts, location="test", detail="small reduce prefer parallel")
    assert sel.chosen == "parallel_tree"


def test_reduce_no_prefer_small_stays_sequential():
    facts = Facts(construct="reduce", n=100, data={"backend": "cpu"})
    sel = select(facts, location="test", detail="small reduce no prefer")
    assert sel.chosen == "sequential"


# ---------------------------------------------------------------------------
# constraints parser
# ---------------------------------------------------------------------------


def test_parse_require_memory():
    result = parse_require("require(memory < 4096)")
    assert result is not None
    resource, op, value = result
    assert resource == "memory"
    assert op == "<"
    assert value == 4096


def test_parse_require_scratch():
    result = parse_require("require(scratch <= 8192)")
    assert result is not None
    resource, op, value = result
    assert resource == "scratch"
    assert op == "<="
    assert value == 8192


def test_parse_require_no_match():
    assert parse_require("not a require") is None


def test_parse_prefer():
    assert parse_prefer("prefer(parallel)") == "parallel"
    assert parse_prefer("prefer(latency)") == "latency"
    assert parse_prefer("not a prefer") is None


def test_constraints_to_facts_require():
    data = constraints_to_facts(requires=["require(memory < 4096)"])
    assert data["require_memory_bytes"] == 4096


def test_constraints_to_facts_prefer():
    data = constraints_to_facts(prefers=["prefer(parallel)"])
    assert data["prefer"] == "parallel"


def test_constraints_to_facts_tightest_wins():
    data = constraints_to_facts(
        requires=["require(memory < 8192)", "require(memory < 4096)"]
    )
    assert data["require_memory_bytes"] == 4096


def test_constraints_to_facts_empty():
    data = constraints_to_facts()
    assert data == {}


# ---------------------------------------------------------------------------
# integration: constraints flip matmul choice
# ---------------------------------------------------------------------------


def test_constraint_flips_matmul_choice():
    """Large matmul picks blocked, but require(memory < 4096) flips to naive."""
    # Without constraint: blocked wins
    facts = Facts(construct="matmul", n=256, data={"backend": "cpu"})
    sel = select(facts)
    assert sel.chosen == "blocked"

    # With constraint: naive wins
    constraint_data = constraints_to_facts(requires=["require(memory < 4096)"])
    facts = Facts(construct="matmul", n=256, data={"backend": "cpu", **constraint_data})
    sel = select(facts)
    assert sel.chosen == "naive"


def test_prefer_flips_reduce_choice():
    """Small reduce picks sequential, but prefer(parallel) flips to tree."""
    # Without prefer: sequential wins
    facts = Facts(construct="reduce", n=100, data={"backend": "cpu"})
    sel = select(facts)
    assert sel.chosen == "sequential"

    # With prefer: tree wins
    constraint_data = constraints_to_facts(prefers=["prefer(parallel)"])
    facts = Facts(construct="reduce", n=100, data={"backend": "cpu", **constraint_data})
    sel = select(facts)
    assert sel.chosen == "parallel_tree"


# ---------------------------------------------------------------------------
# explain output
# ---------------------------------------------------------------------------


def test_explain_includes_non_sort_constructs():
    from flow.plan_selector import format_selections
    facts = Facts(construct="matmul", n=256, data={"backend": "cpu"})
    sel = select(facts, location="test.flow:10", detail="256x256 f64")
    report = format_selections([sel], "test.flow")
    assert "matmul" in report
    assert "blocked" in report
    assert "naive" in report
    assert "CHOSEN" in report
