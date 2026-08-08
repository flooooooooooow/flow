#!/usr/bin/env python3
"""
Mathematical prose — every proof line reads as a mathematician would speak it.

No Nat, Bool, Int, bool, or symbol soup in English output.
"""

from __future__ import annotations

import re
from typing import Optional

from flow.claim_address import ClaimAddress, try_parse_claim_address

# Carriers: code name -> how a mathematician names the domain
CARRIER_MATHEMATICAL: dict[str, str] = {
    "Nat": "the natural numbers",
    "Bool": "boolean truth values",
    "Int": "the integers",
    "Eq": "equality",
    "Geometry": "the Euclidean plane",
    "Analysis": "real analysis",
    "Real": "the real numbers",
    "bool": "boolean truth values",
    "i32": "the integers",
    "i64": "the integers",
}

STRUCTURE_MATHEMATICAL: dict[str, str] = {
    "addition": "addition",
    "multiplication": "multiplication",
    "disjunction": "disjunction",
    "conjunction": "conjunction",
    "equality": "equality",
    "output": "output",
    "fifo": "first-in-first-out ordering",
    "vectorization": "vectorization",
    "fusion": "loop fusion",
    "triangle": "triangles in",
    "isosceles triangle": "isosceles triangles in",
    "intersecting lines": "intersecting lines in",
    "right triangle": "right triangles in",
    "parallel lines": "parallel lines in",
    "triangle congruence": "triangle congruence in",
    "circle": "circles in",
    "Euclid Book I": "Book I of the Elements in",
}

STRUCTURE_COORDINATE: dict[str, str] = {
    "triangle": "triangle",
    "isosceles triangle": "isosceles triangle",
    "intersecting lines": "intersecting lines",
    "right triangle": "right triangle",
    "parallel lines": "parallel lines",
    "triangle congruence": "triangle congruence",
    "circle": "circle",
    "Euclid Book I": "Euclid Book I",
    "Taylor series": "Taylor series",
    "smooth functions": "smooth functions",
}

GEOMETRY_TOKEN_ENGLISH: dict[str, str] = {
    "two_right_angles": "two right angles",
    "one_right_angle": "one right angle",
    "half_of_angle_AOB": "half of angle AOB",
    "radius_OA": "radius OA",
    "radius_OB": "radius OB",
    "angle_alpha": "angle α",
    "angle_alpha_prime": "angle α′",
    "angle_beta": "angle β",
    "angle_beta_prime": "angle β′",
    "angle_gamma": "angle γ",
}

GEOMETRY_TOKEN_LATEX: dict[str, str] = {
    "triangle_ABC": r"\triangle ABC",
    "triangle_DEF": r"\triangle DEF",
    "two_right_angles": r"180^\circ",
    "one_right_angle": r"90^\circ",
    "half_of_angle_AOB": r"\tfrac{1}{2}\angle AOB",
    "radius_OA": r"OA",
    "radius_OB": r"OB",
    "angle_alpha": r"\alpha",
    "angle_alpha_prime": r"\alpha'",
    "angle_beta": r"\beta",
    "angle_beta_prime": r"\beta'",
    "angle_gamma": r"\gamma",
}

ANALYSIS_TOKEN_LATEX: dict[str, str] = {
    "sin_prime_at_zero": r"\sin'(0)",
    "sin_double_prime_at_zero": r"\sin''(0)",
    "near_zero": r"x \to 0",
}

ANALYSIS_TOKEN_ENGLISH: dict[str, str] = {
    "sin_prime_at_zero": "the first derivative of sine at zero",
    "sin_double_prime_at_zero": "the second derivative of sine at zero",
    "near_zero": "in a neighbourhood of zero",
}

_UNDERSCORE_IDENT_RE = re.compile(
    r"(?<!\\)\b[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+\b"
)

TYPE_LATEX: dict[str, str] = {
    "Nat": r"\mathbb{N}",
    "Int": r"\mathbb{Z}",
    "Real": r"\mathbb{R}",
    "i32": r"\mathbb{Z}",
    "i64": r"\mathbb{Z}",
    "bool": r"\{\mathsf{true}, \mathsf{false}\}",
    "Bool": r"\{\mathsf{true}, \mathsf{false}\}",
}


def carrier_mathematical(name: str) -> str:
    return CARRIER_MATHEMATICAL.get(name.strip(), name.strip())


def structure_mathematical(name: str) -> str:
    return STRUCTURE_MATHEMATICAL.get(name.strip(), name.strip())


def type_latex(name: str) -> str:
    return TYPE_LATEX.get(name.strip(), name.strip())


def on_structure_carrier(structure: str, carrier: str) -> str:
    """'addition on the natural numbers' or 'triangles in the Euclidean plane'."""
    struct = structure_mathematical(structure)
    car = carrier_mathematical(carrier)
    if carrier.strip() == "Geometry":
        return f"{struct} {car}"
    return f"{struct} on {car}"


def law_phrase(law: str) -> str:
    """Embed a law as a noun phrase."""
    if not law:
        return "the stated law"
    text = law[0].lower() + law[1:] if law else law
    return text


def addr_prose(addr: ClaimAddress) -> str:
    """One line a mathematician would write in a margin."""
    return (
        f"{law_phrase(addr.law)}, for {structure_mathematical(addr.structure)} "
        f"on {carrier_mathematical(addr.carrier)}"
    )


def structure_coordinate_display(name: str) -> str:
    return STRUCTURE_COORDINATE.get(name.strip(), structure_mathematical(name))


def addr_coordinate_display(addr: ClaimAddress) -> str:
    """Coordinate line without code names."""
    return (
        f"{carrier_mathematical(addr.carrier)} · "
        f"{structure_coordinate_display(addr.structure)} · {addr.law}"
    )


def addr_coordinate_latex(addr: ClaimAddress) -> str:
    """Coordinate line for PDF — uses math-center dots, not Unicode middots."""
    carrier = carrier_mathematical(addr.carrier)
    structure = structure_coordinate_display(addr.structure)
    law = addr.law.replace("_", r"\_")
    return rf"{carrier} \cdot {structure} \cdot {law}"


def claim_path_latex(path: str) -> str:
    """Claim coordinate as plain text for reliable PDF rendering."""
    addr = try_parse_claim_address(path)
    if not addr:
        return path.replace("_", r"\_")
    return addr_coordinate_latex(addr)


def tier_opening_mathematical(tier: str, addr: ClaimAddress) -> str:
    from flow.claim_path import normalize_tier

    t = normalize_tier(tier)
    ctx = on_structure_carrier(addr.structure, addr.carrier)
    if t == "definition":
        return (
            f"We stipulate {law_phrase(addr.law)} for {ctx} "
            f"— this is a definition, not a derived fact."
        )
    if t == "axiom":
        return (
            f"We accept {law_phrase(addr.law)} for {ctx} without proof "
            f"— an ontological commitment, not a lemma."
        )
    return f"We prove that {law_phrase(addr.law)} for {ctx}."


def invoke_premise_mathematical(
    addr: ClaimAddress,
    *,
    phrase: str,
    args: str = "",
    kind: str = "derived fact",
    theorem_ref: str = "",
) -> str:
    if theorem_ref:
        if args:
            return (
                f"We invoke {theorem_ref} ({phrase}, instantiated for {args})."
            )
        return f"We invoke {theorem_ref}: {phrase}."
    ctx = on_structure_carrier(addr.structure, addr.carrier)
    if args:
        return (
            f"We invoke the {kind} governing {ctx}: {phrase} "
            f"(instantiated for {args})."
        )
    return f"We invoke the {kind} governing {ctx}: {phrase}."


def mathematical_case_condition(cond: str) -> str:
    """Turn parser conditions into spoken mathematics."""
    c = cond.strip()
    m = re.match(r"(\w+)\s*==\s*true\s*$", c, re.I)
    if m:
        return f"{m.group(1)} holds"
    m = re.match(r"(\w+)\s*==\s*false\s*$", c, re.I)
    if m:
        return f"{m.group(1)} does not hold"
    m = re.match(r"(\w+)\s*==\s*0\s*$", c)
    if m:
        return f"{m.group(1)} is zero"
    return c.replace("==", " equals ").strip()


def _replace_word(s: str, token: str, phrase: str) -> str:
    return re.sub(rf"\b{re.escape(token)}\b", lambda _m: phrase, s)


def _normalize_geometry_tokens(s: str, *, latex: bool = False) -> str:
    """Turn geometry identifiers into spoken or typeset mathematics."""
    table = GEOMETRY_TOKEN_LATEX if latex else GEOMETRY_TOKEN_ENGLISH
    for token, phrase in table.items():
        s = _replace_word(s, token, phrase)

    if latex:
        s = re.sub(r"\bangle_at_(\w+)\b", lambda m: rf"\angle {m.group(1)}", s)
        s = re.sub(r"\bangle_(\w+)\b", lambda m: rf"\angle {m.group(1)}", s)
        s = re.sub(
            r"\b(\w+)\s*\*\s*\1\b",
            lambda m: rf"{m.group(1)}^{{2}}",
            s,
        )
        s = re.sub(
            r"\b(\w+)\s*\*\s*(\w+)\b",
            lambda m: rf"{m.group(1)} \cdot {m.group(2)}",
            s,
        )
        return s

    s = re.sub(r"\bangle_at_(\w+)\b", r"angle at \1", s)
    s = re.sub(r"\bangle_(\w+)\b", r"angle \1", s)
    return s


def is_geometry_expr(expr: str) -> bool:
    if re.search(
        r"\b(angle_|two_right_angles|one_right_angle|half_of_|radius_|triangle_)",
        expr,
    ):
        return True
    return any(
        re.search(rf"\b{re.escape(token)}\b", expr)
        for token in GEOMETRY_TOKEN_LATEX
    )


def _underscore_ident_to_latex(ident: str) -> str:
    if ident in ANALYSIS_TOKEN_LATEX:
        return ANALYSIS_TOKEN_LATEX[ident]
    if ident in GEOMETRY_TOKEN_LATEX:
        return GEOMETRY_TOKEN_LATEX[ident]
    return rf"\text{{{' '.join(ident.split('_'))}}}"


def _underscore_ident_to_english(ident: str) -> str:
    if ident in ANALYSIS_TOKEN_ENGLISH:
        return ANALYSIS_TOKEN_ENGLISH[ident]
    if ident in GEOMETRY_TOKEN_ENGLISH:
        return GEOMETRY_TOKEN_ENGLISH[ident]
    return ident.replace("_", " ")


def _replace_underscore_identifiers(s: str, converter) -> str:
    idents = set(_UNDERSCORE_IDENT_RE.findall(s))
    for ident in sorted(idents, key=len, reverse=True):
        replacement = converter(ident)

        def _repl(_m: re.Match, rep: str = replacement) -> str:
            return rep

        s = re.sub(rf"(?<!\\)\b{re.escape(ident)}\b", _repl, s)
    return s


def _finalize_latex(s: str) -> str:
    return _replace_underscore_identifiers(s, _underscore_ident_to_latex)


def geometry_expr_to_latex(expr: str) -> str:
    """LaTeX for geometric claims and conclusions."""
    s = expr.strip()
    s = re.sub(r"\s+by\s+\w+.*$", "", s)
    s = s.replace("==", "=")
    s = _normalize_geometry_tokens(s, latex=True)
    return _finalize_latex(s)


def flow_expr_to_mathematical_english(expr: str) -> str:
    """Every expression reads as a mathematician would say it."""
    s = expr.strip()
    s = re.sub(r"\s+by\s+\w+.*$", "", s)
    s = _replace_underscore_identifiers(s, _underscore_ident_to_english)
    s = _normalize_geometry_tokens(s, latex=False)
    s = s.replace("==", " equals ")

    # Shield disjunctions before expanding conjunctions (avoid "a and b" inside disjunction)
    disj_parts: list[tuple[str, str]] = []

    def _shield_or(m: re.Match) -> str:
        idx = len(disj_parts)
        disj_parts.append((m.group(1), m.group(2)))
        return f"__DISJ{idx}__"

    while re.search(r"\b(\w+)\s+or\s+(\w+)\b", s):
        s = re.sub(r"\b(\w+)\s+or\s+(\w+)\b", _shield_or, s, count=1)

    s = re.sub(r"\b(\w+)\s+and\s+(\w+)\b", r"the conjunction of \1 and \2", s)

    # Restore shields in REVERSE order: a later `\w+ or \w+` match may have
    # consumed an earlier `__DISJ{i}__` marker as an operand (e.g. `x or y or
    # z` shields `x or y`, then shields `__DISJ0__ or z`), so restoring
    # forward leaves a leaked marker in the final text.
    for i, (a, b) in reversed(list(enumerate(disj_parts))):
        s = s.replace(f"__DISJ{i}__", f"the disjunction of {a} and {b}")
    s = re.sub(r"\bsucc\(([^)]+)\)", r"the successor of \1", s)
    s = re.sub(r"\btrue\b", "true", s)
    s = re.sub(r"\bfalse\b", "false", s)
    s = re.sub(r">=", " is at least ", s)
    s = re.sub(r"<=", " is at most ", s)
    s = re.sub(r"([^=<>]+)\s*=\s*([^=<>]+)", r"\1 equals \2", s)
    s = re.sub(r"\s*\+\s*", " plus ", s)
    s = re.sub(r"\s*\*\s*", " times ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _analysis_expr_to_latex(expr: str) -> Optional[str]:
    s = expr.strip()
    if not re.search(
        r"\b(taylor_sin|near_zero|sin\(|sin_prime_at_zero|sin_double_prime_at_zero)\b",
        s,
    ):
        return None
    s = re.sub(r"\s+by\s+\w+.*$", "", s)
    s = s.replace("==", "=")
    s = re.sub(
        r"\btaylor_sin\(([^,]+),\s*order_(\d+)\)",
        lambda m: rf"S_{{{m.group(2)}}}({m.group(1)})",
        s,
    )
    s = re.sub(r"\bsin\(", r"\\sin(", s)
    s = re.sub(r"\bnear_zero\b", r"\\quad (x \\to 0)", s)
    return _finalize_latex(s)


def flow_expr_to_latex(expr: str) -> str:
    """Typeset a Flow verification expression for proof PDFs."""
    s = expr.strip()
    if is_geometry_expr(s):
        return geometry_expr_to_latex(s)
    analysis = _analysis_expr_to_latex(s)
    if analysis is not None:
        return analysis
    s = re.sub(r"\s+by\s+\w+.*$", "", s)
    s = s.replace("==", "=")
    s = re.sub(r"\bsucc\(([^)]+)\)", r"\\mathrm{succ}(\1)", s)
    s = re.sub(r"\bor\b", r"\\lor", s)
    s = re.sub(r"\band\b", r"\\land", s)
    s = re.sub(r"\btrue\b", r"\\mathsf{true}", s)
    s = re.sub(r"\bfalse\b", r"\\mathsf{false}", s)
    s = re.sub(
        r"\b(\w+)\s*\*\s*\1\b",
        lambda m: rf"{m.group(1)}^{{2}}",
        s,
    )
    s = re.sub(
        r"\b(\w+)\s*\*\s*(\w+)\b",
        lambda m: rf"{m.group(1)} \cdot {m.group(2)}",
        s,
    )
    s = re.sub(r">=", r"\\ge", s)
    s = re.sub(r"<=", r"\\le", s)
    return _finalize_latex(s)