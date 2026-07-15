#!/usr/bin/env python3
"""
Compile a Flow proof into a parameterizable kernel and plot its dependency graph.

A proof kernel is a DAG of numbered nodes (steps) with explicit edges (refs).
Parameters (theorem arguments and instantiations) select which branches activate.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from flow.claim_address import try_parse_claim_address
from flow.math_prose import addr_coordinate_display
from flow.proof_document import (
    TheoremDoc,
    TutorialLine,
    build_tutorial_lines,
    parse_proof_file,
    _merged_tier_index,
)


@dataclass
class KernelNode:
    step: int
    kind: str
    text: str
    math: Optional[str] = None
    refs: List[int] = field(default_factory=list)
    active: bool = True


@dataclass
class ProofKernel:
    claim: str
    claim_display: str
    parameters: List[str]
    instantiation: Dict[str, str]
    nodes: List[KernelNode]
    edges: List[Tuple[int, int]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim,
            "claim_display": self.claim_display,
            "parameters": self.parameters,
            "instantiation": self.instantiation,
            "nodes": [asdict(n) for n in self.nodes],
            "edges": [{"from": a, "to": b} for a, b in self.edges],
        }


def _node_kind(english: str, *, has_math: bool) -> str:
    lower = english.lower()
    if has_math and "hence proven" in lower:
        return "conclude"
    if has_math:
        return "deduce"
    if "case " in lower:
        return "case"
    if "invoke" in lower or "inductive boundary" in lower:
        return "invoke"
    if "let " in lower or "denote" in lower:
        return "bind"
    if "induction" in lower or "split into" in lower:
        return "frame"
    if "stipulate" in lower or "axiom" in lower or "prove this derived" in lower:
        return "frame"
    if "consider the base" in lower or "inductive step" in lower:
        return "frame"
    return "step"


def _parse_params(params: str) -> List[str]:
    if not params.strip():
        return []
    names: List[str] = []
    for part in params.split(","):
        name = part.strip().split(":")[0].strip()
        if name:
            names.append(name)
    return names


def _activate_branch(
    thm: TheoremDoc,
    tutorial: List[TutorialLine],
    instantiation: Dict[str, str],
) -> Dict[int, bool]:
    """Mark nodes inactive when instantiation falsifies their case guard."""
    active = {tl.number: True for tl in tutorial if not tl.is_goal and tl.number > 0}
    if not instantiation:
        return active

    for tl in tutorial:
        if tl.is_goal or tl.number <= 0:
            continue
        lower = tl.english.lower()
        for var, val in instantiation.items():
            truthy = val.lower() in ("true", "1", "yes")
            if f"suppose {var}  is  true" in lower or f"suppose {var} is true" in lower:
                if val.lower() not in ("true", "false"):
                    continue
                if (truthy and "false" in val.lower()) or (not truthy and truthy is False and val.lower() == "false"):
                    active[tl.number] = False
            if f"where {var}  =  0" in lower or f"where {var} = 0" in lower:
                if val != "0":
                    active[tl.number] = False
            if f"where {var}  =  0" in lower.replace("=", " = ") and val != "0":
                active[tl.number] = False

    # Propagate: if a case header is inactive, deactivate its descendants until next case
    case_starts = [
        tl.number
        for tl in tutorial
        if not tl.is_goal and tl.english.lower().startswith("case ")
    ]
    ordered = sorted(case_starts)
    for i, start in enumerate(ordered):
        if not active.get(start, True):
            end = ordered[i + 1] if i + 1 < len(ordered) else max(active) + 1
            for n in range(start + 1, end):
                if n in active:
                    active[n] = False

    return active


def compile_proof_kernel(
    thm: TheoremDoc,
    *,
    tier_index: Optional[Dict[str, str]] = None,
    instantiation: Optional[Dict[str, str]] = None,
) -> ProofKernel:
    tutorial = build_tutorial_lines(thm, tier_index=tier_index)
    inst = dict(instantiation or {})
    active_map = _activate_branch(thm, tutorial, inst)

    addr = try_parse_claim_address(thm.claim_path)
    claim_display = addr_coordinate_display(addr) if addr else thm.claim_path

    nodes: List[KernelNode] = []
    edges: List[Tuple[int, int]] = []

    for tl in tutorial:
        if tl.is_goal or tl.number <= 0:
            continue
        kind = _node_kind(tl.english, has_math=bool(tl.math_latex))
        nodes.append(
            KernelNode(
                step=tl.number,
                kind=kind,
                text=tl.english,
                math=tl.math_latex,
                refs=list(tl.refs),
                active=active_map.get(tl.number, True),
            )
        )
        for ref in tl.refs:
            edges.append((ref, tl.number))

    return ProofKernel(
        claim=thm.claim_path,
        claim_display=claim_display,
        parameters=_parse_params(thm.params),
        instantiation=inst,
        nodes=nodes,
        edges=edges,
    )


def compile_file_kernel(
    path: str,
    theorem_index: int = 0,
    *,
    instantiation: Optional[Dict[str, str]] = None,
) -> ProofKernel:
    doc = parse_proof_file(path)
    if not doc.theorems:
        raise ValueError(f"No theorems in {path}")
    thm = doc.theorems[theorem_index]
    return compile_proof_kernel(
        thm,
        tier_index=_merged_tier_index(doc),
        instantiation=instantiation,
    )


def write_kernel_json(
    path: str,
    output: Optional[str] = None,
    *,
    theorem_index: int = 0,
    instantiation: Optional[Dict[str, str]] = None,
) -> str:
    kernel = compile_file_kernel(
        path, theorem_index, instantiation=instantiation
    )
    src = Path(path)
    out = Path(output) if output else src.with_suffix(".proof.kernel.json")
    out.write_text(json.dumps(kernel.to_dict(), indent=2), encoding="utf-8")
    return str(out)


def plot_proof_kernel(
    kernel: ProofKernel,
    output: str,
    *,
    title: Optional[str] = None,
) -> str:
    """Render the kernel DAG. Uses matplotlib when available, else Graphviz DOT."""
    try:
        return _plot_matplotlib(kernel, output, title=title)
    except (ImportError, OSError, RuntimeError, AttributeError):
        return _plot_dot(kernel, output, title=title)


def _plot_dot(kernel: ProofKernel, output: str, *, title: Optional[str]) -> str:
    path = Path(output)
    if path.suffix != ".dot":
        path = path.with_suffix(".dot")

    lines = ["digraph ProofKernel {"]
    lines.append('  rankdir=TB; node [shape=box, fontname="Helvetica"];')
    if title:
        lines.append(f'  label="{_escape_dot(title)}";')
    for node in kernel.nodes:
        color = "#c8e6c9" if node.active else "#eeeeee"
        label = f"{node.step}: {_escape_dot(node.kind)}"
        lines.append(
            f'  n{node.step} [label="{label}", style=filled, fillcolor="{color}"];'
        )
    for a, b in kernel.edges:
        lines.append(f"  n{a} -> n{b};")
    lines.append("}")
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def _plot_matplotlib(kernel: ProofKernel, output: str, *, title: Optional[str]) -> str:
    import matplotlib.pyplot as plt
    import networkx as nx

    g = nx.DiGraph()
    for node in kernel.nodes:
        g.add_node(
            node.step,
            label=f"{node.step}\n{node.kind}",
            active=node.active,
        )
    for a, b in kernel.edges:
        g.add_edge(a, b)

    layers: Dict[int, int] = {}
    for n in nx.topological_sort(g):
        preds = list(g.predecessors(n))
        layers[n] = 0 if not preds else max(layers[p] for p in preds) + 1

    pos = {}
    by_layer: Dict[int, List[int]] = {}
    for n, layer in layers.items():
        by_layer.setdefault(layer, []).append(n)
    for layer, ns in by_layer.items():
        for i, n in enumerate(sorted(ns)):
            pos[n] = (i - len(ns) / 2, -layer)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [
        "#81c784" if g.nodes[n].get("active", True) else "#bdbdbd"
        for n in g.nodes
    ]
    labels = {n: g.nodes[n]["label"] for n in g.nodes}
    nx.draw(
        g,
        pos,
        ax=ax,
        labels=labels,
        node_color=colors,
        node_size=2200,
        font_size=8,
        arrows=True,
        arrowsize=12,
    )
    ax.set_title(title or kernel.claim_display)
    fig.tight_layout()
    out = Path(output)
    if out.suffix not in (".png", ".pdf", ".svg"):
        out = out.with_suffix(".png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return str(out)


def _escape_dot(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')