"""Safety manifest generator for Flow (MISRA/CERT compliance artefact).

Collects safety facts from the AST, type checker results, and C generator
state, then emits a structured compliance report. The manifest is the
artefact that makes safety properties visible and auditable.

Triggered by `--emit-manifest` (usually combined with `--profile safety`).

The manifest has three categories per the safety-profile design:
  PROVEN          - compiler mechanically enforced the invariant
  REJECTED        - compiler found a violation (compilation fails)
  REQUIRES EVIDENCE - invariant cannot be machine-proven; human must justify
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from .parser import FunctionDecl, ImplDecl, FunctionCall


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SafetyProperty:
    name: str
    status: str  # "PROVEN", "REJECTED", "REQUIRES EVIDENCE", "N/A"
    detail: str = ""
    standard: str = ""  # e.g. "MISRA 12.1 / CERT INT32-C"


@dataclass
class SafetyManifest:
    profile: str = "default"
    source_file: str = ""
    properties: List[SafetyProperty] = field(default_factory=list)
    deviations: List[Dict[str, str]] = field(default_factory=list)
    function_count: int = 0
    rt_safe_functions: List[str] = field(default_factory=list)
    heap_using_functions: List[str] = field(default_factory=list)
    recursive_functions: List[str] = field(default_factory=list)
    stack_upper_bound: Optional[str] = None  # future: WCET/stack analysis

    def add(self, name: str, status: str, detail: str = "", standard: str = "") -> None:
        self.properties.append(SafetyProperty(name, status, detail, standard))

    def add_deviation(self, rule: str, reason: str, location: str = "") -> None:
        self.deviations.append({"rule": rule, "reason": reason, "location": location})

    def to_text(self) -> str:
        lines: list[str] = []
        lines.append("Flow Safety Manifest")
        lines.append("=" * 60)
        lines.append(f"Source:    {self.source_file or '<stdin>'}")
        lines.append(f"Profile:   {self.profile}")
        lines.append(f"Functions: {self.function_count}")
        lines.append("")

        # Properties table
        lines.append("Properties")
        lines.append("-" * 60)
        for prop in self.properties:
            status_str = prop.status
            if prop.standard:
                lines.append(f"  {prop.name:<35} {status_str:<18} {prop.standard}")
            else:
                lines.append(f"  {prop.name:<35} {status_str}")
            if prop.detail:
                lines.append(f"    {prop.detail}")
        lines.append("")

        # Function analysis
        if self.rt_safe_functions:
            lines.append(f"RT-safe functions ({len(self.rt_safe_functions)})")
            lines.append("-" * 60)
            for fn in sorted(self.rt_safe_functions):
                lines.append(f"  {fn}")
            lines.append("")

        if self.heap_using_functions:
            lines.append(f"Heap-using functions ({len(self.heap_using_functions)})")
            lines.append("-" * 60)
            for fn in sorted(self.heap_using_functions):
                lines.append(f"  {fn}")
            lines.append("")

        if self.recursive_functions:
            lines.append(f"Recursive functions ({len(self.recursive_functions)})")
            lines.append("-" * 60)
            for fn in sorted(self.recursive_functions):
                lines.append(f"  {fn}")
            lines.append("")

        # Stack bound
        if self.stack_upper_bound:
            lines.append(f"Stack upper bound: {self.stack_upper_bound}")
        else:
            lines.append("Stack upper bound: not analyzed")
        lines.append("")

        # Deviations
        if self.deviations:
            lines.append(f"Deviations ({len(self.deviations)})")
            lines.append("-" * 60)
            for dev in self.deviations:
                lines.append(f"  {dev['rule']}: {dev['reason']}")
                if dev.get("location"):
                    lines.append(f"    at {dev['location']}")
            lines.append("")

        # Summary
        proven = sum(1 for p in self.properties if p.status == "PROVEN")
        rejected = sum(1 for p in self.properties if p.status == "REJECTED")
        evidence = sum(1 for p in self.properties if p.status == "REQUIRES EVIDENCE")
        lines.append("Summary")
        lines.append("-" * 60)
        lines.append(f"  Proven:          {proven}")
        lines.append(f"  Rejected:        {rejected}")
        lines.append(f"  Requires evidence: {evidence}")
        lines.append(f"  Deviations:      {len(self.deviations)}")
        lines.append("")

        return "\n".join(lines)

    def to_json(self) -> str:
        import json
        return json.dumps({
            "profile": self.profile,
            "source": self.source_file,
            "functions": self.function_count,
            "properties": [
                {"name": p.name, "status": p.status, "detail": p.detail, "standard": p.standard}
                for p in self.properties
            ],
            "rt_safe_functions": sorted(self.rt_safe_functions),
            "heap_using_functions": sorted(self.heap_using_functions),
            "recursive_functions": sorted(self.recursive_functions),
            "stack_upper_bound": self.stack_upper_bound,
            "deviations": self.deviations,
            "summary": {
                "proven": sum(1 for p in self.properties if p.status == "PROVEN"),
                "rejected": sum(1 for p in self.properties if p.status == "REJECTED"),
                "requires_evidence": sum(1 for p in self.properties if p.status == "REQUIRES EVIDENCE"),
                "deviations": len(self.deviations),
            },
        }, indent=2)


# ---------------------------------------------------------------------------
# Call graph builder
# ---------------------------------------------------------------------------

HEAP_ALLOC_NAMES: frozenset = frozenset({
    "malloc", "calloc", "realloc", "free", "alloc", "dealloc",
    "alloc_bytes", "alloc_zeroed", "alloc_i32", "alloc_f32", "alloc_f64",
    "arena_create", "arena_destroy",
    "frame_arena_create", "frame_arena_destroy",
})


def _iter_call_names(node: Any, seen: Set[int]) -> list[str]:
    """Recursively collect every FunctionCall.name from an AST node."""
    names: list[str] = []
    if node is None:
        return names
    if isinstance(node, FunctionCall):
        names.append(node.name)
    if dataclasses.is_dataclass(node) and not isinstance(node, type):
        node_id = id(node)
        if node_id in seen:
            return names
        seen.add(node_id)
        for f in dataclasses.fields(node):
            names.extend(_iter_call_names(getattr(node, f.name), seen))
    elif isinstance(node, (list, tuple)):
        for item in node:
            names.extend(_iter_call_names(item, seen))
    elif isinstance(node, dict):
        for value in node.values():
            names.extend(_iter_call_names(value, seen))
    return names


def _build_call_graph(declarations: list[Any]) -> Dict[str, Set[str]]:
    """Build direct call graph: function name -> set of callee names."""
    graph: Dict[str, Set[str]] = {}
    for decl in declarations:
        if isinstance(decl, FunctionDecl) and not getattr(decl, "is_extern", False):
            graph[decl.name] = set(_iter_call_names(decl.body, set()))
        elif isinstance(decl, ImplDecl):
            for method in decl.methods:
                mangled = f"{decl.for_type.name}_{decl.trait_name}_{method.name}"
                graph[mangled] = set(_iter_call_names(method.body, set()))
    return graph


def _detect_recursion(call_graph: Dict[str, Set[str]]) -> list[str]:
    """Find functions that are part of a cycle (direct or transitive)."""
    recursive: set[str] = set()

    def dfs(node: str, visited: set[str], path: list[str]) -> None:
        if node in path:
            # Found a cycle: mark all nodes in the cycle
            cycle_start = path.index(node)
            for n in path[cycle_start:]:
                recursive.add(n)
            return
        if node in visited:
            return
        visited.add(node)
        path.append(node)
        for callee in call_graph.get(node, set()):
            dfs(callee, visited, path)
        path.pop()

    for fn in call_graph:
        dfs(fn, set(), [])

    return sorted(recursive)


def _detect_heap_usage(
    call_graph: Dict[str, Set[str]],
    declarations: list[Any],
) -> list[str]:
    """Find functions that directly or transitively call heap allocation."""
    # Functions that directly call heap allocators
    heap_direct: set[str] = set()
    for fn, callees in call_graph.items():
        if any(c in HEAP_ALLOC_NAMES for c in callees):
            heap_direct.add(fn)

    # Fixed-point: propagate to callers
    heap_all = set(heap_direct)
    changed = True
    while changed:
        changed = False
        for fn, callees in call_graph.items():
            if fn in heap_all:
                continue
            if any(c in heap_all for c in callees):
                heap_all.add(fn)
                changed = True

    return sorted(heap_all)


def _get_rt_safe_functions(declarations: list[Any]) -> list[str]:
    """Find functions marked @rt_safe or in callback lifetime domain."""
    rt_safe: list[str] = []
    for decl in declarations:
        if isinstance(decl, FunctionDecl) and not getattr(decl, "is_extern", False):
            attrs = getattr(decl, "attributes", [])
            if "rt_safe" in attrs or any("lifetime(callback)" in a for a in attrs):
                rt_safe.append(decl.name)
        elif isinstance(decl, ImplDecl):
            for method in decl.methods:
                attrs = getattr(method, "attributes", [])
                if "rt_safe" in attrs or any("lifetime(callback)" in a for a in attrs):
                    mangled = f"{decl.for_type.name}_{decl.trait_name}_{method.name}"
                    rt_safe.append(mangled)
    return rt_safe


# ---------------------------------------------------------------------------
# Main analyzer
# ---------------------------------------------------------------------------

def generate_manifest(
    declarations: list[Any],
    type_checker: Any,
    *,
    source_file: str = "",
    profile: str = "default",
    overflow_check: bool = False,
    type_errors: Optional[list[str]] = None,
) -> SafetyManifest:
    """Generate a safety manifest from compilation state.

    Args:
        declarations: AST declarations (functions, structs, etc.)
        type_checker: the TypeChecker instance after .check() was called
        source_file: path to the source file
        profile: active safety profile (default, safety, flight)
        overflow_check: whether overflow checks were emitted
        type_errors: list of type checker error messages (if any)
    """
    manifest = SafetyManifest(
        profile=profile,
        source_file=source_file,
    )

    type_errors = type_errors or []

    # Count functions
    fn_count = sum(
        1 for d in declarations
        if isinstance(d, FunctionDecl) and not getattr(d, "is_extern", False)
    )
    impl_methods = sum(
        len(d.methods) for d in declarations if isinstance(d, ImplDecl)
    )
    manifest.function_count = fn_count + impl_methods

    # Build call graph
    call_graph = _build_call_graph(declarations)

    # Detect recursion
    manifest.recursive_functions = _detect_recursion(call_graph)

    # Detect heap usage
    manifest.heap_using_functions = _detect_heap_usage(call_graph, declarations)

    # RT-safe functions
    manifest.rt_safe_functions = _get_rt_safe_functions(declarations)

    # --- Properties ---

    # Integer overflow (MISRA 12.1 / CERT INT32-C)
    if overflow_check:
        manifest.add(
            "Integer overflow",
            "PROVEN",
            "Runtime overflow checks emitted for signed +,-,*",
            "MISRA 12.1 / CERT INT32-C",
        )
    else:
        manifest.add(
            "Integer overflow",
            "REQUIRES EVIDENCE",
            "Overflow checks not enabled (use --profile safety)",
            "MISRA 12.1 / CERT INT32-C",
        )

    # Division by zero (MISRA 12.5 / CERT INT33-C)
    div0_errors = [e for e in type_errors if "Division/modulo by zero" in e]
    if div0_errors:
        manifest.add(
            "Division by zero",
            "REJECTED",
            f"{len(div0_errors)} literal div0 error(s)",
            "MISRA 12.5 / CERT INT33-C",
        )
    else:
        manifest.add(
            "Division by zero",
            "PROVEN",
            "Literal div0 rejected at compile time; runtime guard emitted",
            "MISRA 12.5 / CERT INT33-C",
        )

    # Shift UB (MISRA 12.2 / CERT INT34-C)
    shift_errors = [e for e in type_errors if "Shift amount" in e or "Left shift" in e]
    if shift_errors:
        manifest.add(
            "Shift undefined behaviour",
            "REJECTED",
            f"{len(shift_errors)} shift UB error(s)",
            "MISRA 12.2 / CERT INT34-C",
        )
    else:
        manifest.add(
            "Shift undefined behaviour",
            "PROVEN",
            "Literal shift UB rejected at compile time; runtime guard emitted",
            "MISRA 12.2 / CERT INT34-C",
        )

    # RT-safety
    if manifest.rt_safe_functions:
        rt_unsafe = getattr(type_checker, "_rt_unsafe_reason", {})
        rt_violations = [
            fn for fn in manifest.rt_safe_functions if fn in rt_unsafe
        ]
        if rt_violations:
            manifest.add(
                "RT-safety (no heap/lock/device on RT paths)",
                "REJECTED",
                f"{len(rt_violations)} RT-safe function(s) reach banned APIs",
                "Flow @rt_safe policy",
            )
        else:
            manifest.add(
                "RT-safety (no heap/lock/device on RT paths)",
                "PROVEN",
                f"{len(manifest.rt_safe_functions)} @rt_safe function(s) verified",
                "Flow @rt_safe policy",
            )
    else:
        manifest.add(
            "RT-safety (no heap/lock/device on RT paths)",
            "N/A",
            "No @rt_safe functions declared",
        )

    # Dynamic allocation
    if manifest.heap_using_functions:
        manifest.add(
            "Dynamic allocation",
            "REQUIRES EVIDENCE",
            f"{len(manifest.heap_using_functions)} function(s) use heap",
            "MISRA 21.3",
        )
    else:
        manifest.add(
            "Dynamic allocation",
            "PROVEN",
            "No heap allocation detected in call graph",
            "MISRA 21.3",
        )

    # Recursion (MISRA 17.2)
    if manifest.recursive_functions:
        manifest.add(
            "Unbounded recursion",
            "REQUIRES EVIDENCE",
            f"{len(manifest.recursive_functions)} recursive function(s): "
            + ", ".join(manifest.recursive_functions[:5]),
            "MISRA 17.2",
        )
    else:
        manifest.add(
            "Unbounded recursion",
            "PROVEN",
            "No recursion detected in call graph",
            "MISRA 17.2",
        )

    # Unbounded loops (MISRA 17.4) - basic detection
    # TODO: analyze loop bounds; for now, mark as requires evidence
    has_loops = _has_loops(declarations)
    if has_loops:
        manifest.add(
            "Unbounded loops",
            "REQUIRES EVIDENCE",
            "Loops present; bounds not statically proven",
            "MISRA 17.4",
        )
    else:
        manifest.add(
            "Unbounded loops",
            "PROVEN",
            "No loops detected",
            "MISRA 17.4",
        )

    # Null pointer dereference (MISRA 11.8 / CERT ERR33-C)
    # TODO: implement null tracking; for now, requires evidence
    manifest.add(
        "Null pointer dereference",
        "REQUIRES EVIDENCE",
        "Null tracking not yet implemented",
        "MISRA 11.8 / CERT ERR33-C",
    )

    # Stack upper bound
    manifest.stack_upper_bound = None

    return manifest


def _has_loops(declarations: list[Any]) -> bool:
    """Check if any function body contains a for/while loop."""
    for decl in declarations:
        if isinstance(decl, FunctionDecl) and decl.body:
            if _contains_loop(decl.body):
                return True
        elif isinstance(decl, ImplDecl):
            for method in decl.methods:
                if method.body and _contains_loop(method.body):
                    return True
    return False


def _contains_loop(node: Any) -> bool:
    """Recursively check if an AST node contains a loop statement."""
    if node is None:
        return False
    # Check for loop statement types by class name (avoid import issues)
    cls_name = type(node).__name__
    if cls_name in ("ForStatement", "WhileStatement", "ForStmt", "WhileStmt", "ForInStmt"):
        return True
    if dataclasses.is_dataclass(node) and not isinstance(node, type):
        for f in dataclasses.fields(node):
            if _contains_loop(getattr(node, f.name)):
                return True
    elif isinstance(node, (list, tuple)):
        for item in node:
            if _contains_loop(item):
                return True
    return False
