"""Cost-based implementation selection for declarative constructs.

A declarative construct in Flow names an *intent*: put this array in order,
find this value. Several C lowerings satisfy the same intent, and which one is
cheapest depends on facts the compiler knows at the call site (how many
elements, what the element type is, whether the input is already ordered,
whether an integer key range is bounded).

This module holds the machinery for that choice, separate from any one
construct:

* `Facts` is the immutable bag of what the compiler knows at a site.
* `Implementation` is one lowering. It declares an applicability predicate,
  a resource claim, and a cost model.
* `select` runs every registered implementation for a construct against the
  facts, keeps the cheapest applicable one, and records why every other
  candidate lost.

The record is the point. `--explain` prints it verbatim, so an adaptive choice
is inspectable rather than magic. See docs/language/explainable-compilation.md.

Costs are *estimated element operations*, a dimensionless count. They are
static estimates from an annotated model, never measurements. Two costs are
comparable within one construct and meaningless across constructs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

__all__ = [
    "Facts",
    "Implementation",
    "Candidate",
    "Selection",
    "register",
    "implementations_for",
    "select",
    "format_selections",
    "SCRATCH_BUDGET_BYTES",
]


# Hard resource budget for compiler-introduced scratch space. A sort helper
# puts its scratch on the C stack, so an implementation that wants more than
# this is rejected rather than silently risking a stack overflow.
SCRATCH_BUDGET_BYTES = 256 * 1024


@dataclass(frozen=True)
class Facts:
    """What the compiler knows at one selection site.

    `construct` names the intent ("sort", "search"). `n` is the element count.
    Everything construct-specific lives in `data` so the selector itself stays
    ignorant of any particular construct.
    """

    construct: str
    n: int
    data: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def summary_items(self) -> List[str]:
        items = [f"n={self.n}"]
        for key in sorted(self.data):
            value = self.data[key]
            if value is None or value == [] or value is False:
                continue
            items.append(f"{key}={value}")
        return items


# An applicability predicate returns None when the implementation may be used,
# or a human-readable sentence naming the constraint that failed.
Predicate = Callable[[Facts], Optional[str]]
CostModel = Callable[[Facts], float]


@dataclass(frozen=True)
class Implementation:
    """One lowering of a construct, with the conditions under which it applies."""

    name: str
    construct: str
    summary: str
    applicable: Predicate
    cost: CostModel
    # Bytes of compiler-introduced scratch this lowering needs. Checked
    # against SCRATCH_BUDGET_BYTES before the cost model is consulted.
    scratch: Callable[[Facts], int] = lambda f: 0
    # Lower wins when two costs tie. Keeps selection deterministic.
    rank: int = 50
    # What the programmer could change to make this candidate applicable.
    # Printed under "possible resolutions" when it is rejected.
    resolution: str = ""


@dataclass
class Candidate:
    """One implementation's fate at one site."""

    name: str
    summary: str
    cost: Optional[float]
    rejected: Optional[str] = None
    scratch: int = 0
    resolution: str = ""
    # True when the rejection was a resource budget rather than a mismatch
    # between the implementation and the data.
    over_budget: bool = False

    @property
    def chosen_marker(self) -> str:
        return "rejected" if self.rejected else "considered"


@dataclass
class Selection:
    """The full record of one selection site."""

    construct: str
    location: str
    detail: str
    facts: Facts
    candidates: List[Candidate]
    chosen: str
    reason: str
    # A resource budget refused at least one candidate, or nothing but one
    # implementation was left standing. Either way the programmer probably
    # wants to know what they could change.
    constrained: bool = False

    def chosen_candidate(self) -> Optional[Candidate]:
        for cand in self.candidates:
            if cand.name == self.chosen:
                return cand
        return None


_REGISTRY: Dict[str, List[Implementation]] = {}


def register(impl: Implementation) -> Implementation:
    """Add an implementation to the registry for its construct."""
    bucket = _REGISTRY.setdefault(impl.construct, [])
    bucket[:] = [i for i in bucket if i.name != impl.name]
    bucket.append(impl)
    return impl


def implementations_for(construct: str) -> List[Implementation]:
    return list(_REGISTRY.get(construct, []))


class NoImplementation(Exception):
    """Raised when every registered implementation was rejected."""


def select(facts: Facts, location: str = "", detail: str = "") -> Selection:
    """Pick the cheapest applicable implementation and record the reasoning."""
    impls = implementations_for(facts.construct)
    if not impls:
        raise NoImplementation(f"No implementations registered for '{facts.construct}'")

    candidates: List[Candidate] = []
    viable: List[tuple] = []
    over_budget = False
    for impl in impls:
        why_not = impl.applicable(facts)
        blew_budget = False
        if why_not is None:
            need = int(impl.scratch(facts))
            if need > SCRATCH_BUDGET_BYTES:
                blew_budget = True
                over_budget = True
                why_not = (
                    f"scratch {_bytes(need)} exceeds the "
                    f"{_bytes(SCRATCH_BUDGET_BYTES)} compiler scratch budget"
                )
            else:
                cost = float(impl.cost(facts))
                candidates.append(
                    Candidate(impl.name, impl.summary, cost, None, need)
                )
                viable.append((cost, impl.rank, impl.name, impl))
                continue
        candidates.append(
            Candidate(
                impl.name,
                impl.summary,
                None,
                why_not,
                0,
                impl.resolution,
                blew_budget,
            )
        )

    if not viable:
        raise NoImplementation(
            f"Every implementation of '{facts.construct}' was rejected at {location}"
        )

    viable.sort(key=lambda t: (t[0], t[1], t[2]))
    best_cost, _, best_name, best_impl = viable[0]
    if len(viable) == 1:
        reason = "only applicable implementation"
    else:
        runner_cost, _, runner_name, _ = viable[1]
        if math.isclose(best_cost, runner_cost):
            reason = f"tied with {runner_name} on cost; broke the tie on declared rank"
        else:
            saving = (runner_cost - best_cost) / runner_cost * 100.0
            reason = (
                f"cheapest applicable plan: {_cost(best_cost)} vs "
                f"{_cost(runner_cost)} for {runner_name} ({saving:.0f}% less work)"
            )

    return Selection(
        construct=facts.construct,
        location=location,
        detail=detail,
        facts=facts,
        candidates=candidates,
        chosen=best_name,
        reason=reason,
        constrained=over_budget or len(viable) == 1,
    )


def _bytes(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / (1024 * 1024):.2f} MiB"
    if n >= 1024:
        return f"{n / 1024:.1f} KiB"
    return f"{n} B"


def _cost(value: float) -> str:
    if value == 0:
        return "0"
    if value >= 1e5:
        return f"{value:.3g}"
    if value >= 10:
        return f"{value:.0f}"
    return f"{value:.2f}"


def format_selections(selections: List[Selection], source: str = "") -> str:
    """Render selection records as the `--explain` report."""
    lines: List[str] = []
    header = "Compilation plan"
    if source:
        header += f" for {source}"
    lines.append(header)
    lines.append("=" * len(header))
    lines.append("")
    if not selections:
        lines.append("No selection sites. This program has no declarative")
        lines.append("construct with more than one implementation.")
        lines.append("")
        return "\n".join(lines)

    for index, sel in enumerate(selections, start=1):
        title = f"[{index}] {sel.construct}"
        if sel.location:
            title += f" at {sel.location}"
        lines.append(title)
        if sel.detail:
            lines.append(f"      {sel.detail}")
        lines.append(f"      facts: {', '.join(sel.facts.summary_items())}")
        lines.append("")
        width = max(len(c.name) for c in sel.candidates)
        for cand in sel.candidates:
            mark = "->" if cand.name == sel.chosen else "  "
            if cand.rejected:
                lines.append(
                    f"   {mark} {cand.name:<{width}}  {'--':>10}   "
                    f"rejected: {cand.rejected}"
                )
            else:
                note = "CHOSEN" if cand.name == sel.chosen else "ok"
                lines.append(
                    f"   {mark} {cand.name:<{width}}  {_cost(cand.cost):>10}   "
                    f"{note}"
                )
                lines.append(f"      {'':<{width}}  {'':>10}   {cand.summary}")
        lines.append("")
        lines.append(f"      chose {sel.chosen}: {sel.reason}")
        # A rejection is ordinary; it only deserves advice when the selector
        # was actually boxed in. Otherwise the per-candidate reasons above
        # already say everything.
        resolutions = []
        if sel.constrained:
            rejected = [c for c in sel.candidates if c.rejected and c.resolution]
            # Budget failures first: they are the ones the programmer hit.
            rejected.sort(key=lambda c: not c.over_budget)
            resolutions = [f"{c.name}: {c.resolution}" for c in rejected]
        if resolutions:
            lines.append("")
            lines.append("      possible resolutions")
            for text in resolutions[:4]:
                lines.append(f"        - {text}")
        lines.append("")

    lines.append(
        "Costs are estimated element operations from a static model, not "
        "measurements."
    )
    lines.append("")
    return "\n".join(lines)
