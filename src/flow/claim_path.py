#!/usr/bin/env python3
"""
Claim Paths — legacy shim.  Prefer claim_address.ClaimAddress (Claim Coordinates).

New syntax: «Nat» «addition» «zero is the left identity»
Legacy:     Nat/+.zero-left  (still parsed, displayed as coordinates)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from flow.claim_address import (
    ClaimAddress,
    parse_claim_address,
    try_parse_claim_address,
)

CLAIM_PATH_RE = re.compile(
    r"^(?P<domain>[A-Za-z][A-Za-z0-9_]*)"
    r"/(?P<morphism>\|\||[+|=|*]|[a-z][a-zA-Z0-9_-]*)"
    r"\.(?P<facet>[a-z][a-z0-9-]+)$"
)

VALID_TIERS = frozenset({"definition", "axiom", "derived"})

TIER_BOUNDARY = {
    "definition": (
        "definitional boundary",
        "We stipulate how this operation is defined — we do not derive it.",
    ),
    "axiom": (
        "axiomatic boundary",
        "We accept this without proof — it marks an ontological commitment.",
    ),
    "derived": (
        "derived boundary",
        "We establish this by proof from definitions, axioms, and prior derived facts.",
    ),
}

MORPHISM_GLOSS = {
    "+": "addition",
    "||": "disjunction (or)",
    "=": "equality",
    "*": "multiplication",
    "out": "output",
    "fifo": "FIFO behaviour",
    "vectorize": "vectorization",
    "fuse": "loop fusion",
}


@dataclass(frozen=True)
class ClaimPath:
    domain: str
    morphism: str
    facet: str

    @property
    def address(self) -> str:
        addr = try_parse_claim_address(
            f"{self.domain}/{self.morphism}.{self.facet}"
        )
        return addr.guillemets if addr else f"{self.domain}/{self.morphism}.{self.facet}"

    @property
    def morphism_gloss(self) -> str:
        return MORPHISM_GLOSS.get(self.morphism, self.morphism)

    def ontology_line(self) -> str:
        addr = try_parse_claim_address(
            f"{self.domain}/{self.morphism}.{self.facet}"
        )
        return addr.display if addr else f"{self.domain} / {self.morphism} · {self.facet}"


def _address_to_claim_path(addr: ClaimAddress) -> ClaimPath:
    sym = {v: k for k, v in {
        "+": "addition",
        "*": "multiplication",
        "||": "disjunction",
        "=": "equality",
    }.items()}.get(addr.structure, addr.structure)
    facet = addr.law.replace(" ", "-")[:32]
    return ClaimPath(domain=addr.carrier, morphism=sym, facet=facet)


def parse_claim_path(text: str) -> ClaimPath:
    addr = parse_claim_address(text)
    return _address_to_claim_path(addr)


def try_parse_claim_path(text: str) -> Optional[ClaimPath]:
    addr = try_parse_claim_address(text)
    return _address_to_claim_path(addr) if addr else None


def normalize_tier(tier: str) -> str:
    t = tier.strip().lower()
    if t in VALID_TIERS:
        return t
    if t in ("definitions-only", "definition-only"):
        return "definition"
    return t


def tier_label(tier: str) -> str:
    t = normalize_tier(tier)
    return {
        "definition": "Definition",
        "axiom": "Axiom",
        "derived": "Derived fact",
    }.get(t, "Theorem")


def tier_opening(tier: str, claim: ClaimPath) -> str:
    t = normalize_tier(tier)
    name, boundary = TIER_BOUNDARY.get(t, TIER_BOUNDARY["derived"])
    addr = try_parse_claim_address(claim.address) if hasattr(claim, "address") else None
    loc = addr.display if addr else claim.ontology_line()
    return (
        f"**{tier_label(t)}** at {loc} — {boundary} "
        f"Carrier: **{claim.domain}**; structure: **{claim.morphism_gloss}**."
    )


def tier_opening_plain(tier: str, claim: ClaimPath) -> str:
    """One sentence for proof-step tables (no markdown bold)."""
    t = normalize_tier(tier)
    addr = try_parse_claim_address(claim.address)
    if t == "definition":
        if addr:
            return (
                f"We stipulate the law «{addr.law}» for {addr.structure} on "
                f"{addr.carrier} — this is a definition, not a derived fact."
            )
        return (
            f"We stipulate how {claim.morphism_gloss} behaves on {claim.domain} "
            f"— this is a definition, not a derived fact."
        )
    if t == "axiom":
        return (
            f"We accept this axiom on {claim.domain} without proof — "
            f"it is an ontological commitment, not a lemma."
        )
    if addr:
        return (
            f"We prove that on {addr.carrier}, {addr.structure} satisfies "
            f"«{addr.law}»."
        )
    return (
        f"We prove this derived fact about {claim.domain} "
        f"and {claim.morphism_gloss} from prior claims."
    )


def assume_premise(
    ref_path: str,
    *,
    phrase: str,
    args: str = "",
    is_induction_hypothesis: bool = False,
    hyp_var: str = "k",
    ref_tier: str = "derived",
    theorem_ref: str = "",
) -> str:
    if is_induction_hypothesis:
        return (
            f"We cross the inductive boundary: assume the claim holds for "
            f"{hyp_var} (the induction hypothesis)."
        )

    t = normalize_tier(ref_tier)
    kind = {
        "definition": "definitional clause",
        "axiom": "axiom",
        "derived": "derived fact",
    }.get(t, "prior claim")

    addr_obj = try_parse_claim_address(ref_path)
    if addr_obj:
        from flow.math_prose import invoke_premise_mathematical

        return invoke_premise_mathematical(
            addr_obj,
            phrase=phrase,
            args=args,
            kind=kind,
            theorem_ref=theorem_ref,
        )
    if args:
        return (
            f"We invoke the {kind}: {phrase} (instantiated for {args})."
        )
    return f"We invoke the {kind}: {phrase}."


def claim_fingerprint(expr: str) -> str:
    """Canonical form of a therefore-clause — duplicate claims share a fingerprint."""
    s = expr.strip()
    s = re.sub(r"\s+by\s+\w+.*$", "", s)
    s = s.replace("==", "=")
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"\bone more than\b", "succ", s)
    return s.lower()


def fingerprint_key(domain: str, morphism: str, fingerprint: str) -> str:
    return f"{domain}/{morphism}#{fingerprint}"


def check_duplicate_claims(
    theorems: List[Tuple[str, str, str]],
) -> List[str]:
    """
    Detect synonym creep: same domain+morphism+fingerprint, different facet.

    Each entry: (claim_path, therefore_expr, file_path).
    Returns human-readable errors.
    """
    seen: Dict[str, str] = {}
    errors: List[str] = []
    for path, expr, file_path in theorems:
        addr = try_parse_claim_address(path)
        if not addr:
            continue
        fp = claim_fingerprint(expr)
        key = fingerprint_key(addr.carrier, addr.structure, fp)
        if key in seen and seen[key] != path:
            errors.append(
                f"Duplicate claim: `{path}` and `{seen[key]}` say the same thing "
                f"({addr.display}, fingerprint {fp!r}) — "
                f"see {file_path}"
            )
        else:
            seen[key] = path
    return errors