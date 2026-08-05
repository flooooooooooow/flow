"""Lowering for `flow Name { ... }` blocks.

Spec: docs/vision/north-star.md sections 1 and 2 (card: evolves-syntax).

A flow block parses to a real FlowDecl AST node (src/flow/parser.py). This
pass validates the dynamics sections and lowers each FlowDecl into ordinary
Flow AST that the type checker and every backend already understand:

    typedef struct Name { states..., inputs..., outputs..., params... }

    Name    Name_new()                       construct with declared defaults
    void    Name_init(Name* self)            (re)apply declared defaults
    void    Name_derivs(Name* self, ...)     dx/dt out-params, pre-step state
    void    Name_step(Name* self, double dt) Euler or RK4, events, outputs
    void    Name_outputs(Name* self)         inline output maps (if any)

Integration semantics (spec 2.2, 2.4): all `evolves` right-hand sides are
evaluated against the pre-step state (simultaneous derivative evaluation),
then every state advances together. Name_derivs is generated as a separate
function so `method rk4` is a pure codegen swap inside Name_step without
touching the surface syntax or the Name_step signature. dt is caller-supplied,
in seconds.

Time blocks (spec section 4, card: time-blocks): each
`every <duration> { ... }` block lowers to a hidden `__every_k_acc : i64`
struct field holding accumulated integrated time in nanoseconds. Inside
Name_step, after integration and before events, dt converts to integer
nanoseconds once, each accumulator advances by it, and a catch-up loop
fires the block body once per elapsed period (so dt > period does not
drop ticks), bounded at 1024 firings per step. Body `becomes` updates
stage synchronously exactly like `when` resets. A `solver { dt .. }`
block lowers to Name_default_dt() returning the default fixed step in
seconds; Name_step keeps its caller-supplied dt.

Hybrid events (spec section 5, card: hybrid-events): each
`when x reaches L { ... }` lowers to a hidden `__guard_k_prev : f64` struct
field holding the previous end-of-step value of g = x - L. Inside Name_step,
after integration and before outputs, each event in declaration order
computes g from the post-step state and fires when its sign differs from the
stored previous sign (or g is exactly zero). A fired body applies its
`becomes` resets synchronously: every right-hand side is evaluated from the
same post-step, pre-reset state, then all targets are assigned together.
Detection is at step granularity; root-finding refinement is a later card.

Constraints (spec section 5.4, card: constraints): each `always` /
`never` clause lowers into Name_check, which returns 0 or the 1-based
index of the first violated clause. Name_step calls Name_check after
events and outputs (normative order of spec 1.4) and on violation calls
flow_panic → abort(). --lenient demotion to a one-shot stderr warning is
recorded in the north-star; flow lowering runs at parse time before the
transpiler flag is known, so v1 always traps (same hard-error convention
as other flow_blocks validation).

The generated functions carry the "flow_api" attribute, which keeps their C
names unmangled (src/flow/overload.py, src/flow/c_generator.py), so
`Name_step(Name* self, double dt)` is a stable C embedding API. Because the
lowered output is ordinary AST, the strict type checker checks every
generated body the same way it checks user code.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from .parser import (
    ArrayAccess,
    ArrayLiteral,
    Assignment,
    BinaryOperation,
    Block,
    CastExpression,
    EffectCall,
    FieldAccess,
    FlowDecl,
    FlowSyntaxError,
    FunctionCall,
    FunctionDecl,
    IfStatement,
    Lambda,
    Literal,
    MethodCall,
    Parameter,
    ReturnStatement,
    StructDecl,
    StructLiteral,
    TryExpr,
    Type,
    UnaryOperation,
    VarDecl,
    Variable,
    VectorLiteral,
    WhileStatement,
)

# Numeric types a flow member may have in this card's scope.
_MEMBER_TYPES = ("f64", "f32")

# C math functions treated as pure (mirrors c_generator.c_math_functions).
_PURE_MATH_FUNCTIONS = {
    "sin", "cos", "tan", "asin", "acos", "atan", "atan2",
    "sinh", "cosh", "tanh", "asinh", "acosh", "atanh",
    "sqrt", "cbrt", "pow", "exp", "exp2", "log", "log2", "log10",
    "fabs", "abs", "floor", "ceil", "round", "fmod",
    "fmin", "fmax", "hypot",
}

_GENERATED_SUFFIXES = (
    "_new", "_init", "_derivs", "_step", "_outputs", "_check", "_default_dt",
)

# Catch-up bound for `every` blocks: at most this many firings per step
# (spec 4.3). The accumulator keeps any remainder, so ticks beyond the cap
# are delayed to later steps rather than dropped; the trap the spec sketches
# arrives with the constraints card's flow_panic machinery.
_EVERY_CATCHUP_CAP = 1024

# Default fixed step for simulation drivers when no solver block exists
# (spec 2.3): 1 ms, in nanoseconds.
_DEFAULT_DT_NS = 1_000_000

_SOLVER_METHODS = ("euler", "rk4")


def expand_flow_decls(declarations: List[Any], source: str = "") -> List[Any]:
    """Replace every FlowDecl with its synthesized struct and functions.

    Raises FlowSyntaxError on semantic errors in the flow's dynamics
    sections (unknown evolves target, missing initializer, impure
    right-hand side, ...).
    """
    flow_decls = [d for d in declarations if isinstance(d, FlowDecl)]
    if not flow_decls:
        return declarations

    flow_by_name: Dict[str, FlowDecl] = {}
    for d in flow_decls:
        if d.name in flow_by_name:
            line = (d.location.line + 1) if d.location else None
            raise _error(
                f"flow '{d.name}' is declared twice",
                line, source,
            )
        flow_by_name[d.name] = d

    local_pure_functions = {
        d.name
        for d in declarations
        if isinstance(d, FunctionDecl) and not getattr(d, "is_extern", False)
    }
    taken_names = {
        getattr(d, "name", None)
        for d in declarations
        if not isinstance(d, FlowDecl)
    }

    result: List[Any] = []
    for decl in declarations:
        if isinstance(decl, FlowDecl):
            _validate_flow(
                decl, local_pure_functions, taken_names, source, flow_by_name
            )
            result.extend(_lower_flow(decl, flow_by_name))
        else:
            result.append(decl)
    return result


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _error(message: str, line: Optional[int], source: str, suggestion: str = None):
    return FlowSyntaxError(message, line=line or None, source=source or None,
                           suggestion=suggestion)


def _validate_flow(
    flow: FlowDecl,
    local_pure_functions: Set[str],
    taken_names: Set[str],
    source: str,
    flow_by_name: Optional[Dict[str, FlowDecl]] = None,
) -> None:
    flow_line = (flow.location.line + 1) if flow.location else None
    children = list(getattr(flow, "children", None) or [])
    connections = list(getattr(flow, "connections", None) or [])
    if flow_by_name is None:
        flow_by_name = {flow.name: flow}

    if not flow.states and not children:
        raise _error(
            f"flow '{flow.name}' declares no state",
            flow_line, source,
            suggestion=(
                "add at least one 'state name : f64 = value' declaration, "
                "or nest child flows ('plant : Motor') for a composite"
            ),
        )

    for suffix in _GENERATED_SUFFIXES:
        generated = f"{flow.name}{suffix}"
        if generated in taken_names:
            raise _error(
                f"name '{generated}' is reserved by flow '{flow.name}' "
                f"(the compiler generates it)",
                flow_line, source,
            )

    members = {}
    sections = (
        [(s, "state") for s in flow.states]
        + [(i, "input") for i in flow.inputs]
        + [(o, "output") for o in flow.outputs]
        + [(p, "param") for p in flow.params]
    )
    for member, kind in sections:
        if member.name in members:
            raise _error(
                f"flow '{flow.name}' declares '{member.name}' twice",
                member.line, source,
            )
        if member.name.startswith("__"):
            raise _error(
                f"flow member '{member.name}' may not start with '__' "
                f"(reserved for compiler-generated fields)",
                member.line, source,
            )
        if member.type.name not in _MEMBER_TYPES:
            raise _error(
                f"{kind} '{member.name}' in flow '{flow.name}' has type "
                f"'{member.type.name}'; flow members must be f64 or f32 in "
                f"this version",
                member.line, source,
            )
        members[member.name] = kind

    for child in children:
        if child.name in members:
            raise _error(
                f"flow '{flow.name}' declares '{child.name}' twice",
                child.line, source,
            )
        if child.name.startswith("__"):
            raise _error(
                f"flow member '{child.name}' may not start with '__' "
                f"(reserved for compiler-generated fields)",
                child.line, source,
            )
        if child.type.name == flow.name:
            raise _error(
                f"nested flow member '{child.name}' in flow '{flow.name}' "
                f"cannot have the parent type (no recursive nesting)",
                child.line, source,
            )
        if child.type.name not in flow_by_name:
            raise _error(
                f"nested flow member '{child.name}' in flow '{flow.name}' "
                f"has type '{child.type.name}', which is not a flow in "
                f"this file",
                child.line, source,
                suggestion="declare the child with 'flow ChildName { ... }' first",
            )
        members[child.name] = "child"

    for state in flow.states:
        if state.initializer is None:
            raise _error(
                f"state '{state.name}' in flow '{flow.name}' needs an "
                f"initial value",
                state.line, source,
                suggestion=f"write 'state {state.name} : {state.type.name} = 0.0'",
            )
    for param in flow.params:
        if param.initializer is None:
            raise _error(
                f"param '{param.name}' in flow '{flow.name}' needs a "
                f"default value",
                param.line, source,
                suggestion=f"write 'param {param.name} : {param.type.name} = 1.0'",
            )
    for output in flow.outputs:
        if output.expr is None:
            raise _error(
                f"output '{output.name}' in flow '{flow.name}' needs an "
                f"inline map ('output {output.name} : {output.type.name} = expr'); "
                f"assigning outputs from 'every'/'when' blocks is a later card",
                output.line, source,
            )

    state_names = {s.name for s in flow.states}
    seen_targets = set()
    for ev in flow.evolves:
        if ev.target not in state_names:
            raise _error(
                f"'{ev.target} evolves as' in flow '{flow.name}' requires "
                f"'{ev.target}' to be a declared state",
                ev.line, source,
                suggestion=f"declare 'state {ev.target} : f64 = 0.0' or fix the name",
            )
        if ev.target in seen_targets:
            raise _error(
                f"state '{ev.target}' in flow '{flow.name}' has two "
                f"'evolves' declarations; a state has exactly one derivative",
                ev.line, source,
            )
        seen_targets.add(ev.target)
        _check_pure(ev.expr, flow, f"'{ev.target} evolves as'", ev.line,
                    local_pure_functions, source)

    param_names = {p.name for p in flow.params}
    for when in flow.whens:
        if when.guard_target not in state_names:
            raise _error(
                f"'when {when.guard_target} reaches' in flow '{flow.name}' "
                f"requires '{when.guard_target}' to be a declared state",
                when.line, source,
                suggestion=(
                    f"declare 'state {when.guard_target} : f64 = 0.0' "
                    f"or fix the name"
                ),
            )
        if when.guard_target not in seen_targets:
            raise _error(
                f"'when {when.guard_target} reaches' in flow '{flow.name}' "
                f"requires '{when.guard_target}' to be a continuous state",
                when.line, source,
                suggestion=(
                    f"give '{when.guard_target}' an "
                    f"'{when.guard_target} evolves as ...' declaration"
                ),
            )
        _check_threshold(when.threshold, flow, when, param_names, source)
        seen_resets = set()
        for reset in when.body:
            if reset.target not in state_names:
                raise _error(
                    f"'{reset.target} becomes' in the "
                    f"'when {when.guard_target} reaches' body of flow "
                    f"'{flow.name}' requires '{reset.target}' to be a "
                    f"declared state",
                    reset.line, source,
                )
            if reset.target in seen_resets:
                raise _error(
                    f"state '{reset.target}' has two 'becomes' resets in one "
                    f"'when' body of flow '{flow.name}'; resets in an event "
                    f"apply simultaneously, so each state has one writer",
                    reset.line, source,
                )
            seen_resets.add(reset.target)
            _check_pure(reset.expr, flow, f"'{reset.target} becomes'",
                        reset.line, local_pure_functions, source)

    if flow.solver is not None:
        if flow.solver.dt_ns <= 0:
            raise _error(
                f"solver dt of flow '{flow.name}' must be positive, "
                f"got '{flow.solver.dt_text}'",
                flow.solver.line, source,
            )
        if flow.solver.method not in _SOLVER_METHODS:
            raise _error(
                f"unknown solver method '{flow.solver.method}' in flow "
                f"'{flow.name}'; valid methods: "
                f"{', '.join(_SOLVER_METHODS)}",
                flow.solver.line, source,
            )

    for every in flow.everys:
        if every.period_ns <= 0:
            raise _error(
                f"'every {every.period_text}' in flow '{flow.name}' has a "
                f"zero period; the period must be positive",
                every.line, source,
            )
        seen_updates = set()
        for upd in every.body:
            if upd.target not in state_names:
                raise _error(
                    f"'{upd.target} becomes' in the "
                    f"'every {every.period_text}' body of flow "
                    f"'{flow.name}' requires '{upd.target}' to be a "
                    f"declared state",
                    upd.line, source,
                )
            if upd.target in seen_targets:
                raise _error(
                    f"state '{upd.target}' in flow '{flow.name}' has both "
                    f"an 'evolves' declaration and a 'becomes' update in "
                    f"an 'every' block; a state is continuous or discrete",
                    upd.line, source,
                    suggestion=(
                        f"reset '{upd.target}' from a "
                        f"'when {upd.target} reaches ...' event, or drop "
                        f"its 'evolves' declaration"
                    ),
                )
            if upd.target in seen_updates:
                raise _error(
                    f"state '{upd.target}' has two 'becomes' updates in "
                    f"one 'every' body of flow '{flow.name}'; updates in a "
                    f"block apply simultaneously, so each state has one "
                    f"writer",
                    upd.line, source,
                )
            seen_updates.add(upd.target)
            _check_pure(upd.expr, flow, f"'{upd.target} becomes'",
                        upd.line, local_pure_functions, source)

    for always in flow.alwayses:
        for clause in always.clauses:
            _check_pure(clause.expr, flow, "'always' clause",
                        clause.line, local_pure_functions, source)
            _check_booleanish(clause.expr, flow, "always", clause.line, source)
    for never in flow.nevers:
        for clause in never.clauses:
            _check_pure(clause.expr, flow, "'never' clause",
                        clause.line, local_pure_functions, source)
            _check_booleanish(clause.expr, flow, "never", clause.line, source)

    for state in flow.states:
        _check_pure(state.initializer, flow, f"initializer of '{state.name}'",
                    state.line, local_pure_functions, source)
    for param in flow.params:
        _check_pure(param.initializer, flow, f"initializer of '{param.name}'",
                    param.line, local_pure_functions, source)
    for output in flow.outputs:
        _check_pure(output.expr, flow, f"output map of '{output.name}'",
                    output.line, local_pure_functions, source)

    if connections or children:
        _validate_connect(flow, children, connections, flow_by_name, source)


def _validate_connect(
    flow: FlowDecl,
    children: List[Any],
    connections: List[Any],
    flow_by_name: Dict[str, FlowDecl],
    source: str,
) -> None:
    """Port direction/type checks and algebraic-loop detection (spec §8.2).

    Stage-1: unconnected child inputs are legal (embedder-driven before
    Name_step). Parent re-export of child inputs and parent `becomes` into
    `child.input` are NOT YET.
    """
    child_by_name = {c.name: c for c in children}
    if connections and not children:
        line = connections[0].line
        raise _error(
            f"'connect' in flow '{flow.name}' needs nested flow members "
            f"to wire (e.g. 'plant : Motor')",
            line, source,
        )

    driven: Dict[Tuple[str, str], Any] = {}
    for conn in connections:
        if conn.src_member not in child_by_name:
            raise _error(
                f"connection source '{conn.src_member}.{conn.src_port}' in "
                f"flow '{flow.name}' names unknown nested member "
                f"'{conn.src_member}'",
                conn.line, source,
            )
        if conn.dst_member not in child_by_name:
            raise _error(
                f"connection destination '{conn.dst_member}.{conn.dst_port}' "
                f"in flow '{flow.name}' names unknown nested member "
                f"'{conn.dst_member}'",
                conn.line, source,
            )
        if conn.src_member == conn.dst_member:
            raise _error(
                f"connection in flow '{flow.name}' wires "
                f"'{conn.src_member}' to itself; Stage-1 connect is "
                f"between sibling subflows only",
                conn.line, source,
            )
        src_flow = flow_by_name[child_by_name[conn.src_member].type.name]
        dst_flow = flow_by_name[child_by_name[conn.dst_member].type.name]
        src_kind, src_type = _lookup_port(src_flow, conn.src_port)
        if src_kind is None:
            raise _error(
                f"'{conn.src_member}.{conn.src_port}' in flow '{flow.name}' "
                f"is not a port of '{src_flow.name}'",
                conn.line, source,
                suggestion=(
                    f"connect sources must be an output or state of "
                    f"'{src_flow.name}'"
                ),
            )
        if src_kind not in ("output", "state"):
            raise _error(
                f"'{conn.src_member}.{conn.src_port}' in flow '{flow.name}' "
                f"is a {src_kind}; connection sources must be an output "
                f"or state",
                conn.line, source,
            )
        dst_kind, dst_type = _lookup_port(dst_flow, conn.dst_port)
        if dst_kind is None:
            raise _error(
                f"'{conn.dst_member}.{conn.dst_port}' in flow '{flow.name}' "
                f"is not a port of '{dst_flow.name}'",
                conn.line, source,
                suggestion=f"connection destinations must be an input of "
                           f"'{dst_flow.name}'",
            )
        if dst_kind != "input":
            raise _error(
                f"'{conn.dst_member}.{conn.dst_port}' in flow '{flow.name}' "
                f"is a {dst_kind}; connection destinations must be an input",
                conn.line, source,
            )
        if src_type.name != dst_type.name:
            raise _error(
                f"type mismatch in connect of flow '{flow.name}': "
                f"'{conn.src_member}.{conn.src_port}' is {src_type.name} but "
                f"'{conn.dst_member}.{conn.dst_port}' is {dst_type.name}",
                conn.line, source,
            )
        key = (conn.dst_member, conn.dst_port)
        if key in driven:
            raise _error(
                f"input '{conn.dst_member}.{conn.dst_port}' in flow "
                f"'{flow.name}' has two incoming connections",
                conn.line, source,
            )
        driven[key] = conn

    # Algebraic loops: edges where the source is an output computed
    # combinationally from inputs (spec §8.2). State-broken edges are fine.
    combo_edges: List[Tuple[str, str, Any]] = []
    for conn in connections:
        src_flow = flow_by_name[child_by_name[conn.src_member].type.name]
        if _port_is_combinational(src_flow, conn.src_port):
            combo_edges.append((conn.src_member, conn.dst_member, conn))
    cycle = _find_member_cycle(
        [c.name for c in children],
        [(a, b) for a, b, _ in combo_edges],
    )
    if cycle is not None:
        edge = next(
            (c for a, b, c in combo_edges
             if a in cycle and b in cycle),
            connections[0] if connections else None,
        )
        line = edge.line if edge is not None else None
        raise _error(
            f"algebraic loop in connect of flow '{flow.name}' through "
            f"combinational outputs: {' -> '.join(cycle)}",
            line, source,
            suggestion=(
                "break the loop with a state (or an output mapped from a "
                "state); Modelica-style algebraic solvers are out of scope"
            ),
        )


def _lookup_port(flow: FlowDecl, port: str):
    """Return (kind, type) for a named port on a flow, or (None, None)."""
    for s in flow.states:
        if s.name == port:
            return "state", s.type
    for i in flow.inputs:
        if i.name == port:
            return "input", i.type
    for o in flow.outputs:
        if o.name == port:
            return "output", o.type
    for p in flow.params:
        if p.name == port:
            return "param", p.type
    return None, None


def _port_is_combinational(flow: FlowDecl, port: str) -> bool:
    """True when `port` is an output whose map references an input (spec §8.2)."""
    for output in flow.outputs:
        if output.name != port:
            continue
        if output.expr is None:
            return False
        input_names = {i.name for i in flow.inputs}
        return _expr_refs_names(output.expr, input_names)
    return False


def _expr_refs_names(expr, names: Set[str]) -> bool:
    if expr is None:
        return False
    if isinstance(expr, Variable):
        return expr.name in names
    if isinstance(expr, FunctionCall):
        return any(_expr_refs_names(a, names) for a in expr.arguments)
    for child in _children(expr):
        if _expr_refs_names(child, names):
            return True
    return False


def _find_member_cycle(
    members: List[str], edges: List[Tuple[str, str]]
) -> Optional[List[str]]:
    """Return a cycle path (node list with repeated start) or None."""
    adj: Dict[str, List[str]] = {m: [] for m in members}
    for a, b in edges:
        if a in adj and b in adj:
            adj[a].append(b)
    visiting: Set[str] = set()
    visited: Set[str] = set()
    stack: List[str] = []

    def dfs(node: str) -> Optional[List[str]]:
        visiting.add(node)
        stack.append(node)
        for nxt in adj[node]:
            if nxt in visiting:
                i = stack.index(nxt)
                return stack[i:] + [nxt]
            if nxt not in visited:
                found = dfs(nxt)
                if found is not None:
                    return found
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for m in members:
        if m not in visited:
            found = dfs(m)
            if found is not None:
                return found
    return None


def _topo_child_order(
    children: List[Any],
    connections: List[Any],
    flow_by_name: Dict[str, FlowDecl],
) -> List[Any]:
    """Topological order by combinational edges; ties by declaration order.

    Spec §8.3: state-broken edges do not constrain order.
    """
    child_by_name = {c.name: c for c in children}
    names = [c.name for c in children]
    indeg = {n: 0 for n in names}
    adj: Dict[str, List[str]] = {n: [] for n in names}
    for conn in connections:
        src_flow = flow_by_name[child_by_name[conn.src_member].type.name]
        if not _port_is_combinational(src_flow, conn.src_port):
            continue
        if conn.dst_member not in indeg or conn.src_member not in adj:
            continue
        adj[conn.src_member].append(conn.dst_member)
        indeg[conn.dst_member] += 1
    # Stable Kahn: among zero-indegree nodes, pick earliest declaration.
    remaining = list(names)
    ordered: List[Any] = []
    while remaining:
        ready = [n for n in remaining if indeg[n] == 0]
        if not ready:
            # Cycle already rejected in validation; fall back to decl order.
            return list(children)
        pick = ready[0]
        remaining.remove(pick)
        ordered.append(child_by_name[pick])
        for nxt in adj[pick]:
            indeg[nxt] -= 1
    return ordered


def _check_booleanish(expr, flow, kind: str, line, source) -> None:
    """Reject clauses that clearly cannot type as bool (spec 5.4).

    Full bool typing is done by the strict checker on the lowered
    Name_check body; this catches the common mistake of a bare numeric
    expression early, with a located flow-body message.
    """
    if isinstance(expr, BinaryOperation) and expr.operator in (
        "==", "!=", "<", "<=", ">", ">=", "&&", "||", "and", "or",
    ):
        return
    if isinstance(expr, UnaryOperation) and expr.operator in ("!", "not"):
        return
    if isinstance(expr, Literal) and getattr(expr.type, "name", None) == "bool":
        return
    if isinstance(expr, Variable):
        # Member or local bool — leave to the type checker.
        return
    raise _error(
        f"'{kind}' clause in flow '{flow.name}' must be a boolean "
        f"expression",
        line, source,
        suggestion="write a comparison or logical expression, e.g. 'x < 1.0'",
    )


def _check_threshold(expr, flow, when, param_names, source) -> None:
    """Reject thresholds that can vary within a step (spec 5.1).

    v1: a threshold is built from literals and params, combined with
    arithmetic and casts. States, inputs, outputs, and calls are rejected.
    """
    if expr is None or isinstance(expr, Literal):
        return
    if isinstance(expr, Variable):
        if expr.name in param_names:
            return
        raise _error(
            f"threshold of 'when {when.guard_target} reaches' in flow "
            f"'{flow.name}' references '{expr.name}'; thresholds must be "
            f"constant over a step, built from params and literals (v1)",
            when.line, source,
        )
    if isinstance(expr, (BinaryOperation, UnaryOperation, CastExpression)):
        for child in _children(expr):
            _check_threshold(child, flow, when, param_names, source)
        return
    raise _error(
        f"threshold of 'when {when.guard_target} reaches' in flow "
        f"'{flow.name}' must be built from params and literals (v1)",
        when.line, source,
    )


def _check_pure(expr, flow, where, line, local_pure_functions, source) -> None:
    """Reject expressions the compiler cannot treat as pure (spec 2.4).

    v1 approximation: C math functions and non-extern functions defined in
    the same file are allowed; effect operations, method calls, and lambdas
    are not.
    """
    if expr is None:
        return
    if isinstance(expr, EffectCall):
        raise _error(
            f"effect call in {where} of flow '{flow.name}'; dynamics "
            f"expressions must be pure",
            line, source,
            suggestion="lift effectful work out of the flow body",
        )
    if isinstance(expr, MethodCall):
        raise _error(
            f"method call in {where} of flow '{flow.name}'; dynamics "
            f"expressions must be pure plain calls in this version",
            line, source,
        )
    if isinstance(expr, Lambda):
        raise _error(
            f"lambda in {where} of flow '{flow.name}' is not supported",
            line, source,
        )
    if isinstance(expr, FunctionCall):
        if (expr.name not in _PURE_MATH_FUNCTIONS
                and expr.name not in local_pure_functions):
            raise _error(
                f"call to '{expr.name}' in {where} of flow '{flow.name}' "
                f"cannot be proven pure; only C math functions and non-extern "
                f"functions defined in the same file are allowed here (v1)",
                line, source,
            )
        for arg in expr.arguments:
            _check_pure(arg, flow, where, line, local_pure_functions, source)
        return
    for child in _children(expr):
        _check_pure(child, flow, where, line, local_pure_functions, source)


def _children(expr) -> List[Any]:
    if isinstance(expr, BinaryOperation):
        return [expr.left, expr.right]
    if isinstance(expr, UnaryOperation):
        return [expr.operand]
    if isinstance(expr, CastExpression):
        return [expr.expr]
    if isinstance(expr, FieldAccess):
        return [expr.object]
    if isinstance(expr, ArrayAccess):
        return [expr.array, expr.index]
    if isinstance(expr, (ArrayLiteral, VectorLiteral)):
        return list(expr.elements)
    if isinstance(expr, StructLiteral):
        return [value for _, value in expr.fields]
    if isinstance(expr, TryExpr):
        return [expr.operand]
    return []


# ---------------------------------------------------------------------------
# Lowering
# ---------------------------------------------------------------------------


def _lower_flow(
    flow: FlowDecl,
    flow_by_name: Optional[Dict[str, FlowDecl]] = None,
) -> List[Any]:
    # Field order: nested flow children (spec §8), then state, input, output,
    # param (spec 1.2), then hidden per-every-block accumulators (spec 4.4)
    # and per-event guard memory (spec 5.3). User members may not start with
    # '__', so the hidden names cannot collide.
    children = list(getattr(flow, "children", None) or [])
    if flow_by_name is None:
        flow_by_name = {flow.name: flow}
    ordered = (
        [(c.name, c.type) for c in children]
        + [(s.name, s.type) for s in flow.states]
        + [(i.name, i.type) for i in flow.inputs]
        + [(o.name, o.type) for o in flow.outputs]
        + [(p.name, p.type) for p in flow.params]
        + [(f"__every_{k}_acc", Type("i64")) for k in range(len(flow.everys))]
        + [(f"__guard_{k}_prev", Type("f64")) for k in range(len(flow.whens))]
    )
    member_names = {name for name, _ in ordered}
    member_types = {name: t for name, t in ordered}

    struct = StructDecl(
        flow.name,
        [Parameter(name, t) for name, t in ordered],
        is_exported=flow.is_exported,
        location=flow.location,
    )
    struct.flow_decl = flow  # dynamics metadata for later cards and tooling

    evolved = [ev for ev in flow.evolves]
    has_outputs = bool(flow.outputs)
    clauses = _invariant_clauses(flow)

    functions = [
        _make_new(flow, ordered),
        _make_init(flow, member_names, member_types, has_outputs),
        _make_derivs(flow, member_names, member_types, evolved),
        _make_step(
            flow, member_names, member_types, evolved, has_outputs,
            clauses, flow_by_name=flow_by_name,
        ),
        _make_default_dt(flow),
    ]
    if has_outputs:
        functions.append(_make_outputs(flow, member_names))
    if clauses:
        functions.append(_make_check(flow, member_names, clauses))

    for fn in functions:
        fn.is_exported = flow.is_exported
        fn.location = flow.location

    return [struct] + functions


def _invariant_clauses(flow: FlowDecl) -> List[Tuple[str, Any]]:
    """Flatten always/never clauses in declaration order within each kind.

    always blocks are checked before never blocks (stable, matches how
    the AST stores them as separate lists). Returns (kind, clause) pairs.
    """
    clauses: List[Tuple[str, Any]] = []
    for always in getattr(flow, "alwayses", None) or []:
        for clause in always.clauses:
            clauses.append(("always", clause))
    for never in getattr(flow, "nevers", None) or []:
        for clause in never.clauses:
            clauses.append(("never", clause))
    return clauses


def _self_ptr_type(flow_name: str) -> Type:
    return Type(f"ptr_{flow_name}", is_pointer=True, element_type=Type(flow_name))


def _zero() -> Literal:
    # Float literals carry Type("f32") in this AST, exactly as the parser
    # builds them; the checker unifies them with f32 and f64 targets.
    return Literal("0.0", Type("f32"))


def _zero_of(t: Type):
    """Default value for a struct field: numeric zero, or Child_new() for
    nested flow members (spec §8)."""
    if t.name == "i64":
        return _i64(0)
    if t.name in _MEMBER_TYPES:
        return _zero()
    # Nested flow / struct field: construct via the generated Name_new API.
    return FunctionCall(f"{t.name}_new", [])


def _i64(value: int) -> Literal:
    return Literal(str(value), Type("i64"))


def _rewrite(expr, member_names: Set[str]):
    """Return expr with every member reference X replaced by self.X."""
    if expr is None:
        return None
    if isinstance(expr, Variable):
        if expr.name in member_names:
            return FieldAccess(Variable("self"), expr.name)
        return expr
    if isinstance(expr, BinaryOperation):
        return BinaryOperation(
            _rewrite(expr.left, member_names),
            expr.operator,
            _rewrite(expr.right, member_names),
        )
    if isinstance(expr, UnaryOperation):
        return UnaryOperation(expr.operator, _rewrite(expr.operand, member_names))
    if isinstance(expr, FunctionCall):
        return FunctionCall(
            expr.name, [_rewrite(a, member_names) for a in expr.arguments]
        )
    if isinstance(expr, CastExpression):
        return CastExpression(_rewrite(expr.expr, member_names), expr.target_type)
    if isinstance(expr, FieldAccess):
        return FieldAccess(_rewrite(expr.object, member_names), expr.field)
    if isinstance(expr, ArrayAccess):
        return ArrayAccess(
            _rewrite(expr.array, member_names), _rewrite(expr.index, member_names)
        )
    if isinstance(expr, (ArrayLiteral, VectorLiteral)):
        rewritten = [_rewrite(e, member_names) for e in expr.elements]
        return type(expr)(rewritten)
    if isinstance(expr, TryExpr):
        return TryExpr(_rewrite(expr.operand, member_names))
    return expr


def _assign_member(name: str, value) -> Assignment:
    return Assignment("", value, target_expr=FieldAccess(Variable("self"), name))


def _flow_fn(flow: FlowDecl, suffix: str, parameters, return_type, statements):
    return FunctionDecl(
        name=f"{flow.name}{suffix}",
        parameters=parameters,
        return_type=return_type,
        body=Block(statements),
        attributes=["flow_api"],
    )


def _make_new(flow: FlowDecl, ordered) -> FunctionDecl:
    """Name_new() -> Name: zero the struct, then apply declared defaults."""
    statements = [
        VarDecl(
            "self",
            Type(flow.name),
            StructLiteral(flow.name, [(name, _zero_of(t)) for name, t in ordered]),
            is_mutable=True,
        ),
        FunctionCall(f"{flow.name}_init", [UnaryOperation("&", Variable("self"))]),
        ReturnStatement(Variable("self")),
    ]
    return _flow_fn(flow, "_new", [], Type(flow.name), statements)


def _make_init(flow: FlowDecl, member_names: Set[str], member_types,
               has_outputs: bool) -> FunctionDecl:
    """Name_init(self): apply declared defaults in order params, inputs,
    states, then zero the every-block accumulators and seed event guard
    memory from the init state, then compute outputs. Initializers may
    reference members assigned earlier in that order (params in state
    initializers is the common case)."""
    statements = []
    for param in flow.params:
        statements.append(
            _assign_member(param.name, _rewrite(param.initializer, member_names))
        )
    for inp in flow.inputs:
        statements.append(_assign_member(inp.name, _zero()))
    for state in flow.states:
        statements.append(
            _assign_member(state.name, _rewrite(state.initializer, member_names))
        )
    for child in getattr(flow, "children", None) or []:
        # Child_new already ran inside Name_new; re-init so Name_init is a
        # full reset of the composite (matches scalar member re-init).
        statements.append(
            FunctionCall(
                f"{child.type.name}_init",
                [
                    UnaryOperation(
                        "&", FieldAccess(Variable("self"), child.name)
                    )
                ],
            )
        )
    for k in range(len(flow.everys)):
        statements.append(_assign_member(f"__every_{k}_acc", _i64(0)))
    for k, when in enumerate(flow.whens):
        statements.append(
            _assign_member(
                f"__guard_{k}_prev",
                _guard_expr(when, member_names, member_types),
            )
        )
    if has_outputs:
        statements.append(
            FunctionCall(f"{flow.name}_outputs", [Variable("self")])
        )
    return _flow_fn(
        flow, "_init",
        [Parameter("self", _self_ptr_type(flow.name))],
        Type("void"), statements,
    )


def _make_derivs(flow: FlowDecl, member_names, member_types, evolved) -> FunctionDecl:
    """Name_derivs(self, d_x, ...): every dx/dt evaluated from the same
    pre-step state (spec 2.2). One out-parameter per evolved state, in
    state declaration order."""
    parameters = [Parameter("self", _self_ptr_type(flow.name))]
    statements = []
    for ev in _in_state_order(flow, evolved):
        state_type = member_types[ev.target]
        parameters.append(
            Parameter(
                f"d_{ev.target}",
                Type(f"ptr_{state_type.name}", is_pointer=True,
                     element_type=Type(state_type.name)),
            )
        )
        statements.append(
            Assignment(
                "",
                _rewrite(ev.expr, member_names),
                target_expr=ArrayAccess(
                    Variable(f"d_{ev.target}"), Literal("0", Type("i32"))
                ),
            )
        )
    return _flow_fn(flow, "_derivs", parameters, Type("void"), statements)


def _guard_expr(when, member_names: Set[str], member_types):
    """g = self.<guard state> - threshold, widened to f64 (spec 5.3)."""
    expr = BinaryOperation(
        FieldAccess(Variable("self"), when.guard_target),
        "-",
        _rewrite(when.threshold, member_names),
    )
    if member_types[when.guard_target].name == "f32":
        expr = CastExpression(expr, Type("f64"))
    return expr


def _solver_method(flow: FlowDecl) -> str:
    """Integration method pinned by the solver block, else explicit Euler."""
    if flow.solver is not None:
        return flow.solver.method
    return "euler"


def _dt_for_state(state_type: Type):
    """Caller dt, narrowed to f32 when the evolved state is f32."""
    dt_expr = Variable("dt")
    if state_type.name == "f32":
        return CastExpression(dt_expr, Type("f32"))
    return dt_expr


def _float_lit(text: str) -> Literal:
    return Literal(text, Type("f32"))


def _derivs_call(flow: FlowDecl, ordered_evolved, stage: str) -> FunctionCall:
    return FunctionCall(
        f"{flow.name}_derivs",
        [Variable("self")]
        + [
            UnaryOperation("&", Variable(f"{stage}_{ev.target}"))
            for ev in ordered_evolved
        ],
    )


def _euler_integration(flow: FlowDecl, ordered_evolved, member_types):
    """Explicit Euler with simultaneous update (spec 2.4)."""
    statements = []
    for ev in ordered_evolved:
        state_type = member_types[ev.target]
        statements.append(
            VarDecl(f"d_{ev.target}", Type(state_type.name), _zero(),
                    is_mutable=True)
        )
    if ordered_evolved:
        statements.append(_derivs_call(flow, ordered_evolved, "d"))
    for ev in ordered_evolved:
        state_type = member_types[ev.target]
        statements.append(
            _assign_member(
                ev.target,
                BinaryOperation(
                    FieldAccess(Variable("self"), ev.target),
                    "+",
                    BinaryOperation(
                        Variable(f"d_{ev.target}"), "*",
                        _dt_for_state(state_type),
                    ),
                ),
            )
        )
    return statements


def _set_state_from_y0_plus_k(ordered_evolved, member_types, k_stage: str,
                              dt_scale):
    """self.x = y0_x + k_stage_x * dt_scale for each evolved state."""
    statements = []
    for ev in ordered_evolved:
        state_type = member_types[ev.target]
        scale = dt_scale(state_type)
        statements.append(
            _assign_member(
                ev.target,
                BinaryOperation(
                    Variable(f"y0_{ev.target}"),
                    "+",
                    BinaryOperation(Variable(f"{k_stage}_{ev.target}"),
                                    "*", scale),
                ),
            )
        )
    return statements


def _rk4_integration(flow: FlowDecl, ordered_evolved, member_types):
    """Classic RK4 via four Name_derivs calls on temporary state copies
    (spec 2.4): save y0, evaluate k1 at y0, k2 at y0+(dt/2)k1, k3 at
    y0+(dt/2)k2, k4 at y0+dt*k3, then
    y = y0 + (dt/6)(k1 + 2 k2 + 2 k3 + k4). Intermediate stages overwrite
    only evolved fields on self; params, inputs, and hidden accumulators
    are left alone.
    """
    statements = []
    for ev in ordered_evolved:
        state_type = member_types[ev.target]
        statements.append(
            VarDecl(
                f"y0_{ev.target}",
                Type(state_type.name),
                FieldAccess(Variable("self"), ev.target),
            )
        )
    for stage in ("k1", "k2", "k3", "k4"):
        for ev in ordered_evolved:
            state_type = member_types[ev.target]
            statements.append(
                VarDecl(
                    f"{stage}_{ev.target}",
                    Type(state_type.name),
                    _zero(),
                    is_mutable=True,
                )
            )

    def half_dt(state_type: Type):
        return BinaryOperation(
            _dt_for_state(state_type), "*", _float_lit("0.5")
        )

    def full_dt(state_type: Type):
        return _dt_for_state(state_type)

    def sixth_dt(state_type: Type):
        return BinaryOperation(
            _dt_for_state(state_type), "/", _float_lit("6.0")
        )

    # k1 at y0 (self still holds the pre-step state)
    statements.append(_derivs_call(flow, ordered_evolved, "k1"))
    statements.extend(
        _set_state_from_y0_plus_k(ordered_evolved, member_types, "k1", half_dt)
    )
    statements.append(_derivs_call(flow, ordered_evolved, "k2"))
    statements.extend(
        _set_state_from_y0_plus_k(ordered_evolved, member_types, "k2", half_dt)
    )
    statements.append(_derivs_call(flow, ordered_evolved, "k3"))
    statements.extend(
        _set_state_from_y0_plus_k(ordered_evolved, member_types, "k3", full_dt)
    )
    statements.append(_derivs_call(flow, ordered_evolved, "k4"))

    for ev in ordered_evolved:
        # k1 + 2*k2 + 2*k3 + k4
        weighted = BinaryOperation(
            BinaryOperation(
                BinaryOperation(
                    Variable(f"k1_{ev.target}"),
                    "+",
                    BinaryOperation(
                        Variable(f"k2_{ev.target}"), "*", _float_lit("2.0"),
                    ),
                ),
                "+",
                BinaryOperation(
                    Variable(f"k3_{ev.target}"), "*", _float_lit("2.0"),
                ),
            ),
            "+",
            Variable(f"k4_{ev.target}"),
        )
        statements.append(
            _assign_member(
                ev.target,
                BinaryOperation(
                    Variable(f"y0_{ev.target}"),
                    "+",
                    BinaryOperation(
                        weighted, "*", sixth_dt(member_types[ev.target]),
                    ),
                ),
            )
        )
    return statements


def _make_step(flow: FlowDecl, member_names, member_types, evolved,
               has_outputs, clauses=None, flow_by_name=None) -> FunctionDecl:
    """Name_step(self, dt): integrate (Euler or RK4), then every-blocks due
    this tick in declaration order, then hybrid events in declaration order,
    then output maps, then nested children (spec §8.3), then invariant
    checks (the normative ordering of spec 1.4). dt is in seconds (spec
    2.3, 2.4; every-blocks per spec 4.3 and 4.4; events per spec 5.2 and
    5.3; invariants per spec 5.4). Method comes from `solver { method … }`;
    default is Euler.

    Event firing test: strict sign comparison, (g < 0) != (g_prev < 0),
    plus the exact-hit case g == 0. The spec's section 5.3 sketch compares
    with <= and stores the pre-reset g; that combination re-fires on the
    step after a reset that lands the guard state exactly on the surface
    (the canonical clamped bounce, spec A.2), flipping the reset back.
    Strict < and recomputing the stored guard from the post-reset state
    keep the spec's step-granularity semantics and fire once per crossing.
    """
    if clauses is None:
        clauses = _invariant_clauses(flow)
    if flow_by_name is None:
        flow_by_name = {flow.name: flow}
    ordered_evolved = _in_state_order(flow, evolved)
    method = _solver_method(flow)
    if method == "rk4":
        statements = _rk4_integration(flow, ordered_evolved, member_types)
    else:
        statements = _euler_integration(flow, ordered_evolved, member_types)
    if flow.everys:
        # dt converts to integer nanoseconds once per step (spec 4.4);
        # drift is bounded by the ns truncation per step.
        statements.append(
            VarDecl(
                "__dt_ns",
                Type("i64"),
                CastExpression(
                    BinaryOperation(
                        Variable("dt"), "*",
                        Literal("1000000000.0", Type("f32")),
                    ),
                    Type("i64"),
                ),
            )
        )
    for k, every in enumerate(flow.everys):
        statements.extend(
            _every_statements(k, every, member_names, member_types)
        )
    for k, when in enumerate(flow.whens):
        statements.extend(
            _event_statements(k, when, member_names, member_types)
        )
    if has_outputs:
        statements.append(FunctionCall(f"{flow.name}_outputs", [Variable("self")]))
    statements.extend(_child_step_statements(flow, flow_by_name))
    if clauses:
        statements.extend(_check_call_statements(flow, clauses))
    return _flow_fn(
        flow, "_step",
        [Parameter("self", _self_ptr_type(flow.name)), Parameter("dt", Type("f64"))],
        Type("void"), statements,
    )


def _child_step_statements(
    flow: FlowDecl, flow_by_name: Dict[str, FlowDecl]
) -> List[Any]:
    """Copy connected ports, then Child_step, in topo order (spec §8.3)."""
    children = list(getattr(flow, "children", None) or [])
    connections = list(getattr(flow, "connections", None) or [])
    if not children:
        return []
    ordered = _topo_child_order(children, connections, flow_by_name)
    by_dst: Dict[str, List[Any]] = {c.name: [] for c in children}
    for conn in connections:
        by_dst.setdefault(conn.dst_member, []).append(conn)
    statements: List[Any] = []
    for child in ordered:
        for conn in by_dst.get(child.name, []):
            src = FieldAccess(
                FieldAccess(Variable("self"), conn.src_member),
                conn.src_port,
            )
            dst = FieldAccess(
                FieldAccess(Variable("self"), conn.dst_member),
                conn.dst_port,
            )
            statements.append(Assignment("", src, target_expr=dst))
        statements.append(
            FunctionCall(
                f"{child.type.name}_step",
                [
                    UnaryOperation(
                        "&", FieldAccess(Variable("self"), child.name)
                    ),
                    Variable("dt"),
                ],
            )
        )
    return statements


def _make_check(flow: FlowDecl, member_names: Set[str], clauses) -> FunctionDecl:
    """Name_check(self) -> i32: 0 if all invariants hold, else the 1-based
    index of the first violated clause (spec 5.4). always clauses must be
    true; never clauses must be false.
    """
    statements = []
    for idx, (kind, clause) in enumerate(clauses, start=1):
        cond = _rewrite(clause.expr, member_names)
        if kind == "always":
            violated = UnaryOperation("!", cond)
        else:
            violated = cond
        statements.append(
            IfStatement(
                violated,
                Block([ReturnStatement(Literal(str(idx), Type("i32")))]),
                [],
                None,
            )
        )
    statements.append(ReturnStatement(Literal("0", Type("i32"))))
    return _flow_fn(
        flow, "_check",
        [Parameter("self", _self_ptr_type(flow.name))],
        Type("i32"), statements,
    )


def _check_call_statements(flow: FlowDecl, clauses) -> List[Any]:
    """Statements Name_step appends after outputs to enforce invariants.

        let __viol : i32 = Name_check(self)
        if __viol == 1 { flow_panic("...") }
        if __viol == 2 { flow_panic("...") }
        ...
    """
    statements: List[Any] = [
        VarDecl(
            "__viol",
            Type("i32"),
            FunctionCall(f"{flow.name}_check", [Variable("self")]),
        )
    ]
    for idx, (_kind, clause) in enumerate(clauses, start=1):
        text = clause.text or _expr_text(clause.expr)
        msg = f"{flow.name}:{clause.line}: invariant violated: {text}"
        statements.append(
            IfStatement(
                BinaryOperation(
                    Variable("__viol"), "==", Literal(str(idx), Type("i32"))
                ),
                Block([
                    FunctionCall(
                        "flow_panic",
                        [Literal(f'"{_escape_c_string(msg)}"', Type("string"))],
                    )
                ]),
                [],
                None,
            )
        )
    return statements


def _escape_c_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _expr_text(expr) -> str:
    """Fallback pretty-print when the parser did not capture a source slice."""
    if expr is None:
        return ""
    if isinstance(expr, Literal):
        return str(expr.value)
    if isinstance(expr, Variable):
        return expr.name
    if isinstance(expr, BinaryOperation):
        return f"({_expr_text(expr.left)} {expr.operator} {_expr_text(expr.right)})"
    if isinstance(expr, UnaryOperation):
        return f"({expr.operator}{_expr_text(expr.operand)})"
    if isinstance(expr, FieldAccess):
        return f"{_expr_text(expr.object)}.{expr.field}"
    if isinstance(expr, FunctionCall):
        args = ", ".join(_expr_text(a) for a in expr.arguments)
        return f"{expr.name}({args})"
    if isinstance(expr, CastExpression):
        return f"({_expr_text(expr.expr)} as {expr.target_type.name})"
    return "..."


def _every_statements(k: int, every, member_names: Set[str], member_types):
    """Statements for one `every P { ... }` block inside Name_step
    (spec 4.3, 4.4).

        self.__every_k_acc = self.__every_k_acc + __dt_ns
        let mut __every_k_n : i64 = 0
        while self.__every_k_acc >= P && __every_k_n < 1024 {
            self.__every_k_acc = self.__every_k_acc - P
            __every_k_n = __every_k_n + 1
            let __tick_k_t : T = <rhs from pre-block state> ...
            self.t = __tick_k_t ...
        }

    The while loop is the catch-up form: dt > P fires the body once per
    elapsed period, so slow stepping does not drop ticks. The counter
    bounds a step at 1024 firings (spec 4.3); any remainder stays in the
    accumulator for later steps. First firing lands at t >= P because the
    accumulator starts at zero. Body writes stage synchronously, exactly
    like `when` resets (spec 3.2).
    """
    acc_name = f"__every_{k}_acc"
    counter = f"__every_{k}_n"
    acc = FieldAccess(Variable("self"), acc_name)
    period = _i64(every.period_ns)

    body_stmts = [
        _assign_member(acc_name, BinaryOperation(acc, "-", period)),
        Assignment(
            counter,
            BinaryOperation(Variable(counter), "+", _i64(1)),
        ),
    ]
    for upd in every.body:
        body_stmts.append(
            VarDecl(
                f"__tick_{k}_{upd.target}",
                Type(member_types[upd.target].name),
                _rewrite(upd.expr, member_names),
            )
        )
    for upd in every.body:
        body_stmts.append(
            _assign_member(upd.target, Variable(f"__tick_{k}_{upd.target}"))
        )

    due = BinaryOperation(
        BinaryOperation(acc, ">=", period),
        "&&",
        BinaryOperation(Variable(counter), "<", _i64(_EVERY_CATCHUP_CAP)),
    )
    return [
        _assign_member(acc_name, BinaryOperation(acc, "+", Variable("__dt_ns"))),
        VarDecl(counter, Type("i64"), _i64(0), is_mutable=True),
        WhileStatement(due, Block(body_stmts)),
    ]


def _make_default_dt(flow: FlowDecl) -> FunctionDecl:
    """Name_default_dt() -> f64: the default fixed step in seconds for
    simulation drivers (spec 2.3): the solver dt when a `solver` block is
    declared, else 1 ms. Emitted as a flow_api function rather than a
    #define because the lowering targets plain Flow AST shared by every
    backend. Name_step keeps its caller-supplied dt either way.
    """
    dt_ns = flow.solver.dt_ns if flow.solver is not None else _DEFAULT_DT_NS
    seconds = repr(dt_ns / 1e9)
    statements = [ReturnStatement(Literal(seconds, Type("f32")))]
    return _flow_fn(flow, "_default_dt", [], Type("f64"), statements)


def _event_statements(k: int, when, member_names: Set[str], member_types):
    """Statements for one `when x reaches L { ... }` event inside Name_step.

        let __g_k : f64 = self.x - L
        if (__g_k < 0.0) != (self.__guard_k_prev < 0.0) or __g_k == 0.0 {
            let __reset_k_t : T = <rhs from post-step, pre-reset state> ...
            self.t = __reset_k_t ...
        }
        self.__guard_k_prev = self.x - L    # post-reset value

    All reset right-hand sides are evaluated before any target is written,
    the same simultaneous semantics as `evolves as` (spec 3.2).
    """
    g_name = f"__g_{k}"
    prev = FieldAccess(Variable("self"), f"__guard_{k}_prev")
    fired = BinaryOperation(
        BinaryOperation(
            BinaryOperation(Variable(g_name), "<", _zero()),
            "!=",
            BinaryOperation(prev, "<", _zero()),
        ),
        "||",
        BinaryOperation(Variable(g_name), "==", _zero()),
    )
    reset_stmts = []
    for reset in when.body:
        reset_stmts.append(
            VarDecl(
                f"__reset_{k}_{reset.target}",
                Type(member_types[reset.target].name),
                _rewrite(reset.expr, member_names),
            )
        )
    for reset in when.body:
        reset_stmts.append(
            _assign_member(
                reset.target, Variable(f"__reset_{k}_{reset.target}")
            )
        )
    return [
        VarDecl(g_name, Type("f64"),
                _guard_expr(when, member_names, member_types)),
        IfStatement(fired, Block(reset_stmts), [], None),
        _assign_member(f"__guard_{k}_prev",
                       _guard_expr(when, member_names, member_types)),
    ]


def _make_outputs(flow: FlowDecl, member_names: Set[str]) -> FunctionDecl:
    """Name_outputs(self): inline output maps, in declaration order."""
    statements = [
        _assign_member(output.name, _rewrite(output.expr, member_names))
        for output in flow.outputs
    ]
    return _flow_fn(
        flow, "_outputs",
        [Parameter("self", _self_ptr_type(flow.name))],
        Type("void"), statements,
    )


def _in_state_order(flow: FlowDecl, evolved):
    """Evolves declarations ordered by state declaration order, so the
    generated signatures are deterministic and independent of the order the
    user wrote the 'evolves' lines (spec 2.2)."""
    position = {s.name: i for i, s in enumerate(flow.states)}
    return sorted(evolved, key=lambda ev: position[ev.target])
