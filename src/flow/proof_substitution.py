#!/usr/bin/env python3
"""Premise instantiation and substitution annotations for proof LaTeX."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from flow.claim_address import ClaimAddress, try_parse_claim_address
from flow.math_prose import flow_expr_to_latex


# therefore-expression templates keyed by (carrier, structure, law)
PREMISE_EXPR: Dict[Tuple[str, str, str], str] = {
    ("Nat", "addition", "zero is the left identity"): "0 + {0} == {0}",
    ("Nat", "addition", "successor on the right steps the sum"): (
        "{0} + succ({1}) == succ({0} + {1})"
    ),
    ("Nat", "addition", "zero is the right identity"): "{0} + 0 == {0}",
    ("Nat", "addition", "order does not matter"): "{0} + {1} == {1} + {0}",
    ("Eq", "equality", "everything equals itself"): "{0} == {0}",
    ("Bool", "disjunction", "order does not matter"): "{0} or {1} == {1} or {0}",
    ("Int", "multiplication", "squaring never yields a negative"): (
        "{0} * {0} >= 0"
    ),
}


@dataclass
class SubstitutionBox:
    """One boxed term substituted into a deductive step."""

    latex: str
    source_step: int
    source_label: str = ""


def _split_args(args: str) -> List[str]:
    if not args.strip():
        return []
    return [part.strip() for part in args.split(",")]


def _substitute_param_names(expr: str, param_names: List[str], values: List[str]) -> str:
    out = expr
    for name, value in zip(param_names, values):
        out = re.sub(rf"\b{re.escape(name)}\b", value, out)
    return out


def _param_names_from_sig(params: str) -> List[str]:
    names: List[str] = []
    for chunk in params.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        names.append(chunk.split(":")[0].strip())
    return names


def instantiate_premise_latex(
    ref: str,
    args: str,
    *,
    claim_expr: str = "",
    params: str = "",
) -> Optional[str]:
    """
    Build the LaTeX equation obtained by instantiating a named premise.
    Returns None when no template is known.
    """
    addr = try_parse_claim_address(ref)
    if addr:
        key = (addr.carrier, addr.structure, addr.law)
        template = PREMISE_EXPR.get(key)
        if template:
            values = _split_args(args)
            filled = template
            for i, value in enumerate(values):
                filled = filled.replace(f"{{{i}}}", value)
            return flow_expr_to_latex(filled)

    if claim_expr and params:
        names = _param_names_from_sig(params)
        values = _split_args(args)
        if names and values and len(names) == len(values):
            return flow_expr_to_latex(
                _substitute_param_names(claim_expr, names, values)
            )

    return None


def substitution_boxes_for_refs(
    ref_steps: List[Tuple[int, str, str]],
    *,
    claim_expr: str = "",
    params: str = "",
    source_labels: Optional[Dict[int, str]] = None,
) -> List[SubstitutionBox]:
    """
    Given (step_number, claim_ref, args) for premise steps, emit boxed substitutions.
    """
    boxes: List[SubstitutionBox] = []
    labels = source_labels or {}
    for step_num, ref, args in ref_steps:
        latex = instantiate_premise_latex(
            ref,
            args,
            claim_expr=claim_expr,
            params=params,
        )
        if latex:
            boxes.append(
                SubstitutionBox(
                    latex=latex,
                    source_step=step_num,
                    source_label=labels.get(step_num, ""),
                )
            )
    return boxes