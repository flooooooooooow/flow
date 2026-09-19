"""Local region inference and conservative non-aliasing proofs (#694).

This is a sound intraprocedural slice of the region-inference work. It proves
a small, useful set of non-aliasing facts inside a single function body with no
manual annotations, and declines (reports "may alias") whenever it cannot
prove disjointness. A wrong proof is undefined behaviour, so the analysis only
ever claims disjointness it can justify from the surface syntax.

What it proves
--------------
Each binding is assigned an abstract *region*: an abstract storage location.

- Two DISTINCT owned local variables occupy distinct storage, so a reference
  rooted at local ``a`` never aliases a reference rooted at local ``b``.
- A freshly allocated local (an array/vector/struct/scalar value binding) does
  not alias any parameter: the local is allocated in this frame after the
  parameters were bound to caller storage.

What it declines
----------------
- Two references rooted at parameters. The caller may legally pass the same
  buffer for two pointer/span parameters, so distinct parameters may alias.
- Anything rooted at a value of unknown provenance, for example the result of
  a function call (which may return a borrow into a parameter).
- A binding that is reassigned or redeclared, whose region is then ambiguous.
- Two references rooted at the same variable.

Connection to restrict emission (#731)
---------------------------------------
The C/MLIR backends may only emit ``restrict``/noalias for pointers they can
prove disjoint. ``restrict_candidates`` returns the local reference bindings
this analysis proves disjoint from every parameter and from each other, which
is the sound subset a backend can annotate on local pointer temporaries. The
analysis never claims two *parameters* are disjoint, so it does not by itself
license ``restrict`` on a function signature: that needs the interprocedural
boundary work still open on #694.

The analysis has no dependency on the type checker's mutable state; it walks
the parsed ``FunctionDecl`` directly, which keeps it easy to test in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from .parser import (
    FunctionDecl,
    Block,
    VarDecl,
    Assignment,
    Variable,
    UnaryOperation,
    SliceExpr,
    ArrayAccess,
    FieldAccess,
    ArrayLiteral,
    VectorLiteral,
    StructLiteral,
    Literal,
    BinaryOperation,
    IfStatement,
    WhileStatement,
    ForStatement,
    MatchStatement,
)


# Region kinds.
LOCAL = "local"      # fresh storage allocated in this frame; distinct ids never alias
PARAM = "param"      # storage bound at entry; distinct params MAY alias each other
UNKNOWN = "unknown"  # top: aliases anything (provenance not established)


@dataclass(frozen=True)
class Region:
    """An abstract storage location.

    ``kind`` is one of ``LOCAL``, ``PARAM`` or ``UNKNOWN``. ``ident`` gives a
    distinct identity to each LOCAL and PARAM region; it is ignored for
    ``UNKNOWN`` (all unknowns are the single top element).
    """

    kind: str
    ident: int = -1

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        if self.kind == UNKNOWN:
            return "Region(UNKNOWN)"
        return f"Region({self.kind}#{self.ident})"


TOP = Region(UNKNOWN)


class RegionInference:
    """Sound, conservative non-aliasing analysis over one function body."""

    def __init__(self, func: FunctionDecl) -> None:
        self.func = func
        self._next_id = 0
        # binding name -> Region
        self.region_of: Dict[str, Region] = {}
        # parameter index -> Region (also mirrored into region_of by name)
        self.param_region: Dict[int, Region] = {}
        self._param_names: Set[str] = set()
        self._analyze()

    # -- region minting -----------------------------------------------------
    def _fresh(self, kind: str) -> Region:
        r = Region(kind, self._next_id)
        self._next_id += 1
        return r

    # -- driver -------------------------------------------------------------
    def _analyze(self) -> None:
        for i, param in enumerate(self.func.parameters):
            r = self._fresh(PARAM)
            self.param_region[i] = r
            self.region_of[param.name] = r
            self._param_names.add(param.name)

        # A binding whose region is not stable across the body cannot carry a
        # single sound region. Pre-scan for names that are reassigned as a
        # whole binding, or declared more than once, and force them to TOP.
        reassigned: Set[str] = set()
        decl_counts: Dict[str, int] = {}
        self._prescan(self.func.body, reassigned, decl_counts)
        self._unstable: Set[str] = set(reassigned)
        self._unstable |= {n for n, c in decl_counts.items() if c > 1}
        # A parameter that is reassigned is also unstable.
        for name in list(self.region_of):
            if name in self._unstable:
                self.region_of[name] = TOP

        self._walk(self.func.body)

        for name in self._unstable:
            self.region_of[name] = TOP

    def _prescan(
        self, block: Block, reassigned: Set[str], decl_counts: Dict[str, int]
    ) -> None:
        for stmt in self._statements(block):
            if isinstance(stmt, VarDecl):
                decl_counts[stmt.name] = decl_counts.get(stmt.name, 0) + 1
            elif isinstance(stmt, Assignment):
                # A whole-binding assignment (`x = ...`) can retarget a
                # reference; an element/field write (`x[i] = ...`) does not.
                if stmt.target is not None and stmt.target_expr is None:
                    reassigned.add(stmt.target)
            for sub in self._sub_blocks(stmt):
                self._prescan(sub, reassigned, decl_counts)

    def _walk(self, block: Block) -> None:
        for stmt in self._statements(block):
            if isinstance(stmt, VarDecl):
                if stmt.name not in self._unstable:
                    self.region_of[stmt.name] = self._region_of_init(stmt.initializer)
            for sub in self._sub_blocks(stmt):
                self._walk(sub)

    # -- AST plumbing -------------------------------------------------------
    @staticmethod
    def _statements(block: Any) -> List[Any]:
        if isinstance(block, Block):
            return block.statements
        if isinstance(block, list):
            return block
        return []

    def _sub_blocks(self, stmt: Any) -> List[Block]:
        blocks: List[Block] = []
        if isinstance(stmt, IfStatement):
            blocks.append(stmt.then_block)
            for _cond, blk in (stmt.elif_blocks or []):
                blocks.append(blk)
            if stmt.else_block is not None:
                blocks.append(stmt.else_block)
        elif isinstance(stmt, (WhileStatement, ForStatement)):
            blocks.append(stmt.body)
        elif isinstance(stmt, MatchStatement):
            for case in stmt.cases:
                blocks.append(case.body)
            if stmt.default_case is not None:
                blocks.append(stmt.default_case)
        elif isinstance(stmt, Block):
            blocks.append(stmt)
        return [b for b in blocks if b is not None]

    # -- region of an initializer expression --------------------------------
    def _region_of_init(self, expr: Any) -> Region:
        """Region a new binding takes on from its initializer.

        Value constructors (array/vector/struct/scalar literals and
        arithmetic) allocate fresh storage, so they get a fresh LOCAL region.
        Borrows and copies inherit the region of their root. Anything whose
        provenance is not established (a function call result, an unrecognised
        form) is TOP, so it is never claimed disjoint from anything.
        """
        if expr is None:
            # `let mut r: T` with no initializer: fresh owned storage.
            return self._fresh(LOCAL)
        if isinstance(expr, (ArrayLiteral, VectorLiteral, StructLiteral, Literal,
                             BinaryOperation)):
            return self._fresh(LOCAL)
        if isinstance(expr, UnaryOperation):
            if expr.operator == "&":
                return self._root_region(expr.operand)
            # A unary arithmetic op (`-x`) yields a fresh value.
            return self._fresh(LOCAL)
        if isinstance(expr, (Variable, SliceExpr, ArrayAccess, FieldAccess)):
            # Conservatively share the root's region. This never over-claims
            # disjointness; it only costs precision for value copies.
            return self._root_region(expr)
        # FunctionCall and everything else: provenance unknown.
        return TOP

    # -- region at the root of a reference expression -----------------------
    def _root_region(self, expr: Any) -> Region:
        if isinstance(expr, Variable):
            return self.region_of.get(expr.name, TOP)
        if isinstance(expr, UnaryOperation) and expr.operator == "&":
            return self._root_region(expr.operand)
        if isinstance(expr, SliceExpr):
            return self._root_region(expr.base)
        if isinstance(expr, ArrayAccess):
            return self._root_region(expr.array)
        if isinstance(expr, FieldAccess):
            return self._root_region(expr.object)
        return TOP

    # -- public query API ---------------------------------------------------
    def region_for(self, expr: Any) -> Region:
        """The region at the root of a reference expression (TOP if unknown)."""
        return self._root_region(expr)

    def may_alias(self, e1: Any, e2: Any) -> bool:
        """True unless the two references are provably disjoint.

        Sound direction: this returns False only when disjointness is proven.
        A caller may safely act on a False result (emit ``restrict``); a True
        result means "not proven", never "proven to alias".
        """
        r1 = self._root_region(e1)
        r2 = self._root_region(e2)
        if r1.kind == UNKNOWN or r2.kind == UNKNOWN:
            return True
        if r1 == r2:
            return True
        # Two distinct parameters may still be aliased by the caller.
        if r1.kind == PARAM and r2.kind == PARAM:
            return True
        # At least one side is a distinct LOCAL region and the regions differ:
        # provably disjoint storage.
        return False

    def provably_disjoint(self, e1: Any, e2: Any) -> bool:
        """True when the two references are proven not to alias."""
        return not self.may_alias(e1, e2)

    def restrict_candidates(self) -> Set[str]:
        """Local reference/value bindings safe to annotate ``restrict``.

        A name qualifies when its region is a distinct LOCAL and no OTHER
        binding shares that region. Such a binding is disjoint from every
        parameter and from every other tracked binding, which is the sound
        subset a backend may mark ``restrict`` on a local pointer (#731).
        """
        counts: Dict[Region, int] = {}
        for region in self.region_of.values():
            if region.kind == LOCAL:
                counts[region] = counts.get(region, 0) + 1
        out: Set[str] = set()
        for name, region in self.region_of.items():
            if name in self._param_names:
                continue
            if region.kind == LOCAL and counts.get(region, 0) == 1:
                out.add(name)
        return out


def analyze_function(func: FunctionDecl) -> RegionInference:
    """Convenience constructor mirroring the other analysis passes."""
    return RegionInference(func)
