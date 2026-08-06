"""Implementation registry for Flow's declarative ordering and search.

Two constructs share one selector (see `plan_selector`):

* `sort`: `xs |> sort`, `xs |> sortBy [...]`. Six lowerings, from "do nothing
  because the input is already in that order" to a stable bottom-up merge.
* `search`: `xs |> find(x)`. Two lowerings, linear scan and binary search.

The interesting part is that the two constructs share facts. A `|> sort` in
straight-line code leaves the array provably ascending, and a later `|> find`
on the same array reads that fact and drops from a linear scan to a binary
search. That is the whole point of carrying ordering hints through the
compiler rather than re-deriving them per construct.

Fact keys used by the sort implementations:

    elem_kind   "int" | "float" | "string" | "struct" | "bool"
    elem_bytes  estimated size of one element
    keys        number of `by` keys (0 = whole-element compare)
    stable      caller asked for a stable order
    unique      caller asked for adjacent-duplicate compaction
    direction   "asc" | "desc", the order being produced
    input_order "asc" | "asc_strict" | "desc" | "desc_strict" | "unknown"
    key_range   [lo, hi] when the sort key is a bounded integer, else None
    expect_runs "few" when the caller wrote `adaptive`, else "unknown"
    pinned      implementation name when the caller wrote `general`
"""

from __future__ import annotations

import math
from typing import Optional

from .plan_selector import Facts, Implementation, register

__all__ = ["sort_facts_ok", "COUNTING_MAX_SPAN", "SORT_MIN_RUN"]


# A counting sort allocates one bucket per distinct key. Past this span the
# bucket array costs more than the merge it replaces.
COUNTING_MAX_SPAN = 4096

# Below this length run detection has nothing to detect.
MERGE_MIN_N = 16

# Shortest run the natural merge will merge. Shorter runs are grown by
# insertion first. The C generator emits this same number, so the cost model
# and the emitted loop agree.
SORT_MIN_RUN = 32

# Cost charged per element for growing short runs up to SORT_MIN_RUN, in the
# same units as one merge pass. A count of comparisons would put it near
# SORT_MIN_RUN / 4, but insertion over a 32-element window stays in cache
# while a merge pass streams the whole array, so it is much cheaper per
# comparison than that count suggests. This number is calibrated against
# benchmarks/ordering/adaptive_sort_bench.flow, where the run-detecting merge
# beat the plain bottom-up merge on every input shape measured, random
# included. Re-measure before changing it.
RUN_EXTENSION_WEIGHT = SORT_MIN_RUN / 8.0


def _pinned(facts: Facts, me: str) -> Optional[str]:
    pin = facts.get("pinned")
    if pin and pin != me:
        return f"the `general` policy pinned this site to {pin}"
    return None


def sort_facts_ok(facts: Facts) -> Optional[str]:
    """Constraints every sort lowering shares."""
    if facts.n < 0:
        return "element count is not known at compile time"
    return None


def _log2(x: float) -> float:
    return math.log2(x) if x > 1 else 0.0


def _runs(facts: Facts) -> float:
    """Estimated number of ascending runs in the input."""
    order = facts.get("input_order", "unknown")
    if order in ("asc", "asc_strict"):
        return 1.0
    if facts.get("expect_runs") == "few":
        # `adaptive` is the caller asserting the data has structure. Take that
        # at its word and model it as sqrt(n) runs, the usual shape for
        # partially ordered input.
        return max(1.0, math.sqrt(facts.n))
    # No information: assume the worst a run detector can meet, alternating
    # pairs, which is n/2 runs.
    return max(1.0, facts.n / 2.0)


# ---------------------------------------------------------------------------
# sort
# ---------------------------------------------------------------------------


def _already_ordered_applicable(facts: Facts) -> Optional[str]:
    pin = _pinned(facts, "already_ordered")
    if pin:
        return pin
    if facts.get("unique"):
        return "`unique` still has to compact duplicates, so the sort cannot be skipped"
    order = facts.get("input_order", "unknown")
    want = facts.get("direction", "asc")
    if order.split("_")[0] != want:
        return f"input is not proven to be in {want} order (provenance: {order})"
    return None


register(
    Implementation(
        name="already_ordered",
        construct="sort",
        summary="no-op; provenance proves the array is already in this order",
        applicable=_already_ordered_applicable,
        cost=lambda f: 0.0,
        rank=0,
        resolution=(
            "sort where the order is provable. A call taking the array, a "
            "write to one of its elements, or a surrounding loop all drop "
            "the fact."
        ),
    )
)


def _reverse_applicable(facts: Facts) -> Optional[str]:
    pin = _pinned(facts, "reverse_in_place")
    if pin:
        return pin
    if facts.get("unique"):
        return "`unique` still has to compact duplicates, so a reverse is not enough"
    order = facts.get("input_order", "unknown")
    want = facts.get("direction", "asc")
    opposite = "desc" if want == "asc" else "asc"
    if order != opposite + "_strict":
        return (
            f"input is not proven to be in strictly {opposite} order "
            f"(provenance: {order}); reversing a run of equal keys would "
            "break stability"
        )
    return None


register(
    Implementation(
        name="reverse_in_place",
        construct="sort",
        summary="reverse the array in place; provenance proves it is strictly reversed",
        applicable=_reverse_applicable,
        cost=lambda f: f.n / 2.0,
        rank=1,
        resolution=(
            "only a strictly reversed input can be sorted by reversing it; "
            "add `unstable` if equal keys may be reordered"
        ),
    )
)


def _counting_applicable(facts: Facts) -> Optional[str]:
    pin = _pinned(facts, "counting")
    if pin:
        return pin
    if facts.get("keys"):
        return "counting sort handles whole-element keys only, not `by` keys"
    if facts.get("elem_kind") not in ("int", "bool"):
        return f"element type is {facts.get('elem_kind')}, not a bounded integer"
    rng = facts.get("key_range")
    if not rng:
        return "key range is not proven bounded and non-negative"
    lo, hi = rng
    if lo < 0:
        return f"key range [{lo}, {hi}] includes negative values"
    span = hi - lo + 1
    if span > COUNTING_MAX_SPAN:
        return (
            f"key span {span} exceeds the {COUNTING_MAX_SPAN}-bucket counting budget"
        )
    if facts.n < 8:
        return f"n={facts.n} is too small to amortise the bucket pass"
    return None


def _counting_cost(facts: Facts) -> float:
    lo, hi = facts.get("key_range")
    span = hi - lo + 1
    # Two passes over the data plus two over the buckets.
    return 2.0 * facts.n + 2.0 * span


def _counting_scratch(facts: Facts) -> int:
    rng = facts.get("key_range")
    if not rng:
        return 0
    lo, hi = rng
    # int32 bucket counts, plus a stable output buffer.
    return 4 * (hi - lo + 1) + facts.n * int(facts.get("elem_bytes", 8))


register(
    Implementation(
        name="counting",
        construct="sort",
        summary="stable counting sort over a proven non-negative bounded key range",
        applicable=_counting_applicable,
        cost=_counting_cost,
        scratch=_counting_scratch,
        rank=2,
        resolution=(
            "narrow the element type (u8 bounds keys to [0, 255], bool to "
            "[0, 1]) so the key range is proven without analysis"
        ),
    )
)


def _insertion_applicable(facts: Facts) -> Optional[str]:
    return _pinned(facts, "insertion")


def _insertion_cost(facts: Facts) -> float:
    n = float(facts.n)
    order = facts.get("input_order", "unknown")
    if order.startswith("asc") and facts.get("direction", "asc") == "asc":
        return n
    if facts.get("expect_runs") == "few":
        # Partially ordered input still leaves O(n * sqrt(n)) inversions.
        return n * math.sqrt(max(1.0, n))
    return n * n / 4.0


register(
    Implementation(
        name="insertion",
        construct="sort",
        summary="stable in-place insertion sort; no scratch, wins for small n",
        applicable=_insertion_applicable,
        cost=_insertion_cost,
        rank=3,
        resolution="drop the `general` policy",
    )
)


def _merge_scratch(facts: Facts) -> int:
    return facts.n * int(facts.get("elem_bytes", 8))


def _natural_merge_applicable(facts: Facts) -> Optional[str]:
    pin = _pinned(facts, "natural_merge")
    if pin:
        return pin
    if facts.n < MERGE_MIN_N:
        return f"n={facts.n} is below the {MERGE_MIN_N}-element run-detection floor"
    return None


def _natural_merge_cost(facts: Facts) -> float:
    n = float(facts.n)
    found = _runs(facts)
    # Runs shorter than the minimum are grown by insertion before merging, so
    # a run detector never gets more than n/SORT_MIN_RUN runs, and it pays
    # about SORT_MIN_RUN/4 comparisons per element when it has to do that
    # growing. On unstructured input that extension is what makes the run
    # detector lose to a plain bottom-up merge.
    ceiling = max(1.0, n / SORT_MIN_RUN)
    extension = 0.0
    if found > ceiling:
        found = ceiling
        extension = n * RUN_EXTENSION_WEIGHT
    # One scan to find runs, the extension, then log2(runs) merge passes.
    return n + extension + n * _log2(found)


register(
    Implementation(
        name="natural_merge",
        construct="sort",
        summary="run-detecting stable merge; one pass finds ascending and "
        "descending runs, then merges them pairwise",
        applicable=_natural_merge_applicable,
        cost=_natural_merge_cost,
        scratch=_merge_scratch,
        rank=4,
        resolution=(
            "the merge buffer is one element per input element; sort in "
            "chunks that fit the scratch budget, or use a narrower element "
            "type"
        ),
    )
)


def _bottom_up_applicable(facts: Facts) -> Optional[str]:
    # The general plan is always applicable. Something has to be, or a site
    # with an unusual shape would have no lowering at all.
    return _pinned(facts, "bottom_up_merge")


register(
    Implementation(
        name="bottom_up_merge",
        construct="sort",
        summary="stable bottom-up merge sort; the general-purpose plan",
        applicable=_bottom_up_applicable,
        cost=lambda f: f.n + f.n * _log2(f.n),
        scratch=_merge_scratch,
        rank=5,
        resolution=(
            "the merge buffer is one element per input element; sort in "
            "chunks that fit the scratch budget, or use a narrower element "
            "type"
        ),
    )
)


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


register(
    Implementation(
        name="linear_scan",
        construct="search",
        summary="scan from index 0 and stop at the first match",
        applicable=lambda f: None,
        cost=lambda f: max(1.0, f.n / 2.0),
        rank=1,
    )
)


def _binary_applicable(facts: Facts) -> Optional[str]:
    order = facts.get("input_order", "unknown")
    if not order.startswith("asc"):
        return (
            f"input is not proven to be in ascending order (provenance: {order})"
        )
    return None


register(
    Implementation(
        name="binary_search",
        construct="search",
        summary="lower-bound binary search; provenance proves the array is ascending",
        applicable=_binary_applicable,
        cost=lambda f: _log2(max(2.0, float(f.n))),
        rank=0,
        resolution=(
            "sort the array immediately before searching it; a call taking "
            "the array in between drops the ordering fact"
        ),
    )
)
