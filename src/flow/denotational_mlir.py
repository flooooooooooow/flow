"""Denotational MLIR emitter for Flow evolution blocks (first slice).

A `flow` block denotes a first-order system dx/dt = f(x, u, p). The shipped
path desugars it to plain functions (see src/flow/flow_blocks.py), which erases
that structure before MLIR sees it. This module emits a `flow.*` dialect that
keeps the structure, so a later pass can fuse and vectorize an ensemble of
instances. See docs/design/denotational-mlir.md for the plan.

This first slice is a textual emitter over a parsed `FlowDecl`. It produces the
`flow.system` skeleton with `flow.state`/`flow.param` members and one
`flow.evolve` region per state. Derivative expressions are lowered for the
arithmetic, unary and known-math-call subset; anything else is preserved as a
`flow.opaque` op carrying the source text, so the emitter never silently loses
meaning. It does not yet wire into mlir_generator.py.
"""

from __future__ import annotations

from typing import Any, List, Optional

from .parser import (
    Lexer,
    Parser,
    FlowDecl,
    BinaryOperation,
    UnaryOperation,
    Variable,
    Literal,
    FunctionCall,
)

# Binary operators with a direct floating-point MLIR op.
_BINOP = {
    "+": "arith.addf",
    "-": "arith.subf",
    "*": "arith.mulf",
    "/": "arith.divf",
}

# Math calls with a direct `math` dialect op.
_MATH1 = {
    "sin": "math.sin",
    "cos": "math.cos",
    "tan": "math.tan",
    "exp": "math.exp",
    "log": "math.log",
    "sqrt": "math.sqrt",
    "fabs": "math.absf",
    "abs": "math.absf",
}


def raw_flow_decls(code: str) -> List[FlowDecl]:
    """Parse `code` without expanding flow blocks and return the FlowDecls."""
    decls = Parser(Lexer(code)).parse(expand_flows=False)
    return [d for d in decls if isinstance(d, FlowDecl)]


class _Region:
    """One `flow.evolve` region: SSA numbering plus emitted body lines.

    `elem_type` is the MLIR element type the derivative arithmetic runs on. It
    is `f64` for a single system, and `vector<Nxf64>` for a fused ensemble step,
    where the same arithmetic evaluates N instances at once.
    """

    def __init__(self, members: set, elem_type: str = "f64"):
        self._members = members
        self._ty = elem_type
        self._n = 0
        self.lines: List[str] = []

    def _fresh(self) -> str:
        name = f"%d{self._n}"
        self._n += 1
        return name

    def lower(self, expr: Any) -> str:
        """Lower a derivative expression to an SSA value, returning its name."""
        if isinstance(expr, Variable):
            # A reference to a state, input or param is the member SSA value.
            if expr.name in self._members:
                return f"%{expr.name}"
            # An unknown free name is kept opaque rather than guessed.
            return self._opaque(expr.name)
        if isinstance(expr, Literal):
            out = self._fresh()
            self.lines.append(
                f"{out} = arith.constant {expr.value} : {self._ty}"
            )
            return out
        if isinstance(expr, UnaryOperation) and expr.operator == "-":
            operand = self.lower(expr.operand)
            out = self._fresh()
            self.lines.append(f"{out} = arith.negf {operand} : {self._ty}")
            return out
        if isinstance(expr, BinaryOperation) and expr.operator in _BINOP:
            left = self.lower(expr.left)
            right = self.lower(expr.right)
            out = self._fresh()
            self.lines.append(
                f"{out} = {_BINOP[expr.operator]} {left}, {right} : {self._ty}"
            )
            return out
        if isinstance(expr, FunctionCall) and expr.name in _MATH1 and len(expr.arguments) == 1:
            arg = self.lower(expr.arguments[0])
            out = self._fresh()
            self.lines.append(f"{out} = {_MATH1[expr.name]} {arg} : {self._ty}")
            return out
        # The lowered subset ends here. Everything else is preserved as an
        # opaque op carrying its source, so meaning is never silently lost.
        return self._opaque(_render_source(expr))

    def _opaque(self, text: str) -> str:
        out = self._fresh()
        escaped = text.replace('"', '\\"')
        self.lines.append(
            f'{out} = flow.opaque {{source = "{escaped}"}} : {self._ty}'
        )
        return out


def _render_source(expr: Any) -> str:
    """A compact source rendering of an unlowered expression, for flow.opaque."""
    if isinstance(expr, Variable):
        return expr.name
    if isinstance(expr, Literal):
        return str(expr.value)
    if isinstance(expr, UnaryOperation):
        return f"{expr.operator}{_render_source(expr.operand)}"
    if isinstance(expr, BinaryOperation):
        return f"({_render_source(expr.left)} {expr.operator} {_render_source(expr.right)})"
    if isinstance(expr, FunctionCall):
        args = ", ".join(_render_source(a) for a in expr.arguments)
        return f"{expr.name}({args})"
    return type(expr).__name__


def _init_text(decl: Any) -> Optional[str]:
    init = getattr(decl, "initializer", None)
    if isinstance(init, Literal):
        return str(init.value)
    if init is None:
        return None
    return _render_source(init)


def emit_denotational_mlir(flow: FlowDecl) -> str:
    """Emit the `flow.system` denotational dialect for one flow block."""
    members = set()
    for group in (flow.states, flow.inputs, flow.outputs, flow.params):
        for m in group:
            members.add(m.name)

    lines: List[str] = [f"flow.system @{flow.name} {{"]

    for st in flow.states:
        init = _init_text(st)
        attr = f" {{init = {init}}}" if init is not None else ""
        lines.append(f'  %{st.name} = flow.state "{st.name}" : f64{attr}')
    for p in flow.params:
        init = _init_text(p)
        attr = f" {{init = {init}}}" if init is not None else ""
        lines.append(f'  %{p.name} = flow.param "{p.name}" : f64{attr}')
    for i in flow.inputs:
        lines.append(f'  %{i.name} = flow.input "{i.name}" : f64')

    for ev in flow.evolves:
        region = _Region(members)
        value = region.lower(ev.expr)
        lines.append(f"  flow.evolve %{ev.target} {{")
        for body_line in region.lines:
            lines.append(f"    {body_line}")
        lines.append(f"    flow.deriv {value} : f64")
        lines.append("  }")

    for period in flow.everys:
        lines.append(f"  flow.every {period.period_ns} {{")
        _emit_becomes_body(period.body, members, lines, indent="    ")
        lines.append("  }")

    for when in flow.whens:
        guard = _Region(members)
        threshold = guard.lower(when.threshold)
        lines.append(f"  flow.when %{when.guard_target} reaches {{")
        for body_line in guard.lines:
            lines.append(f"    {body_line}")
        lines.append(f"    flow.threshold {threshold} : f64")
        lines.append("  } do {")
        _emit_becomes_body(when.body, members, lines, indent="    ")
        lines.append("  }")

    # Anything still outside this emitter (always/never invariants, solver,
    # connections, child systems) is flagged so partial output is never taken
    # for the whole system.
    pending = {
        "always": len(getattr(flow, "alwayses", []) or []),
        "never": len(getattr(flow, "nevers", []) or []),
        "connect": len(getattr(flow, "connections", []) or []),
        "child": len(getattr(flow, "children", []) or []),
    }
    pending = {k: v for k, v in pending.items() if v}
    if pending:
        fields = ", ".join(f"{k} = {v}" for k, v in pending.items())
        lines.append(f"  flow.pending {{{fields}}}")

    lines.append("}")
    return "\n".join(lines)


def emit_ensemble_step(flow: FlowDecl, n: int) -> str:
    """Emit a fused, vectorized single step for `n` instances of `flow`.

    This is the payoff of keeping the vector field visible. Each state and param
    becomes a `vector<Nxf64>`, and every `flow.evolve` body evaluates all N
    instances with one set of `arith`/`math` ops, so N systems step in a single
    kernel. The desugared `_derivs` function cannot be fused this way because
    MLIR sees it as an opaque call.

    Only the continuous vector field is fused here. Per-instance discrete resets
    (`every`/`when`) are data-dependent and stay flagged with `flow.pending`;
    they lower on the scalar path.
    """
    if n < 1:
        raise ValueError("ensemble size must be at least 1")
    vec = f"vector<{n}xf64>"
    members = set()
    for group in (flow.states, flow.inputs, flow.outputs, flow.params):
        for m in group:
            members.add(m.name)

    lines: List[str] = [f"flow.ensemble @{flow.name} x {n} {{"]
    for st in flow.states:
        lines.append(f'  %{st.name} = flow.ensemble_state "{st.name}" : {vec}')
    for p in flow.params:
        lines.append(f'  %{p.name} = flow.ensemble_param "{p.name}" : {vec}')

    lines.append("  flow.step %dt {")
    for ev in flow.evolves:
        region = _Region(members, elem_type=vec)
        value = region.lower(ev.expr)
        lines.append(f"    flow.evolve %{ev.target} {{")
        for body_line in region.lines:
            lines.append(f"      {body_line}")
        lines.append(f"      flow.deriv {value} : {vec}")
        lines.append("    }")

    n_every = len(getattr(flow, "everys", []) or [])
    n_when = len(getattr(flow, "whens", []) or [])
    if n_every or n_when:
        lines.append(f"    flow.pending {{every = {n_every}, when = {n_when}}}")
    lines.append("  }")
    lines.append("}")
    return "\n".join(lines)


def _emit_becomes_body(body: List[Any], members: set, lines: List[str], indent: str) -> None:
    """Emit `flow.becomes %x = <region>` ops for a set of reset statements."""
    for stmt in body:
        target = getattr(stmt, "target", None)
        expr = getattr(stmt, "expr", None)
        if target is None or expr is None:
            continue
        region = _Region(members)
        value = region.lower(expr)
        lines.append(f"{indent}flow.becomes %{target} {{")
        for body_line in region.lines:
            lines.append(f"{indent}  {body_line}")
        lines.append(f"{indent}  flow.value {value} : f64")
        lines.append(f"{indent}}}")
