"""Ordering provenance: what the compiler already knows about an array.

Issue #145 asks for cheap provenance hints so a declarative `sort` can pick an
adaptive algorithm instead of a general one. This pass supplies them.

It is deliberately small. It walks a function body in source order and keeps,
per array variable, two facts:

    order      "asc" / "asc_strict" / "desc" / "desc_strict" / "unknown"
    key_range  [lo, hi] when every element came from an integer literal

Both facts are dropped the moment anything could invalidate them: an
assignment to the variable or to one of its elements, the variable being
passed to a call (which could mutate through the pointer), or the variable
being touched anywhere inside a loop, conditional, or match arm. The pass
never guesses. An unknown fact costs a general plan, a wrong fact costs
correctness, so every ambiguity resolves to "unknown".

Two things produce a fact:

* An array literal initializer whose elements are all integer or float
  literals. Sortedness and the integer key range are read straight off it.
* A `|> sort` on the variable in straight-line code. Afterwards the array is
  in the order that sort produced.

The facts are written back onto the `SortExpr` / `FindExpr` nodes as
`hint_input_order` and `hint_key_range`, where the C generator reads them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .parser import (
    ArrayLiteral,
    Assignment,
    Block,
    FindExpr,
    ForStatement,
    FunctionCall,
    FunctionDecl,
    IfStatement,
    Literal,
    MatchStatement,
    MethodCall,
    SortExpr,
    UnaryOperation,
    Variable,
    VarDecl,
    WhileStatement,
)

__all__ = ["ArrayFacts", "annotate_ordering_hints", "analyze_function"]


@dataclass
class ArrayFacts:
    """What is known about one array variable at one point in the body."""

    order: str = "unknown"
    key_range: Optional[Tuple[int, int]] = None


@dataclass
class _Analysis:
    """Per-function result, kept for tests and for the explain report."""

    sites: List[Tuple[Any, ArrayFacts]] = field(default_factory=list)

    def facts_for(self, node: Any) -> ArrayFacts:
        for site, facts in self.sites:
            if site is node:
                return facts
        return ArrayFacts()


def annotate_ordering_hints(functions: List[FunctionDecl]) -> None:
    """Run the pass over every function and write hints onto the AST."""
    for fn in functions:
        body = getattr(fn, "body", None)
        if body is None:
            continue
        analyze_function(fn)


def analyze_function(fn: FunctionDecl) -> _Analysis:
    """Analyze one function, annotate its sort/search sites, return the record."""
    analysis = _Analysis()
    body = getattr(fn, "body", None)
    if body is None:
        return analysis
    known: Dict[str, ArrayFacts] = {}
    _walk_block(body, known, analysis, straight_line=True)
    return analysis


# ---------------------------------------------------------------------------
# statement walk
# ---------------------------------------------------------------------------


def _statements(block: Any) -> List[Any]:
    if isinstance(block, Block):
        return list(block.statements)
    if isinstance(block, list):
        return list(block)
    return []


def _walk_block(
    block: Any,
    known: Dict[str, ArrayFacts],
    analysis: _Analysis,
    straight_line: bool,
) -> None:
    for stmt in _statements(block):
        _walk_statement(stmt, known, analysis, straight_line)


def _walk_statement(
    stmt: Any,
    known: Dict[str, ArrayFacts],
    analysis: _Analysis,
    straight_line: bool,
) -> None:
    # Record hints for every selection site inside this statement first: the
    # facts that hold on entry are the ones the site sees.
    for site in _selection_sites(stmt):
        _record_site(site, known, analysis, straight_line)

    if isinstance(stmt, VarDecl):
        _kill(known, _mutated(stmt))
        if stmt.initializer is not None and straight_line:
            facts = _facts_from_literal(stmt.initializer, getattr(stmt.type, "size", None))
            if facts is not None:
                known[stmt.name] = facts
                return
        known.pop(stmt.name, None)
        return

    if isinstance(stmt, (IfStatement, WhileStatement, ForStatement, MatchStatement)):
        # Anything a nested block writes is unknown afterwards, and a hint
        # taken inside a loop body cannot be trusted on the second iteration.
        _kill(known, _mutated(stmt))
        _walk_nested(stmt, known, analysis)
        return

    sorted_var = _straight_line_sort_target(stmt)
    if sorted_var is not None and straight_line:
        name, produced = sorted_var
        known[name] = produced
        return

    _kill(known, _mutated(stmt))


def _walk_nested(stmt: Any, known: Dict[str, ArrayFacts], analysis: _Analysis) -> None:
    """Visit nested blocks with no usable facts, so their sites still register."""
    inner: Dict[str, ArrayFacts] = {}
    for block in _nested_blocks(stmt):
        _walk_block(block, inner, analysis, straight_line=False)


def _nested_blocks(stmt: Any) -> List[Any]:
    blocks: List[Any] = []
    if isinstance(stmt, IfStatement):
        blocks.append(stmt.then_block)
        for _, blk in stmt.elif_blocks or []:
            blocks.append(blk)
        if stmt.else_block is not None:
            blocks.append(stmt.else_block)
    elif isinstance(stmt, (WhileStatement, ForStatement)):
        blocks.append(stmt.body)
    elif isinstance(stmt, MatchStatement):
        for case in getattr(stmt, "cases", []) or []:
            body = getattr(case, "body", None)
            if body is not None:
                blocks.append(body)
    return blocks


def _record_site(
    site: Any,
    known: Dict[str, ArrayFacts],
    analysis: _Analysis,
    straight_line: bool,
) -> None:
    facts = ArrayFacts()
    if straight_line:
        name = _array_var_name(site.array)
        if name is not None and name in known:
            facts = ArrayFacts(known[name].order, known[name].key_range)
    site.hint_input_order = facts.order
    site.hint_key_range = list(facts.key_range) if facts.key_range else None
    analysis.sites.append((site, facts))


def _straight_line_sort_target(stmt: Any) -> Optional[Tuple[str, ArrayFacts]]:
    """`xs |> sort` as a bare statement leaves `xs` in a known order."""
    expr = _bare_expression(stmt)
    if not isinstance(expr, SortExpr):
        return None
    name = _array_var_name(expr.array)
    if name is None:
        return None
    if expr.keys:
        # Multi-key order says nothing about whole-element order.
        return None
    direction = "desc" if expr.descending else "asc"
    # `unique` removes adjacent equals, so the result is strictly ordered.
    order = direction + "_strict" if expr.unique else direction
    return name, ArrayFacts(order=order)


def _bare_expression(stmt: Any) -> Any:
    """The expression of a statement that is just an expression."""
    if isinstance(stmt, (SortExpr, FindExpr)):
        return stmt
    for attr in ("expression", "expr", "value"):
        inner = getattr(stmt, attr, None)
        if isinstance(inner, (SortExpr, FindExpr)):
            return inner
    return None


def _array_var_name(expr: Any) -> Optional[str]:
    if isinstance(expr, Variable):
        return expr.name
    return None


# ---------------------------------------------------------------------------
# invalidation
# ---------------------------------------------------------------------------


def _kill(known: Dict[str, ArrayFacts], names: Set[str]) -> None:
    for name in names:
        known.pop(name, None)


def _mutated(node: Any) -> Set[str]:
    """Names this node could write to, directly or through a callee."""
    out: Set[str] = set()
    _collect_mutations(node, out)
    return out


def _collect_mutations(node: Any, out: Set[str]) -> None:
    if node is None:
        return
    if isinstance(node, (list, tuple)):
        for item in node:
            _collect_mutations(item, out)
        return
    if isinstance(node, Assignment):
        if node.target:
            out.add(node.target)
        base = _base_name(node.target_expr)
        if base:
            out.add(base)
    elif isinstance(node, VarDecl):
        out.add(node.name)
    elif isinstance(node, (FunctionCall, MethodCall)):
        # An array argument decays to a pointer, so the callee may reorder it.
        for arg in getattr(node, "arguments", []) or []:
            base = _base_name(arg)
            if base:
                out.add(base)
    elif isinstance(node, SortExpr):
        # Ordering is in place, so the array it names is written.
        base = _base_name(node.array)
        if base:
            out.add(base)
    elif isinstance(node, UnaryOperation):
        if getattr(node, "operator", None) in ("&", "addr"):
            base = _base_name(getattr(node, "operand", None))
            if base:
                out.add(base)
    if hasattr(node, "__dataclass_fields__"):
        for name in node.__dataclass_fields__:
            _collect_mutations(getattr(node, name, None), out)


def _base_name(expr: Any) -> Optional[str]:
    """Root variable of `x`, `x[i]`, `x.f`, `x[i].f`."""
    seen = 0
    while expr is not None and seen < 32:
        seen += 1
        if isinstance(expr, Variable):
            return expr.name
        nxt = None
        for attr in ("array", "base", "object"):
            candidate = getattr(expr, attr, None)
            if candidate is not None:
                nxt = candidate
                break
        if nxt is None:
            return None
        expr = nxt
    return None


def _selection_sites(node: Any) -> List[Any]:
    out: List[Any] = []
    _collect_sites(node, out, skip_blocks=True)
    return out


def _collect_sites(node: Any, out: List[Any], skip_blocks: bool) -> None:
    if node is None:
        return
    if skip_blocks and isinstance(node, Block):
        return
    if isinstance(node, (list, tuple)):
        for item in node:
            _collect_sites(item, out, skip_blocks)
        return
    if isinstance(node, (SortExpr, FindExpr)):
        out.append(node)
    if hasattr(node, "__dataclass_fields__"):
        for name in node.__dataclass_fields__:
            _collect_sites(getattr(node, name, None), out, skip_blocks)


# ---------------------------------------------------------------------------
# literal analysis
# ---------------------------------------------------------------------------


def _facts_from_literal(expr: Any, declared_size: Any = None) -> Optional[ArrayFacts]:
    if not isinstance(expr, ArrayLiteral):
        return None
    # A short initializer zero-fills the rest, so the literal describes only a
    # prefix and says nothing about the whole array.
    if declared_size is not None:
        try:
            if int(declared_size) != len(expr.elements):
                return None
        except (TypeError, ValueError):
            return None
    values: List[float] = []
    ints: List[int] = []
    all_int = True
    for element in expr.elements:
        value = _numeric_literal(element)
        if value is None:
            return None
        values.append(value)
        if isinstance(value, int):
            ints.append(value)
        else:
            all_int = False
    if not values:
        return ArrayFacts()

    order = _order_of(values)
    key_range = (min(ints), max(ints)) if all_int and ints else None
    return ArrayFacts(order=order, key_range=key_range)


def _numeric_literal(expr: Any):
    if isinstance(expr, UnaryOperation) and getattr(expr, "operator", None) == "-":
        inner = _numeric_literal(getattr(expr, "operand", None))
        return None if inner is None else -inner
    if not isinstance(expr, Literal):
        return None
    text = str(expr.value)
    try:
        if any(ch in text for ch in ".eE") and not text.lower().startswith("0x"):
            return float(text)
        return int(text, 0)
    except ValueError:
        return None


def _order_of(values: List[float]) -> str:
    ascending = all(a <= b for a, b in zip(values, values[1:]))
    strict_asc = all(a < b for a, b in zip(values, values[1:]))
    descending = all(a >= b for a, b in zip(values, values[1:]))
    strict_desc = all(a > b for a, b in zip(values, values[1:]))
    if strict_asc:
        return "asc_strict"
    if strict_desc:
        return "desc_strict"
    if ascending:
        return "asc"
    if descending:
        return "desc"
    return "unknown"
