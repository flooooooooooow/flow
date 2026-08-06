"""Unit tests for cost-based implementation selection (issues #145, #146, #147).

The selector is construct-agnostic, so the first half of this file tests it
against implementations invented here. The second half tests the sort and
search implementations Flow actually registers.
"""

import pytest

from flow import ordering_plans  # noqa: F401  (registers sort / search impls)
from flow.plan_selector import (
    Facts,
    Implementation,
    NoImplementation,
    SCRATCH_BUDGET_BYTES,
    Selection,
    format_selections,
    implementations_for,
    register,
    select,
)


# ---------------------------------------------------------------------------
# the selector itself
# ---------------------------------------------------------------------------


@pytest.fixture
def toy():
    """Three implementations of a made-up construct, registered fresh."""
    register(
        Implementation(
            name="cheap_but_picky",
            construct="_toy",
            summary="only works on even n",
            applicable=lambda f: None if f.n % 2 == 0 else "n is odd",
            cost=lambda f: 1.0,
        )
    )
    register(
        Implementation(
            name="greedy",
            construct="_toy",
            summary="wants more scratch than the budget allows",
            applicable=lambda f: None,
            cost=lambda f: 0.5,
            scratch=lambda f: SCRATCH_BUDGET_BYTES + 1,
        )
    )
    register(
        Implementation(
            name="always",
            construct="_toy",
            summary="the fallback",
            applicable=lambda f: None,
            cost=lambda f: 10.0,
        )
    )
    yield
    implementations_for("_toy").clear()


def test_cheapest_applicable_wins(toy):
    sel = select(Facts("_toy", 4))
    assert sel.chosen == "cheap_but_picky"


def test_inapplicable_candidate_records_its_constraint(toy):
    sel = select(Facts("_toy", 5))
    assert sel.chosen == "always"
    rejected = {c.name: c.rejected for c in sel.candidates if c.rejected}
    assert rejected["cheap_but_picky"] == "n is odd"


def test_scratch_budget_rejects_before_cost(toy):
    sel = select(Facts("_toy", 4))
    greedy = next(c for c in sel.candidates if c.name == "greedy")
    assert greedy.cost is None
    assert "exceeds" in greedy.rejected
    assert "scratch budget" in greedy.rejected


def test_every_candidate_appears_in_the_record(toy):
    sel = select(Facts("_toy", 5))
    assert {c.name for c in sel.candidates} == {
        "cheap_but_picky",
        "greedy",
        "always",
    }


def test_ties_break_on_rank():
    register(
        Implementation(
            name="second",
            construct="_tie",
            summary="",
            applicable=lambda f: None,
            cost=lambda f: 3.0,
            rank=9,
        )
    )
    register(
        Implementation(
            name="first",
            construct="_tie",
            summary="",
            applicable=lambda f: None,
            cost=lambda f: 3.0,
            rank=1,
        )
    )
    try:
        sel = select(Facts("_tie", 1))
        assert sel.chosen == "first"
        assert "tie" in sel.reason
    finally:
        implementations_for("_tie").clear()


def test_no_applicable_implementation_raises():
    register(
        Implementation(
            name="never",
            construct="_empty",
            summary="",
            applicable=lambda f: "never applies",
            cost=lambda f: 1.0,
        )
    )
    try:
        with pytest.raises(NoImplementation):
            select(Facts("_empty", 1), location="line 1")
    finally:
        implementations_for("_empty").clear()


def test_unknown_construct_raises():
    with pytest.raises(NoImplementation):
        select(Facts("_not_registered", 1))


# ---------------------------------------------------------------------------
# the sort implementations
# ---------------------------------------------------------------------------


def sort_facts(n=100, **over):
    data = {
        "elem": "i32",
        "elem_kind": "int",
        "elem_bytes": 4,
        "keys": 0,
        "stable": True,
        "unique": False,
        "direction": "asc",
        "input_order": "unknown",
        "key_range": None,
        "expect_runs": "unknown",
        "pinned": None,
    }
    data.update(over)
    return Facts("sort", n, data)


def test_proven_sorted_input_skips_the_sort():
    sel = select(sort_facts(input_order="asc_strict"))
    assert sel.chosen == "already_ordered"
    assert sel.chosen_candidate().cost == 0.0


def test_proven_reversed_input_reverses():
    sel = select(sort_facts(input_order="desc_strict"))
    assert sel.chosen == "reverse_in_place"


def test_non_strict_reverse_is_refused_for_stability():
    sel = select(sort_facts(input_order="desc"))
    assert sel.chosen != "reverse_in_place"
    reason = next(
        c.rejected for c in sel.candidates if c.name == "reverse_in_place"
    )
    assert "stability" in reason


def test_unique_keeps_the_sort_even_when_already_ordered():
    sel = select(sort_facts(input_order="asc_strict", unique=True))
    assert sel.chosen != "already_ordered"
    reason = next(c.rejected for c in sel.candidates if c.name == "already_ordered")
    assert "unique" in reason


def test_bounded_non_negative_range_picks_counting():
    sel = select(sort_facts(n=4096, key_range=[0, 255]))
    assert sel.chosen == "counting"


def test_negative_range_rejects_counting():
    sel = select(sort_facts(n=4096, key_range=[-1, 255]))
    assert sel.chosen != "counting"
    reason = next(c.rejected for c in sel.candidates if c.name == "counting")
    assert "negative" in reason


def test_wide_range_rejects_counting():
    sel = select(sort_facts(n=4096, key_range=[0, 1 << 20]))
    reason = next(c.rejected for c in sel.candidates if c.name == "counting")
    assert "bucket" in reason


def test_float_elements_reject_counting():
    sel = select(sort_facts(n=4096, elem="f64", elem_kind="float", elem_bytes=8))
    reason = next(c.rejected for c in sel.candidates if c.name == "counting")
    assert "bounded integer" in reason


def test_small_arrays_pick_insertion():
    assert select(sort_facts(n=8)).chosen == "insertion"


def test_large_arrays_pick_the_run_detecting_merge():
    # It measured faster than the plain bottom-up merge on every input shape
    # in benchmarks/ordering, unstructured input included, so it is the
    # default above the insertion crossover.
    assert select(sort_facts(n=4096)).chosen == "natural_merge"


def test_adaptive_policy_widens_the_run_detector_margin():
    plain = select(sort_facts(n=4096))
    adaptive = select(sort_facts(n=4096, expect_runs="few"))
    assert adaptive.chosen == plain.chosen == "natural_merge"
    assert adaptive.chosen_candidate().cost < plain.chosen_candidate().cost


def test_the_run_detector_is_not_worth_it_on_short_arrays():
    sel = select(sort_facts(n=12))
    assert sel.chosen == "insertion"
    reason = next(c.rejected for c in sel.candidates if c.name == "natural_merge")
    assert "run-detection floor" in reason


def test_general_policy_pins_the_general_plan():
    sel = select(sort_facts(n=8, pinned="bottom_up_merge"))
    assert sel.chosen == "bottom_up_merge"
    reason = next(c.rejected for c in sel.candidates if c.name == "insertion")
    assert "pinned" in reason


def test_merge_scratch_budget_rejects_huge_arrays():
    n = SCRATCH_BUDGET_BYTES  # 8 bytes each blows the budget eight times over
    sel = select(sort_facts(n=n, elem="f64", elem_kind="float", elem_bytes=8))
    for name in ("natural_merge", "bottom_up_merge"):
        reason = next(c.rejected for c in sel.candidates if c.name == name)
        assert "scratch budget" in reason
    assert sel.chosen == "insertion"


# ---------------------------------------------------------------------------
# the search implementations
# ---------------------------------------------------------------------------


def search_facts(n=100, order="unknown"):
    return Facts("search", n, {"elem": "i32", "elem_kind": "int", "input_order": order})


def test_search_falls_back_to_a_linear_scan():
    sel = select(search_facts())
    assert sel.chosen == "linear_scan"
    reason = next(c.rejected for c in sel.candidates if c.name == "binary_search")
    assert "ascending" in reason


def test_sorted_input_flips_search_to_binary():
    assert select(search_facts(order="asc")).chosen == "binary_search"
    assert select(search_facts(order="asc_strict")).chosen == "binary_search"


def test_descending_input_does_not_enable_binary_search():
    assert select(search_facts(order="desc")).chosen == "linear_scan"


# ---------------------------------------------------------------------------
# the report
# ---------------------------------------------------------------------------


def test_report_names_the_choice_and_every_rejection():
    sel = select(
        sort_facts(n=4096, expect_runs="few"),
        location="line 7 in main()",
        detail="array<i32, 4096>",
    )
    text = format_selections([sel], source="prog.flow")
    assert "Compilation plan for prog.flow" in text
    assert "line 7 in main()" in text
    assert "natural_merge" in text
    assert "CHOSEN" in text
    assert "rejected:" in text
    # Every implementation shows up, chosen or not.
    for impl in implementations_for("sort"):
        assert impl.name in text


def test_report_is_honest_about_where_costs_come_from():
    text = format_selections([select(sort_facts())])
    assert "not measurements" in text


def test_empty_report_says_so():
    text = format_selections([])
    assert "No selection sites" in text
