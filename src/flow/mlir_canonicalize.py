"""AST canonicalizations applied before MLIR generation.

Two rewrites live here, both discovered while compiling Doom through the MLIR
backend:

* ``canonicalize_counted_loops`` rotates ``while true { P; if c == 0 { break }
  S }`` into ``P; while c != 0 { S; P }`` so the exit test sits at the loop
  latch instead of the middle of the body (issue #473). LLVM's loop optimizers
  need a latch compare to recover a trip count.
* ``find_trivial_accessors`` reports parameterless functions whose whole body
  is ``return &global`` or ``return global``, so the generator can substitute
  the global at each call site instead of emitting a call (issue #474).

Both are pure: they read the AST and return new nodes, never mutating the
input. The C backend keeps working on the original tree.
"""

from copy import copy
from dataclasses import fields, is_dataclass
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .parser import (
    Assignment,
    BinaryOperation,
    Block,
    BreakStatement,
    ContinueStatement,
    DeferStatement,
    Expression,
    FunctionDecl,
    Literal,
    ReturnStatement,
    UnaryOperation,
    VarDecl,
    Variable,
    WhileStatement,
)


# ---------------------------------------------------------------------------
# Generic AST walking
# ---------------------------------------------------------------------------

def _child_blocks(node: Any) -> Iterator[Tuple[Any, str, Any]]:
    """Yield (owner, field_name, value) for every field holding Block data."""
    if not is_dataclass(node):
        return
    for f in fields(node):
        value = getattr(node, f.name, None)
        if _contains_block(value):
            yield node, f.name, value


def _contains_block(value: Any) -> bool:
    if isinstance(value, Block):
        return True
    if isinstance(value, (list, tuple)):
        return any(_contains_block(v) for v in value)
    return False


def _walk_statements(node: Any) -> Iterator[Any]:
    """Yield every statement reachable from ``node``, depth first."""
    if isinstance(node, Block):
        for stmt in node.statements:
            yield from _walk_statements(stmt)
        return
    if isinstance(node, (list, tuple)):
        for item in node:
            yield from _walk_statements(item)
        return
    if not is_dataclass(node):
        return
    yield node
    for _, _, value in _child_blocks(node):
        yield from _walk_statements(value)


# ---------------------------------------------------------------------------
# #473 — counted-loop canonicalization
# ---------------------------------------------------------------------------

def _with_fields(node: Any, **updates: Any) -> Any:
    """Shallow-copy ``node`` with fields overridden.

    A plain copy rather than ``dataclasses.replace`` so attributes set after
    construction (and any non-init fields) survive the rewrite.
    """
    clone = copy(node)
    for name, value in updates.items():
        setattr(clone, name, value)
    return clone


def _is_literal_true(expr: Any) -> bool:
    return isinstance(expr, Literal) and str(expr.value).lower() == "true"


def _is_zero_literal(expr: Any) -> bool:
    if not isinstance(expr, Literal):
        return False
    text = str(expr.value)
    try:
        return int(text, 0) == 0
    except ValueError:
        return False


def _break_counter(stmt: Any) -> Optional[str]:
    """Return the counter name for ``if <ctr> == 0 { break }``, else None."""
    if not (
        hasattr(stmt, "then_block")
        and hasattr(stmt, "elif_blocks")
        and hasattr(stmt, "else_block")
    ):
        return None
    if stmt.elif_blocks or stmt.else_block is not None:
        return None
    body = getattr(stmt.then_block, "statements", None)
    if not body or len(body) != 1 or not isinstance(body[0], BreakStatement):
        return None
    cond = stmt.condition
    if not isinstance(cond, BinaryOperation) or cond.operator != "==":
        return None
    if isinstance(cond.left, Variable) and _is_zero_literal(cond.right):
        return cond.left.name
    if isinstance(cond.right, Variable) and _is_zero_literal(cond.left):
        return cond.right.name
    return None


def _is_decrement_of(stmt: Any, name: str) -> bool:
    """True for ``name = name - <literal>``."""
    if not isinstance(stmt, Assignment) or stmt.target_expr is not None:
        return False
    if stmt.target != name:
        return False
    value = stmt.value
    return (
        isinstance(value, BinaryOperation)
        and value.operator == "-"
        and isinstance(value.left, Variable)
        and value.left.name == name
        and isinstance(value.right, Literal)
    )


def _match_counted_loop(loop: WhileStatement):
    """Match the rotatable counted-loop shape.

    Returns ``(counter, prefix, suffix, break_if)`` or None.
    """
    if not _is_literal_true(loop.condition):
        return None

    stmts = list(loop.body.statements)
    break_index = None
    counter = None
    for i, stmt in enumerate(stmts):
        name = _break_counter(stmt)
        if name is None:
            continue
        if break_index is not None:
            return None  # more than one exit test; not the counted shape
        break_index, counter = i, name
    if break_index is None:
        return None

    prefix = stmts[:break_index]
    suffix = stmts[break_index + 1:]
    break_if = stmts[break_index]

    # The counter must be decremented exactly once, after the exit test. That
    # is what makes the rotated latch compare a real trip count.
    decrements = [s for s in suffix if _is_decrement_of(s, counter)]
    if len(decrements) != 1:
        return None

    # The recognized break must be the only loop-control statement in the body.
    # Anything else would change targets once the body is rotated. `defer` is
    # scope-sensitive for the same reason.
    for stmt in _walk_statements(loop.body):
        if isinstance(stmt, DeferStatement):
            return None
        if isinstance(stmt, (BreakStatement, ContinueStatement)):
            if not (isinstance(stmt, BreakStatement) and stmt is break_if.then_block.statements[0]):
                return None

    # The prefix is duplicated (once before the loop, once at the end of the
    # rotated body). A declaration there would land in two different scopes.
    for stmt in prefix:
        for inner in _walk_statements(stmt):
            if isinstance(inner, VarDecl):
                return None

    # A second assignment to the counter outside the decrement means the exit
    # test is not a plain countdown; leave it alone.
    for stmt in _walk_statements(loop.body):
        if isinstance(stmt, VarDecl) and stmt.name == counter:
            return None
        if (
            isinstance(stmt, Assignment)
            and stmt.target_expr is None
            and stmt.target == counter
            and stmt is not decrements[0]
        ):
            return None

    return counter, prefix, suffix, break_if


def _rotate(loop: WhileStatement, match) -> List[Any]:
    """Emit ``P; while ctr != 0 { S; P }`` for a matched loop."""
    counter, prefix, suffix, break_if = match
    zero = break_if.condition.right if isinstance(break_if.condition.left, Variable) else break_if.condition.left
    condition = BinaryOperation(
        left=Variable(name=counter),
        operator="!=",
        right=zero,
        line=getattr(break_if.condition, "line", 0),
    )
    rotated = _with_fields(
        loop,
        condition=condition,
        body=Block(statements=list(suffix) + list(prefix)),
    )
    return list(prefix) + [rotated]


def _rewrite_statement(stmt: Any) -> List[Any]:
    """Rewrite one statement, returning the statements that replace it."""
    if not is_dataclass(stmt):
        return [stmt]

    updates: Dict[str, Any] = {}
    for _, name, value in _child_blocks(stmt):
        updates[name] = _rewrite_block_field(value)
    if updates:
        stmt = _with_fields(stmt, **updates)

    if isinstance(stmt, WhileStatement):
        match = _match_counted_loop(stmt)
        if match is not None:
            return _rotate(stmt, match)
    return [stmt]


def _rewrite_block_field(value: Any) -> Any:
    if isinstance(value, Block):
        return canonicalize_counted_loops(value)
    if isinstance(value, list):
        return [_rewrite_block_field(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_rewrite_block_field(v) for v in value)
    return value


def canonicalize_counted_loops(block: Block) -> Block:
    """Rotate counted ``while true`` loops so the exit test sits at the latch.

    ``while true { P; if ctr == 0 { break }; S }`` becomes
    ``P; while ctr != 0 { S; P }``. Both forms evaluate the test at exactly the
    same points, so the iteration count is unchanged.
    """
    statements: List[Any] = []
    for stmt in block.statements:
        statements.extend(_rewrite_statement(stmt))
    return Block(statements=statements)


# ---------------------------------------------------------------------------
# #474 — trivial accessor inlining
# ---------------------------------------------------------------------------

def _accessor_target(func: FunctionDecl) -> Optional[Expression]:
    """Return the returned expression when ``func`` is a trivial accessor."""
    if getattr(func, "is_extern", False):
        return None
    if func.parameters:
        return None
    body = getattr(func, "body", None)
    statements = getattr(body, "statements", None)
    if not statements or len(statements) != 1:
        return None
    stmt = statements[0]
    if not isinstance(stmt, ReturnStatement) or stmt.value is None:
        return None
    value = stmt.value
    if isinstance(value, UnaryOperation) and value.operator == "&":
        return value if isinstance(value.operand, Variable) else None
    if isinstance(value, Variable):
        return value
    return None


def _referenced_global(expr: Expression) -> str:
    return expr.operand.name if isinstance(expr, UnaryOperation) else expr.name


def find_trivial_accessors(declarations: List[Any], is_module_global) -> Dict[str, Expression]:
    """Map accessor function name -> the expression to substitute for a call.

    An accessor is a parameterless function whose entire body is
    ``return &g`` or ``return g`` for a module-scope ``g``. ``is_module_global``
    is called with the referenced name and decides whether the symbol really is
    module storage.
    """
    accessors: Dict[str, Expression] = {}
    for decl in declarations:
        if not isinstance(decl, FunctionDecl):
            continue
        target = _accessor_target(decl)
        if target is None:
            continue
        name = _referenced_global(target)
        # A self-referential accessor would inline into itself forever.
        if name == decl.name:
            continue
        if not is_module_global(name):
            continue
        accessors[decl.name] = target
    return accessors
