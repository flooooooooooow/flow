"""Prove span indices in bounds at compile time, so the check costs nothing.

Flow emits a bounds check on every span access. The check is real safety, but it is
paid per access, and in a numeric kernel almost every one of those accesses is already
provably safe: the index is a loop variable, and the loop runs to a bound that is either
the span's own length or a value the caller passed alongside it.

This pass reads that structure back out. It walks each function over an affine domain,
carries an interval for every loop variable, and at each access discharges two
obligations:

    idx >= 0            the index does not walk off the front
    idx <= len - 1      and not off the back

Each obligation reduces to an affine form that must be non-negative. Three things can
happen to it:

    the form is a non-negative constant   -> Proven. Emit no check.
    the form is a negative constant       -> Refuted. This is a compile error.
    the form still has symbols in it      -> residual. If every symbol is invariant
                                             across the enclosing loop, the obligation
                                             is too, and one check before the loop
                                             covers every iteration of it.

That last case is the one that matters for real code. `for i in 0 to n { xs[i] }` cannot
be proven outright, because nothing local relates `n` to `xs.len`. But the obligation it
leaves, `0 <= n && n <= xs.len`, does not mention `i` at all. Checking it once at the top
of the loop is exactly equivalent to checking it on every iteration, and it costs O(1)
instead of O(n).

Soundness of the hoist rests on three conditions, all checked before it is taken:

  - Every symbol in the obligation is unassigned in the loop body, so the value tested at
    the top is the value that would have been tested inside.
  - The access is reached unconditionally on every iteration, with no `if` between it and
    the loop header and no `break`, `continue` or `return` anywhere in the body. Otherwise
    the loop might legitimately never reach the extreme index, and a hoisted check would
    abort a program that was correct.
  - The guard is itself predicated on the loop actually running. A loop with an empty
    range performs no access and must not be made to fault.

`for i in A to B` with no explicit step picks its direction at run time from `A <= B`, so
a descending run is possible and the interval for `i` is the union of both directions:
[min(A, B+1), max(A, B-1)]. Keeping the union is what makes the negative half of the
obligation real rather than decorative.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .parser import (
    ArrayAccess,
    MatchStatement,
    ReturnStatement,
    VarDecl,
    Assignment,
    BinaryOperation,
    FieldAccess,
    ForStatement,
    FunctionCall,
    IfStatement,
    Literal,
    SliceExpr,
    Variable,
    WhileStatement,
)


# --- the affine domain --------------------------------------------------------------

def _stmts(body) -> list:
    """Statement list from a body that may be a Block, a list, or absent."""
    if body is None:
        return []
    inner = getattr(body, "statements", None)
    if inner is not None:
        return list(inner)
    if isinstance(body, list):
        return body
    return []


@dataclass(frozen=True)
class Sym:
    """An opaque non-constant term, keyed so equal expressions cancel.

    The key is a printed form of the expression. Two occurrences of `c.n_beams` produce
    the same key and therefore cancel in a subtraction, which is the whole reason an
    obligation like `len - n` can ever collapse to a constant.
    """

    key: str


@dataclass
class Affine:
    """const + sum(coeff * monomial), where a monomial is a sorted tuple of symbols.

    Degree one is the common case and behaves exactly like an affine form. Degree two
    appears the moment a kernel indexes a matrix: `values[row * width + column]` has the
    monomial `row*width`, and substituting the row's range for `row` leaves `width*rows`,
    a product of two loop-invariant quantities. Keeping such a product as an atomic term
    is what lets the obligation `len >= width * rows` be stated at all.
    """

    const: int = 0
    # monomial (a sorted tuple of symbols, never empty) -> integer coefficient
    terms: Dict[Tuple[Sym, ...], int] = field(default_factory=dict)

    @staticmethod
    def of_const(c: int) -> "Affine":
        return Affine(const=c)

    @staticmethod
    def of_sym(s: Sym) -> "Affine":
        return Affine(const=0, terms={(s,): 1})

    def is_const(self) -> bool:
        return not self.terms

    def degree(self) -> int:
        return max((len(m) for m in self.terms), default=0)

    def __add__(self, other: "Affine") -> "Affine":
        terms = dict(self.terms)
        for m, c in other.terms.items():
            merged = terms.get(m, 0) + c
            if merged:
                terms[m] = merged
            else:
                terms.pop(m, None)
        return Affine(self.const + other.const, terms)

    def __neg__(self) -> "Affine":
        return Affine(-self.const, {m: -c for m, c in self.terms.items()})

    def __sub__(self, other: "Affine") -> "Affine":
        return self + (-other)

    def scale(self, k: int) -> "Affine":
        if k == 0:
            return Affine.of_const(0)
        return Affine(self.const * k, {m: c * k for m, c in self.terms.items()})

    def mul(self, other: "Affine") -> "Affine":
        """Polynomial product. Monomials concatenate and stay sorted."""
        out = Affine.of_const(self.const * other.const)
        for m, c in self.terms.items():
            if other.const:
                out = out + Affine(0, {m: c * other.const})
        for m, c in other.terms.items():
            if self.const:
                out = out + Affine(0, {m: c * self.const})
        for m1, c1 in self.terms.items():
            for m2, c2 in other.terms.items():
                merged = tuple(sorted(m1 + m2, key=lambda s: s.key))
                out = out + Affine(0, {merged: c1 * c2})
        return out

    def mentions(self, s: Sym) -> bool:
        return any(s in m for m in self.terms)

    def degree_of(self, s: Sym) -> int:
        return max((m.count(s) for m in self.terms), default=0)


# An interval whose endpoints are themselves affine forms. `None` is unbounded.
Interval = Tuple[Optional[Affine], Optional[Affine]]


# --- deciding whether a linear fact set implies an obligation -----------------------

class Facts:
    """A conjunction of `affine >= 0` constraints, with an implication test.

    The test is Fourier-Motzkin: to decide whether the facts imply `goal >= 0`, assume
    the negation (`-goal - 1 >= 0`, valid because every quantity here is an integer) and
    eliminate variables until either a contradiction appears, which proves the goal, or
    the system stays satisfiable, which means the obligation is genuinely open.

    Elimination is exact over the rationals and the system is tiny, so this terminates
    immediately in practice: a few symbols and a handful of constraints.
    """

    LIMIT = 60  # constraint-count ceiling; give up rather than blow up on odd input

    def __init__(self, constraints: Optional[List[Affine]] = None):
        self.constraints: List[Affine] = list(constraints or [])

    def plus(self, *extra: Affine) -> "Facts":
        return Facts(self.constraints + [c for c in extra if c is not None])

    def implies(self, goal: Affine) -> bool:
        if goal.is_const():
            return goal.const >= 0
        # goal < 0  <=>  goal <= -1  <=>  -goal - 1 >= 0
        system = self.constraints + [(-goal) - Affine.of_const(1)]
        return not self._satisfiable(system)

    def infeasible(self) -> bool:
        """True when the fact set contradicts itself, so its branch cannot be taken."""
        return not self._satisfiable(self.constraints)

    @classmethod
    def _satisfiable(cls, system: List[Affine]) -> bool:
        rows = [Affine(c.const, dict(c.terms)) for c in system]
        # Each distinct monomial is linearised into its own variable. That is sound:
        # any solution of the nonlinear system is a solution of the linear one, so a
        # contradiction here is a contradiction there. It is not complete, which only
        # ever means an obligation stays open and its check stays.
        symbols = sorted({m for r in rows for m in r.terms},
                         key=lambda m: tuple(s.key for s in m))
        for sym in symbols:
            positive, negative, rest = [], [], []
            for r in rows:
                coeff = r.terms.get(sym, 0)
                if coeff > 0:
                    positive.append(r)
                elif coeff < 0:
                    negative.append(r)
                else:
                    rest.append(r)
            if len(positive) * len(negative) + len(rest) > cls.LIMIT:
                return True  # too big to decide: report satisfiable, which proves nothing
            combined = list(rest)
            for hi in positive:
                for lo in negative:
                    a = hi.terms[sym]
                    b = -lo.terms[sym]
                    combined.append(hi.scale(b) + lo.scale(a))
            rows = combined
        for r in rows:
            if r.const < 0:            # 0 >= 0 reduced to a negative constant
                return False
        return True


# --- verdicts -----------------------------------------------------------------------

PROVEN = "proven"          # no check needed anywhere
REFUTED = "refuted"        # provably out of bounds: a compile error
HOIST = "hoist"            # safe once one guard runs at the top of the enclosing loop
UNKNOWN = "unknown"        # keep the per-access check


@dataclass
class Guard:
    """One direction's residual obligations for a loop.

    `ascending` records which run of the loop these apply to. A loop whose direction is
    settled statically produces one of these; a loop that could go either way produces
    both, and codegen emits them as the two arms of a single test on `start <= end`.
    """

    ascending: bool
    obligations: List[Affine] = field(default_factory=list)


@dataclass
class Verdict:
    kind: str
    loop: Optional[ForStatement] = None
    detail: str = ""


@dataclass
class LoopGuards:
    """Everything codegen needs to emit one loop's guard."""

    loop: ForStatement
    ascending: List[Affine] = field(default_factory=list)
    descending: List[Affine] = field(default_factory=list)
    direction_known: Optional[bool] = None  # True ascending-only, False descending-only

    def is_empty(self) -> bool:
        return not self.ascending and not self.descending


@dataclass
class _LenOf:
    """Marker for `<span>.len`, so codegen can rebuild a guard expression in C."""

    span: object


@dataclass
class _LoopFrame:
    var: str
    stmt: ForStatement
    start: Optional[Affine]
    end: Optional[Affine]
    step_is_one: bool
    assigned: set
    allows_hoist: bool


class BoundsProver:
    """Walks one function and classifies every span access in it."""

    def __init__(self, span_lengths: Optional[Dict[str, Affine]] = None):
        self.verdicts: Dict[int, Verdict] = {}
        self.loop_guards: Dict[int, LoopGuards] = {}
        self.errors: List[Tuple[str, ArrayAccess]] = []
        self.sym_expr: Dict[Sym, object] = {}
        self._lengths: Dict[str, Affine] = dict(span_lengths or {})
        self._frames: List[_LoopFrame] = []
        self._reassigned: set = set()
        self._length_syms: set = set()
        # name -> affine form it was bound to, for integer `let`s whose definition is
        # itself affine. An index written `fbar[slot]` says nothing on its own; the
        # `let slot: i32 = row * width + column` two lines above says everything.
        self._defs: Dict[str, Affine] = {}

    # -- expressions to affine forms --------------------------------------------------

    def _key(self, expr) -> Optional[str]:
        if isinstance(expr, Variable):
            return f"v:{expr.name}"
        if isinstance(expr, FieldAccess):
            inner = self._key(expr.object)
            return f"{inner}.{expr.field}" if inner else None
        return None

    def _sym(self, expr) -> Optional[Sym]:
        key = self._key(expr)
        if key is None:
            return None
        s = Sym(key)
        self.sym_expr.setdefault(s, expr)
        return s

    def affine(self, expr) -> Optional[Affine]:
        if isinstance(expr, Literal):
            # The lexer keeps a literal's text, so an integer arrives as "0", not 0.
            value = expr.value
            if isinstance(value, bool):
                return None
            if isinstance(value, int):
                return Affine.of_const(value)
            if isinstance(value, str):
                text = value.strip().replace("_", "")
                try:
                    base = 0 if text[:2].lower() in ("0x", "0b", "0o") else 10
                    return Affine.of_const(int(text, base))
                except (ValueError, IndexError):
                    return None
            return None
        if isinstance(expr, (Variable, FieldAccess)):
            if isinstance(expr, Variable):
                known = self._defs.get(expr.name)
                if known is not None and expr.name not in self._reassigned:
                    return known
            s = self._sym(expr)
            if s is None:
                return None
            if s.key.endswith(".len"):
                self._length_syms.add(s)
            return Affine.of_sym(s)
        if isinstance(expr, BinaryOperation):
            left = self.affine(expr.left)
            right = self.affine(expr.right)
            if left is None or right is None:
                return None
            if expr.operator == "+":
                return left + right
            if expr.operator == "-":
                return left - right
            if expr.operator == "*":
                if left.is_const():
                    return right.scale(left.const)
                if right.is_const():
                    return left.scale(right.const)
                product = left.mul(right)
                # Degree is capped: past two the linearisation stops paying for itself
                # and the obligations stop being things a guard can cheaply evaluate.
                return product if product.degree() <= 2 else None
        return None

    # -- structural helpers ----------------------------------------------------------

    @staticmethod
    def _assigned_in(node, include_decls: bool = True) -> set:
        """Names this subtree writes to.

        `include_decls` distinguishes the two questions asked of this walk. For loop
        invariance a name rebound by a `let` inside the body is just as unstable as one
        assigned to, so declarations count. For deciding whether a span's recorded length
        still holds, only a genuine reassignment matters, and its own declaration must
        not disqualify it.
        """
        found = set()

        def walk(n):
            if isinstance(n, Assignment):
                target = getattr(n, "target", None)
                if isinstance(target, str) and target:
                    found.add(target)
                elif isinstance(target, Variable):
                    found.add(target.name)
                base = getattr(n, "target_expr", None)
                while isinstance(base, (FieldAccess, ArrayAccess)):
                    base = getattr(base, "object", None) or getattr(base, "array", None)
                if isinstance(base, Variable):
                    found.add(base.name)
            if include_decls and isinstance(n, VarDecl):
                found.add(n.name)
            for attr in ("body", "then_block", "else_block", "elif_blocks", "statements",
                         "cases", "default_case"):
                sub = getattr(n, attr, None)
                if sub is not None and not isinstance(sub, list):
                    sub = _stmts(sub)
                if isinstance(sub, list):
                    for item in sub:
                        if isinstance(item, tuple):
                            for part in item:
                                for st in (part if isinstance(part, list) else _stmts(part)):
                                    walk(st)
                        elif hasattr(item, "__dataclass_fields__"):
                            walk(item)
            for attr in ("value", "condition", "index", "array", "left", "right", "object"):
                sub = getattr(n, attr, None)
                if sub is not None and hasattr(sub, "__dataclass_fields__"):
                    walk(sub)

        walk(node)
        return found

    @staticmethod
    def _has_early_exit(body) -> bool:
        from .parser import BreakStatement, ContinueStatement, ReturnStatement

        found = False

        def walk(n):
            nonlocal found
            if found:
                return
            if isinstance(n, (BreakStatement, ContinueStatement, ReturnStatement)):
                found = True
                return
            for attr in ("body", "then_block", "else_block", "elif_blocks", "statements",
                         "cases", "default_case"):
                sub = getattr(n, attr, None)
                if sub is not None and not isinstance(sub, list):
                    sub = _stmts(sub)
                if isinstance(sub, list):
                    for item in sub:
                        if isinstance(item, tuple):
                            for part in item:
                                for st in (part if isinstance(part, list) else _stmts(part)):
                                    walk(st)
                        elif hasattr(item, "__dataclass_fields__"):
                            walk(item)

        for st in _stmts(body):
            walk(st)
        return found

    def _assigned_in_block(self, body, include_decls: bool = True) -> set:
        found = set()
        for st in _stmts(body):
            found |= self._assigned_in(st, include_decls)
        return found

    # -- the walk --------------------------------------------------------------------

    def run(self, fn) -> None:
        body = getattr(fn, "body", None)
        self._reassigned = self._assigned_in_block(body, include_decls=False)
        self._walk_block(body, conditional=False)

    def _walk_block(self, body, conditional: bool) -> None:
        outer = dict(self._defs)
        try:
            for st in _stmts(body):
                self._walk_stmt(st, conditional)
        finally:
            self._defs = outer

    def _walk_stmt(self, st, conditional: bool) -> None:
        if isinstance(st, VarDecl):
            self._walk_expr(st.initializer, conditional)
            self._record_length(st)
            self._record_definition(st)
            return
        if isinstance(st, ForStatement):
            self._walk_for(st, conditional)
            return
        if isinstance(st, IfStatement):
            self._walk_expr(st.condition, conditional)
            # Under a branch an access is not reached every iteration, so its obligation
            # cannot move to a loop header.
            self._walk_block(st.then_block, conditional=True)
            for entry in (st.elif_blocks or []):
                cond, block = entry[0], entry[1]
                self._walk_expr(cond, conditional=True)
                self._walk_block(block, conditional=True)
            self._walk_block(st.else_block, conditional=True)
            return
        if isinstance(st, WhileStatement):
            self._walk_expr(st.condition, conditional)
            self._walk_block(st.body, conditional=True)
            return
        if isinstance(st, MatchStatement):
            self._walk_expr(st.value, conditional)
            for case in st.cases or []:
                self._walk_block(getattr(case, "body", None), conditional=True)
            self._walk_block(getattr(st, "default_case", None), conditional=True)
            return
        if isinstance(st, Assignment):
            self._walk_expr(getattr(st, "target_expr", None), conditional)
            self._walk_expr(st.value, conditional)
            return
        if isinstance(st, ReturnStatement):
            self._walk_expr(st.value, conditional)
            return
        if isinstance(st, (FunctionCall, ArrayAccess, BinaryOperation, FieldAccess)):
            self._walk_expr(st, conditional)
            return
        for attr in ("value", "expr", "condition"):
            sub = getattr(st, attr, None)
            if sub is not None and hasattr(sub, "__dataclass_fields__"):
                self._walk_expr(sub, conditional)
        for attr in ("body", "statements"):
            sub = getattr(st, attr, None)
            if sub is not None:
                self._walk_block(sub, conditional=True)

    def _record_definition(self, decl: VarDecl) -> None:
        """Remember an integer `let` whose initialiser is itself an affine form."""
        if decl.name in self._reassigned or not _is_integer_decl(decl):
            self._defs.pop(decl.name, None)
            return
        form = self.affine(decl.initializer)
        if form is None:
            self._defs.pop(decl.name, None)
        else:
            self._defs[decl.name] = form

    def _record_length(self, decl: VarDecl) -> None:
        init = decl.initializer
        if isinstance(init, SliceExpr):
            start = self.affine(init.start) if init.start is not None else Affine.of_const(0)
            end = self.affine(init.end) if init.end is not None else None
            if start is not None and end is not None:
                self._lengths[decl.name] = end - start
                return
        self._lengths.pop(decl.name, None)

    def _walk_for(self, st: ForStatement, conditional: bool) -> None:
        self._walk_expr(st.range_start, conditional)
        self._walk_expr(st.range_end, conditional)
        step_is_one = st.step is None or (
            isinstance(st.step, Literal) and str(st.step.value).strip() == "1"
        )
        frame = _LoopFrame(
            var=st.variable,
            stmt=st,
            start=self.affine(st.range_start),
            end=self.affine(st.range_end),
            step_is_one=step_is_one,
            assigned=self._assigned_in_block(st.body),
            allows_hoist=not self._has_early_exit(st.body),
        )
        self._frames.append(frame)
        try:
            self._walk_block(st.body, conditional)
        finally:
            self._frames.pop()

    def _walk_expr(self, expr, conditional: bool) -> None:
        if expr is None or not hasattr(expr, "__dataclass_fields__"):
            return
        if isinstance(expr, ArrayAccess):
            self._walk_expr(expr.array, conditional)
            self._walk_expr(expr.index, conditional)
            self._classify(expr, conditional)
            return
        for attr in ("left", "right", "object", "array", "index", "base", "start", "end",
                     "value", "condition", "then_expr", "else_expr"):
            sub = getattr(expr, attr, None)
            if sub is not None and hasattr(sub, "__dataclass_fields__"):
                self._walk_expr(sub, conditional)
        if isinstance(expr, FunctionCall):
            for arg in expr.arguments or []:
                self._walk_expr(arg, conditional)

    # -- the decision ----------------------------------------------------------------

    def _base_facts(self) -> Facts:
        """What is true regardless of any branch.

        A span's length is its element count and cannot be negative. That single axiom
        is what lets the descending run of `for i in 0 to xs.len` be discharged as
        unreachable rather than guarded.
        """
        return Facts([Affine.of_sym(s) for s in self._length_syms])

    def _length_of(self, access: ArrayAccess) -> Affine:
        name = access.array.name if isinstance(access.array, Variable) else None
        if name is not None and name in self._lengths and name not in self._reassigned:
            return self._lengths[name]
        base_key = self._key(access.array)
        s = Sym(f"{base_key}.len")
        self.sym_expr.setdefault(s, _LenOf(access.array))
        self._length_syms.add(s)
        return Affine.of_sym(s)

    def _classify(self, access: ArrayAccess, conditional: bool) -> None:
        if self._key(access.array) is None:
            self._verdict(access, UNKNOWN, "index base is not a name")
            return
        index = self.affine(access.index)
        if index is None:
            self._verdict(access, UNKNOWN, "index is not affine")
            return

        length = self._length_of(access)
        depth = self._hoist_depth(index)

        # Enumerate the loop directions that are actually possible. Each combination
        # carries its own path condition, which often makes the combination unreachable.
        combos = self._direction_combos(depth)
        if combos is None:
            self._verdict(access, UNKNOWN, "loop bound is not affine")
            return

        per_direction: Dict[bool, List[Affine]] = {}
        reachable = 0
        refuted: List[str] = []
        for directions in combos:
            facts, interval, sign_needs = self._evaluate(directions, index, depth)
            if facts is None:
                self._verdict(access, UNKNOWN, "loop bound is not affine")
                return
            if facts.infeasible():
                continue  # this run of the loop cannot happen
            reachable += 1
            low, high = interval
            # A sign assumption made while extremising is an obligation like any other:
            # the guard has to establish it before the check-free copy may run.
            residual: List[Affine] = [f for f in sign_needs if not facts.implies(f)]
            broken = None
            for goal, why in ((low, "below zero"),
                              (length - high - Affine.of_const(1), "past the end")):
                if facts.implies(goal):
                    continue
                if facts.implies((-goal) - Affine.of_const(1)):
                    # Not merely unproven: on this run the index is guaranteed out of
                    # range. If every reachable run says so the program is wrong and
                    # this is a compile error. If only some do, the others are legal,
                    # and the guard's job is to refuse that run at the loop header.
                    broken = why
                    break
                residual.append(goal)
            key = directions[-1] if directions else True
            if broken is not None:
                refuted.append(broken)
                per_direction.setdefault(key, [])
                contradiction = Affine.of_const(-1)   # never satisfiable
                if not any(_same_affine(contradiction, g) for g in per_direction[key]):
                    per_direction[key].append(contradiction)
                continue
            if residual:
                per_direction.setdefault(key, [])
                for form in residual:
                    if not any(_same_affine(form, g) for g in per_direction[key]):
                        per_direction[key].append(form)

        if reachable and len(refuted) == reachable:
            self._verdict(access, REFUTED, f"index is {refuted[0]}")
            self.errors.append((f"index is {refuted[0]}", access))
            return

        if not reachable or not per_direction:
            self._verdict(access, PROVEN)
            return

        loop = self._hoist_target(per_direction, depth, conditional)
        if loop is None:
            self._verdict(access, UNKNOWN, "obligation is not loop-invariant")
            return

        self._verdict(access, HOIST, loop=loop)
        guards = self.loop_guards.setdefault(
            id(loop), LoopGuards(loop=loop)
        )
        for ascending, forms in per_direction.items():
            bucket = guards.ascending if ascending else guards.descending
            for form in forms:
                if not any(_same_affine(form, g) for g in bucket):
                    bucket.append(form)
        settled = self._settled_direction(self._frames[depth - 1]) if depth else None
        guards.direction_known = settled

    def _verdict(self, access, kind, detail="", loop=None) -> None:
        self.verdicts[id(access)] = Verdict(kind, loop=loop, detail=detail)

    def _hoist_depth(self, index: Affine) -> int:
        """How many enclosing loops the index actually depends on, outermost-counted."""
        depth = 0
        for i, frame in enumerate(self._frames):
            if index.mentions(Sym(f"v:{frame.var}")):
                depth = i + 1
        return max(depth, 0)

    def _settled_direction(self, frame: _LoopFrame) -> Optional[bool]:
        if frame.start is None or frame.end is None or not frame.step_is_one:
            return None
        base = self._base_facts()
        if base.implies(frame.end - frame.start):          # end >= start
            return True
        if base.implies(frame.start - frame.end - Affine.of_const(1)):  # start > end
            return False
        return None

    def _direction_combos(self, depth: int) -> Optional[List[Tuple[bool, ...]]]:
        combos: List[Tuple[bool, ...]] = [()]
        for frame in self._frames[:depth]:
            if frame.start is None or frame.end is None or not frame.step_is_one:
                return None
            settled = self._settled_direction(frame)
            options = (True, False) if settled is None else (settled,)
            combos = [c + (opt,) for c in combos for opt in options]
        return combos

    def _evaluate(self, directions: Tuple[bool, ...], index: Affine, depth: int):
        """Path facts, the index interval, and any sign assumptions the substitution made."""
        facts = self._base_facts()
        extra: List[Affine] = []
        low = high = index
        for i in range(depth - 1, -1, -1):
            frame = self._frames[i]
            ascending = directions[i]
            start, end = frame.start, frame.end
            if start is None or end is None:
                return None, None, []
            one = Affine.of_const(1)
            if ascending:
                facts = facts.plus(end - start)                 # end >= start
                lo_bound, hi_bound = start, end - one
            else:
                facts = facts.plus(start - end - one)           # start > end
                lo_bound, hi_bound = end + one, start
            sym = Sym(f"v:{frame.var}")
            low, low_needs = _substitute(low, sym, lo_bound, hi_bound, minimising=True)
            high, high_needs = _substitute(high, sym, lo_bound, hi_bound, minimising=False)
            if low is None or high is None:
                return None, None, []
            extra.extend(low_needs)
            extra.extend(high_needs)
        return facts, (low, high), extra

    def _hoist_target(self, per_direction, depth: int, conditional: bool):
        """Outermost loop the obligation can be lifted to, or None.

        The access may sit under a branch, and the loop may exit early. Neither
        disqualifies it, because the guard does not decide whether to abort: it decides
        which of two copies of the loop to run. An obligation that is stronger than the
        program needs sends control to the copy that still checks, which is exactly the
        behaviour there is today.

        What does still matter is that the guard can be evaluated at the loop header, so
        every symbol it mentions must be stable across the loop.
        """
        if not self._frames:
            return None
        forms = [f for forms in per_direction.values() for f in forms]
        target = None
        for i in range(len(self._frames) - 1, -1, -1):
            frame = self._frames[i]
            if i < depth:
                # The obligation was derived using this loop's own bounds; lifting past
                # it would test something the loop header has not established yet.
                if i == depth - 1:
                    target = frame.stmt
                break
            if any(f.mentions(Sym(f"v:{frame.var}")) for f in forms):
                break
            if any(_mentions_any_name(f, frame.assigned | {frame.var}) for f in forms):
                break
            target = frame.stmt
        return target



_INTEGER_TYPES = {
    "i8", "i16", "i32", "i64", "i128",
    "u8", "u16", "u32", "u64", "u128",
    "int", "usize", "isize",
}


def _is_integer_decl(decl) -> bool:
    """Whether a declaration binds an integer, so its value may enter an index."""
    declared = getattr(decl, "type", None)
    name = getattr(declared, "name", None)
    if name is None:
        return True  # untyped `let`: the initialiser decides, and non-integers fail later
    return name in _INTEGER_TYPES


def _substitute(form: Affine, sym: Sym, lo: Affine, hi: Affine, minimising: bool):
    """Replace `sym` by the end of its range that extremises `form`.

    A monomial carrying `sym` contributes `coeff * rest * sym`, and which end extremises
    it depends on the sign of `coeff * rest`. When `rest` is empty the sign is known and
    the choice is made here. When it is not, the choice is made by assuming the product is
    non-negative and handing back that assumption as an obligation, which the guard then
    has to establish before the check-free copy of the loop runs.

    Returns (form, obligations), or (None, []) when `sym` appears squared and the domain
    has nothing useful to say.
    """
    obligations: List[Affine] = []
    if not form.mentions(sym):
        return form, obligations
    if form.degree_of(sym) > 1:
        return None, obligations

    result = Affine(form.const, {m: c for m, c in form.terms.items() if sym not in m})
    for monomial, coeff in form.terms.items():
        if sym not in monomial:
            continue
        rest = list(monomial)
        rest.remove(sym)
        rest_tuple = tuple(rest)
        factor = (Affine.of_const(coeff) if not rest_tuple
                  else Affine(0, {rest_tuple: coeff}))
        if factor.is_const():
            positive = factor.const > 0
        else:
            positive = True
            obligations.append(factor)   # the guard must show this product is >= 0
        if minimising:
            pick = lo if positive else hi
        else:
            pick = hi if positive else lo
        result = result + factor.mul(pick)
    return result, obligations


def _same_affine(a: Affine, b: Affine) -> bool:
    return a.const == b.const and a.terms == b.terms


def _mentions_any_name(form: Affine, names: set) -> bool:
    for monomial in form.terms:
        for sym in monomial:
            head = sym.key.split(".")[0]
            if head.startswith("v:") and head[2:] in names:
                return True
    return False
