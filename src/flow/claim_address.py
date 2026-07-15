#!/usr/bin/env python3
"""
Claim Coordinates — permanent addressing for verified facts.

Old Claim Paths (Nat/+.zero-left) read like file paths and glue symbols to
English fragments.  Claim Coordinates read like sentences:

    «Nat» «addition» «zero is the left identity»

Three layers, always full words:
  carrier   — what kind of thing        (Nat, Bool, FullAdder)
  structure — which operation/transform (addition, disjunction, output)
  law       — the property in plain English (zero is the left identity)

Canonical slug (for tools):  Nat.addition.zero_is_the_left_identity
Human display:              Nat › addition › zero is the left identity
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

# «carrier» «structure» «law phrase»
GUILLEMET_CLAIM_RE = re.compile(
    r"^«(?P<carrier>[^»]+)»\s*«(?P<structure>[^»]+)»\s*«(?P<law>[^»]+)»"
)

# Legacy: Nat/+.zero-left
LEGACY_CLAIM_RE = re.compile(
    r"^(?P<carrier>[A-Za-z][A-Za-z0-9_]*)"
    r"/(?P<structure>\|\||[+|=|*]|[a-z][a-zA-Z0-9_-]*)"
    r"\.(?P<facet>[a-z][a-z0-9-]+)$"
)

STRUCTURE_SYMBOL_TO_NAME: Dict[str, str] = {
    "+": "addition",
    "*": "multiplication",
    "||": "disjunction",
    "&&": "conjunction",
    "=": "equality",
    "out": "output",
    "fifo": "fifo",
    "vectorize": "vectorization",
    "fuse": "fusion",
}

FACET_TO_LAW: Dict[str, str] = {
    "zero-left": "zero is the left identity",
    "zero-right": "zero is the right identity",
    "succ-right": "successor on the right steps the sum",
    "succ-left": "successor on the left steps the sum",
    "commutes": "order does not matter",
    "assoc": "parentheses do not matter",
    "reflexive": "everything equals itself",
    "symmetric": "equality reverses",
    "transitive": "equality chains",
    "square-nonneg": "squaring never yields a negative",
    "correct": "output matches specification",
    "semantics-equal": "optimized code matches naive code",
    "order-kept": "order is preserved",
}


@dataclass(frozen=True)
class ClaimAddress:
    carrier: str
    structure: str
    law: str

    @property
    def slug(self) -> str:
        return f"{self.carrier}.{self.structure}.{slug_phrase(self.law)}"

    @property
    def guillemets(self) -> str:
        return f"«{self.carrier}» «{self.structure}» «{self.law}»"

    @property
    def display(self) -> str:
        return f"{self.carrier} › {self.structure} › {self.law}"

    def ontology_line(self) -> str:
        return self.display


def slug_phrase(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def to_legacy_path(addr: ClaimAddress) -> str:
    """Deprecated path for index aliases."""
    sym = {v: k for k, v in STRUCTURE_SYMBOL_TO_NAME.items()}.get(
        addr.structure, addr.structure
    )
    facet_rev = {v: k for k, v in FACET_TO_LAW.items()}
    facet = facet_rev.get(addr.law, slug_phrase(addr.law).replace("_", "-"))
    return f"{addr.carrier}/{sym}.{facet}"


def parse_claim_address(text: str) -> ClaimAddress:
    raw = text.strip().split("(")[0].strip()

    m = GUILLEMET_CLAIM_RE.match(raw)
    if m:
        return ClaimAddress(
            carrier=m.group("carrier").strip(),
            structure=m.group("structure").strip(),
            law=m.group("law").strip(),
        )

    m = LEGACY_CLAIM_RE.match(raw)
    if m:
        return legacy_to_address(
            m.group("carrier"),
            m.group("structure"),
            m.group("facet"),
        )

    # Canonical slug: Nat.addition.zero_is_the_left_identity
    if raw.count(".") >= 2:
        carrier, structure, law_slug = raw.split(".", 2)
        return ClaimAddress(carrier, structure, law_slug.replace("_", " "))

    raise ValueError(f"Not a Claim Address: {text!r}")


def try_parse_claim_address(text: str) -> Optional[ClaimAddress]:
    try:
        return parse_claim_address(text)
    except ValueError:
        return None


def legacy_to_address(carrier: str, structure_sym: str, facet: str) -> ClaimAddress:
    structure = STRUCTURE_SYMBOL_TO_NAME.get(structure_sym, structure_sym)
    law = FACET_TO_LAW.get(facet, facet.replace("-", " "))
    return ClaimAddress(carrier=carrier, structure=structure, law=law)


def tier_opening_plain(tier: str, addr: ClaimAddress) -> str:
    from flow.math_prose import tier_opening_mathematical

    return tier_opening_mathematical(tier, addr)


def address_phrase(addr: ClaimAddress) -> str:
    """Plain English gloss for proof prose."""
    gloss = {
        ("Nat", "addition", "zero is the left identity"): (
            "adding zero on the left does not change the number"
        ),
        ("Nat", "addition", "zero is the right identity"): (
            "adding zero on the right does not change the number"
        ),
        ("Nat", "addition", "successor on the right steps the sum"): (
            "adding one more on the right bumps the sum by one"
        ),
        ("Nat", "addition", "order does not matter"): (
            "you can swap the order when you add"
        ),
        ("Eq", "equality", "everything equals itself"): (
            "anything is always equal to itself"
        ),
        ("Bool", "disjunction", "order does not matter"): (
            'order does not matter for "or"'
        ),
        ("Int", "multiplication", "squaring never yields a negative"): (
            "squaring never gives a negative number"
        ),
        ("Geometry", "triangle", "interior angles sum to two right angles"): (
            "the three interior angles of a triangle sum to two right angles"
        ),
        ("Geometry", "isosceles triangle", "base angles are equal"): (
            "the angles at the base of an isosceles triangle are equal"
        ),
        ("Geometry", "intersecting lines", "vertical angles are equal"): (
            "vertical angles formed by intersecting lines are equal"
        ),
        ("Geometry", "right triangle", "the Pythagorean relation holds"): (
            "the square on the hypotenuse equals the sum of squares on the legs"
        ),
        ("Geometry", "parallel lines", "alternate angles are equal"): (
            "alternate interior angles are equal when parallel lines meet a transversal"
        ),
        ("Geometry", "triangle congruence", "side-angle-side implies congruence"): (
            "two sides and the included angle determine a triangle up to congruence"
        ),
        ("Geometry", "circle", "radii from the centre are equal"): (
            "all radii from the centre to the circumference are equal"
        ),
        ("Geometry", "circle", "inscribed angle is half the central angle"): (
            "an inscribed angle equals half the central angle on the same arc"
        ),
        ("Geometry", "circle", "Thales right angle in semicircle"): (
            "an angle inscribed in a semicircle is a right angle"
        ),
        ("Analysis", "Taylor series", "sin equals its Maclaurin series near zero"): (
            "sin(x) matches its Maclaurin partial sums in a neighbourhood of the origin"
        ),
        ("Analysis", "smooth functions", "derivatives of sine are known"): (
            "the derivatives of sine at zero follow the alternating pattern of the Maclaurin series"
        ),
    }
    key = (addr.carrier, addr.structure, addr.law)
    if key in gloss:
        return gloss[key]
    from flow.math_prose import addr_prose

    return addr_prose(addr)