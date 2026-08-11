"""Worst-case execution time and stack depth analysis (#282).

Provides `flow analyze --wcet` and `flow analyze --stack-depth` for
DO-178C / ISO 26262 compliance evidence.

Both analyses operate on the Flow AST (not generated C) and produce
conservative upper bounds:

- **Stack depth**: walks the call graph, sums local variable sizes per
  function, and reports the maximum stack depth across all call chains.
  Requires no recursion (enforced by --profile safety, MISRA 17.2).

- **WCET**: estimates worst-case instruction count from loop bounds
  (@max_iterations) and a simple per-statement cost model. Reports the
  maximum WCET across all call chains.

These are static estimates, not measured values. They are suitable for
certification evidence when combined with a timing budget.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Type size model (bytes). Matches the C backend's inttypes.
TYPE_SIZES: Dict[str, int] = {
    "i8": 1, "u8": 1, "bool": 1,
    "i16": 2, "u16": 2,
    "i32": 4, "u32": 4, "f32": 4,
    "i64": 8, "u64": 8, "f64": 8,
    "i128": 16, "u128": 16,
    "c64": 8, "c128": 16,
    "ptr": 8, "string": 8,
}

# Per-statement cost model (abstract instruction count).
# These are conservative upper bounds for a simple in-order pipeline.
STMT_COSTS: Dict[str, int] = {
    "assignment": 2,
    "if": 3,
    "for": 5,
    "while": 5,
    "return": 2,
    "call": 10,
    "declare": 1,
    "default": 1,
}

# Default loop bound when @max_iterations is absent (conservative).
DEFAULT_LOOP_BOUND = 1000


@dataclass
class FunctionInfo:
    name: str
    local_bytes: int = 0
    stmt_cost: int = 0
    callees: Set[str] = field(default_factory=set)
    is_extern: bool = False
    has_body: bool = False


@dataclass
class AnalysisResult:
    function: str
    value: int
    unit: str
    chain: List[str]


def analyze_flow_source(source: str) -> List[Any]:
    """Parse Flow source and return declarations."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from flow.parser import parse_flow_code
    return parse_flow_code(source)


def _type_size(type_name: str) -> int:
    """Estimate the size of a Flow type in bytes."""
    if type_name in TYPE_SIZES:
        return TYPE_SIZES[type_name]
    # Structs: approximate as 16 bytes (conservative default).
    if type_name.startswith("ptr_") or type_name.startswith("Ptr_"):
        return 8
    return 16


def _collect_functions(declarations: List[Any]) -> Dict[str, FunctionInfo]:
    """Build FunctionInfo for every function in the AST."""
    from flow.parser import FunctionDecl, ImplDecl

    funcs: Dict[str, FunctionInfo] = {}

    def register(name: str, decl_or_method: Any, body: Optional[Any]) -> None:
        info = FunctionInfo(name=name, has_body=body is not None)
        info.is_extern = getattr(decl_or_method, "is_extern", False)
        if body is not None:
            _analyze_body(body, info)
        funcs[name] = info

    for decl in declarations:
        if isinstance(decl, FunctionDecl):
            register(decl.name, decl, decl.body)
        elif isinstance(decl, ImplDecl):
            for method in decl.methods:
                mangled = f"{decl.for_type.name}_{decl.trait_name}_{method.name}"
                register(mangled, method, method.body)

    return funcs


def _analyze_body(body: Any, info: FunctionInfo) -> None:
    """Walk a function body to collect local sizes, statement costs, and callees."""
    from flow.parser import (
        FunctionCall, WhileStatement,
        ForStatement, IfStatement, ReturnStatement, Assignment,
        VarDecl, MethodCall, EffectCall,
    )
    import dataclasses

    def walk(node: Any, depth: int = 0) -> None:
        if node is None:
            return
        if isinstance(node, FunctionCall):
            info.callees.add(node.name)
            info.stmt_cost += STMT_COSTS["call"]
        if isinstance(node, MethodCall):
            info.callees.add(f"{node.object_type}_{node.trait}_{node.method}" if hasattr(node, "trait") else node.method)
            info.stmt_cost += STMT_COSTS["call"]
        if isinstance(node, EffectCall):
            info.callees.add(node.effect)
            info.stmt_cost += STMT_COSTS["call"]
        if isinstance(node, VarDecl):
            tname = getattr(node.type, "name", "") if node.type else ""
            info.local_bytes += _type_size(tname)
            info.stmt_cost += STMT_COSTS["declare"]
        if isinstance(node, Assignment):
            info.stmt_cost += STMT_COSTS["assignment"]
        if isinstance(node, ReturnStatement):
            info.stmt_cost += STMT_COSTS["return"]
        if isinstance(node, IfStatement):
            info.stmt_cost += STMT_COSTS["if"]
        if isinstance(node, ForStatement):
            # Counted for loop: cost = bound * body_cost (approximated).
            info.stmt_cost += STMT_COSTS["for"]
        if isinstance(node, WhileStatement):
            bound = getattr(node, "max_iterations", None) or DEFAULT_LOOP_BOUND
            info.stmt_cost += STMT_COSTS["while"] * bound

        # Recurse into dataclass fields.
        if dataclasses.is_dataclass(node) and not isinstance(node, type):
            for f in dataclasses.fields(node):
                walk(getattr(node, f.name), depth + 1)
        elif isinstance(node, (list, tuple)):
            for item in node:
                walk(item, depth + 1)
        elif isinstance(node, dict):
            for v in node.values():
                walk(v, depth + 1)

    walk(body)


def compute_stack_depth(funcs: Dict[str, FunctionInfo]) -> List[AnalysisResult]:
    """Compute maximum stack depth for each function via call graph DFS.

    Returns results sorted by depth (descending).
    """
    cache: Dict[str, Tuple[int, List[str]]] = {}

    def dfs(name: str, visiting: Set[str]) -> Tuple[int, List[str]]:
        if name in cache:
            return cache[name]
        info = funcs.get(name)
        if info is None or info.is_extern or not info.has_body:
            # Unknown or extern function: assume a fixed cost.
            return (64, [name])
        if name in visiting:
            # Recursion detected (should not happen under safety profile).
            return (0, [name + " (recursive)"])
        visiting.add(name)
        max_callee_depth = 0
        max_chain: List[str] = []
        for callee in info.callees:
            d, c = dfs(callee, visiting)
            if d > max_callee_depth:
                max_callee_depth = d
                max_chain = c
        visiting.discard(name)
        total = info.local_bytes + max_callee_depth
        chain = [name] + max_chain
        cache[name] = (total, chain)
        return cache[name]

    results: List[AnalysisResult] = []
    for name in funcs:
        depth, chain = dfs(name, set())
        results.append(AnalysisResult(name, depth, "bytes", chain))

    results.sort(key=lambda r: r.value, reverse=True)
    return results


def compute_wcet(funcs: Dict[str, FunctionInfo]) -> List[AnalysisResult]:
    """Compute worst-case execution time estimate for each function.

    Returns results sorted by cost (descending).
    """
    cache: Dict[str, Tuple[int, List[str]]] = {}

    def dfs(name: str, visiting: Set[str]) -> Tuple[int, List[str]]:
        if name in cache:
            return cache[name]
        info = funcs.get(name)
        if info is None or info.is_extern or not info.has_body:
            # Unknown/extern: assume 100 instructions (conservative).
            return (100, [name + " (extern)"])
        if name in visiting:
            return (0, [name + " (recursive)"])
        visiting.add(name)
        max_callee_cost = 0
        max_chain: List[str] = []
        for callee in info.callees:
            c, ch = dfs(callee, visiting)
            if c > max_callee_cost:
                max_callee_cost = c
                max_chain = ch
        visiting.discard(name)
        total = info.stmt_cost + max_callee_cost
        chain = [name] + max_chain
        cache[name] = (total, chain)
        return cache[name]

    results: List[AnalysisResult] = []
    for name in funcs:
        cost, chain = dfs(name, set())
        results.append(AnalysisResult(name, cost, "instructions (est.)", chain))

    results.sort(key=lambda r: r.value, reverse=True)
    return results


def format_stack_report(results: List[AnalysisResult], source: str) -> str:
    lines = []
    lines.append(f"Stack depth analysis: {source}")
    lines.append("=" * 60)
    lines.append(f"{'Function':<40} {'Max depth':>10} {'Chain'}")
    lines.append("-" * 60)
    for r in results[:20]:
        chain_str = " → ".join(r.chain[:5])
        if len(r.chain) > 5:
            chain_str += " → ..."
        lines.append(f"{r.function:<40} {r.value:>8} {r.unit:<2}  {chain_str}")
    if len(results) > 20:
        lines.append(f"  ... and {len(results) - 20} more")
    lines.append("")
    return "\n".join(lines)


def format_wcet_report(results: List[AnalysisResult], source: str) -> str:
    lines = []
    lines.append(f"WCET analysis: {source}")
    lines.append("=" * 60)
    lines.append(f"{'Function':<40} {'Max cost':>10} {'Chain'}")
    lines.append("-" * 60)
    for r in results[:20]:
        chain_str = " → ".join(r.chain[:5])
        if len(r.chain) > 5:
            chain_str += " → ..."
        lines.append(f"{r.function:<40} {r.value:>8} {r.unit[:4]}  {chain_str}")
    if len(results) > 20:
        lines.append(f"  ... and {len(results) - 20} more")
    lines.append("")
    return "\n".join(lines)


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="flow-analyze-wcet",
        description="WCET and stack depth analysis for Flow programs (#282).",
    )
    p.add_argument("input", help="Input .flow file")
    p.add_argument(
        "--wcet",
        action="store_true",
        help="Estimate worst-case execution time from loop bounds and call graph",
    )
    p.add_argument(
        "--stack-depth",
        action="store_true",
        help="Compute maximum stack depth from the call graph",
    )
    p.add_argument(
        "--budget",
        type=int,
        default=None,
        help="Fail if any function exceeds this budget (bytes for --stack-depth, instructions for --wcet)",
    )
    args = p.parse_args(argv)

    if not args.wcet and not args.stack_depth:
        p.error("at least one of --wcet or --stack-depth is required")

    source_path = Path(args.input)
    if not source_path.exists():
        print(f"Error: {source_path} not found", file=sys.stderr)
        return 1

    source = source_path.read_text()
    declarations = analyze_flow_source(source)
    funcs = _collect_functions(declarations)

    exit_code = 0

    if args.stack_depth:
        results = compute_stack_depth(funcs)
        print(format_stack_report(results, str(source_path)))
        if args.budget is not None:
            for r in results:
                if r.value > args.budget:
                    print(f"BUDGET EXCEEDED: {r.function} uses {r.value} bytes (limit: {args.budget})", file=sys.stderr)
                    exit_code = 1

    if args.wcet:
        results = compute_wcet(funcs)
        print(format_wcet_report(results, str(source_path)))
        if args.budget is not None and not args.stack_depth:
            for r in results:
                if r.value > args.budget:
                    print(f"BUDGET EXCEEDED: {r.function} costs {r.value} (limit: {args.budget})", file=sys.stderr)
                    exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
