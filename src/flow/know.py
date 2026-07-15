#!/usr/bin/env python3
"""flow know — learn a Claim Path in the moment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flow.claim_address import to_legacy_path, try_parse_claim_address
from flow.claim_path import check_duplicate_claims, tier_label
from flow.proof_document import (
    ModuleDoc,
    TheoremDoc,
    flow_expr_to_english,
    flow_expr_to_latex,
    parse_proof_file,
)


@dataclass
class ClaimEntry:
    theorem: TheoremDoc
    module: ModuleDoc
    qualified_path: str


def _default_search_roots(project_root: str) -> List[str]:
    return [
        os.path.join(project_root, "lib", "verify"),
        os.path.join(project_root, "examples", "verify"),
    ]


def _normalize_query(query: str) -> str:
    q = query.strip()
    for prefix in ("verify.", "examples.verify.", "lib.verify."):
        if q.startswith(prefix):
            q = q[len(prefix) :]
    return q


def _package_prefix(module: str) -> str:
    """Package path only — Claim Paths must not appear in module names."""
    if not module or "/" not in module:
        return module
    return ".".join(seg for seg in module.split(".") if "/" not in seg)


def _qualify(module: str, claim_path: str) -> str:
    prefix = _package_prefix(module)
    if prefix:
        return f"{prefix}.{claim_path}"
    return claim_path


def scan_claim_index(
    roots: List[str],
    *,
    recursive: bool = True,
) -> Dict[str, ClaimEntry]:
    index: Dict[str, ClaimEntry] = {}
    for root in roots:
        path = Path(root)
        if not path.exists():
            continue
        files = (
            path.rglob("*.flow")
            if recursive
            else path.glob("*.flow")
        )
        for fp in sorted(files):
            doc = parse_proof_file(str(fp))
            for thm in doc.theorems:
                keys = {
                    thm.claim_path,
                    _qualify(doc.module, thm.claim_path),
                }
                addr = try_parse_claim_address(thm.claim_path)
                if addr:
                    keys.add(addr.guillemets)
                    keys.add(addr.slug)
                    keys.add(addr.display)
                    keys.add(to_legacy_path(addr))
                    keys.add(_qualify(doc.module, addr.guillemets))
                    keys.add(_qualify(doc.module, to_legacy_path(addr)))
                entry = ClaimEntry(
                    theorem=thm,
                    module=doc,
                    qualified_path=_qualify(doc.module, thm.claim_path),
                )
                for key in keys:
                    index[key] = entry
    return index


def lookup_claim(
    query: str,
    project_root: str,
    *,
    search_roots: Optional[List[str]] = None,
) -> Optional[ClaimEntry]:
    roots = search_roots or _default_search_roots(project_root)
    index = scan_claim_index(roots)
    q = _normalize_query(query)
    if q in index:
        return index[q]
    # Fuzzy: facet suffix or ends-with
    for key, entry in index.items():
        if key.endswith(q) or q.endswith(entry.theorem.claim_path):
            return entry
    return None


def format_know(entry: ClaimEntry) -> str:
    thm = entry.theorem
    addr = try_parse_claim_address(thm.claim_path)
    lines: List[str] = []
    lines.append(entry.qualified_path)
    lines.append("")

    if addr:
        lines.append(f"  coordinate: {addr.display}")
        lines.append(f"  syntax:     {addr.guillemets}")
    if thm.meta.means:
        lines.append("  means:   " + thm.meta.means)
    if thm.claim_expr:
        lines.append("  claim:   " + flow_expr_to_english(thm.claim_expr))
        lines.append("           $" + flow_expr_to_latex(thm.claim_expr) + "$")
    if thm.meta.tier:
        lines.append(f"  tier:    {tier_label(thm.meta.tier)} ({thm.meta.tier})")
    if thm.meta.from_source:
        lines.append("  from:    " + thm.meta.from_source)
    if thm.meta.needs:
        lines.append("  needs:   " + ", ".join(thm.meta.needs))
    if thm.meta.used_by:
        lines.append("  used-by: " + ", ".join(thm.meta.used_by))

    lines.append("")
    lines.append(f"  source:  {thm.file_path}")
    lines.append("")
    lines.append("  proof:   run `flow doc proof` on the source file for the full trace")
    return "\n".join(lines)


def lint_duplicate_claims(project_root: str) -> List[str]:
    roots = _default_search_roots(project_root)
    rows: List[Tuple[str, str, str]] = []
    for root in roots:
        path = Path(root)
        if not path.exists():
            continue
        for fp in path.rglob("*.flow"):
            doc = parse_proof_file(str(fp))
            for thm in doc.theorems:
                expr = thm.claim_expr or ""
                if not expr:
                    for step in thm.steps:
                        if step.kind == "therefore":
                            expr = step.text
                            break
                if expr:
                    rows.append((thm.claim_path, expr, str(fp)))
    return check_duplicate_claims(rows)