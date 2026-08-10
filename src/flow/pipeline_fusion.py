"""Compile-time fusion of adjacent map stages in |> pipelines.

When the desugared AST contains `map_f32(map_f32(buf, n, f), n, g)`, this
pass rewrites it to `map_f32(buf, n, |x| g(f(x)))`, avoiding the
intermediate buffer allocation.

Supported fusions:
  map_T(map_T(buf, n, f), n, g)  ->  map_T(buf, n, |x| g(f(x)))
  scale_T(scale_T(buf, n, a), n, b)  ->  scale_T(buf, n, a*b)
  offset_T(offset_T(buf, n, a), n, b)  ->  offset_T(buf, n, a+b)

The pass walks every function body and replaces expressions in place.
"""
from typing import List, Any
from flow.parser import (
    FunctionDecl,
    FunctionCall,
    Lambda,
    BinaryOperation,
    UnaryOperation,
    Variable,
    VarDecl,
    ReturnStatement,
    IfStatement,
    ForStatement,
    Block,
)


# Functions that can be fused when nested with the same function name.
_FUSABLE = {"map_f32", "map_f64", "scale_f32", "scale_f64", "offset_f32", "offset_f64"}


def fuse_pipelines(declarations: List[Any]) -> List[Any]:
    """Run pipeline fusion on all function bodies. Returns the same list."""
    for decl in declarations:
        if isinstance(decl, FunctionDecl) and decl.body:
            _fuse_block(decl.body)
    return declarations


def _fuse_block(block: Block) -> None:
    """Walk statements in a block and fuse expressions."""
    for i, stmt in enumerate(block.statements):
        block.statements[i] = _fuse_stmt(stmt)


def _fuse_stmt(stmt: Any) -> Any:
    """Fuse a statement, returning the (possibly replaced) statement."""
    if isinstance(stmt, VarDecl):
        if stmt.initializer is not None:
            stmt.initializer = _fuse_expr(stmt.initializer)
        return stmt
    elif isinstance(stmt, ReturnStatement):
        if stmt.value is not None:
            stmt.value = _fuse_expr(stmt.value)
        return stmt
    elif isinstance(stmt, IfStatement):
        stmt.condition = _fuse_expr(stmt.condition)
        if stmt.then_block:
            _fuse_block(stmt.then_block)
        if stmt.else_block:
            _fuse_block(stmt.else_block)
        return stmt
    elif isinstance(stmt, ForStatement):
        if stmt.range_start:
            stmt.range_start = _fuse_expr(stmt.range_start)
        if stmt.range_end:
            stmt.range_end = _fuse_expr(stmt.range_end)
        if stmt.step:
            stmt.step = _fuse_expr(stmt.step)
        if stmt.body:
            _fuse_block(stmt.body)
        return stmt
    elif isinstance(stmt, Block):
        _fuse_block(stmt)
        return stmt
    else:
        # Expression statements are bare expressions (FunctionCall, etc.)
        return _fuse_expr(stmt)


def _fuse_expr(expr: Any) -> Any:
    """Recursively fuse pipeline expressions."""
    if expr is None:
        return expr
    # Recurse into sub-expressions first (bottom-up).
    if isinstance(expr, FunctionCall):
        expr.arguments = [_fuse_expr(a) for a in expr.arguments]
        return _try_fuse(expr)
    if isinstance(expr, BinaryOperation):
        expr.left = _fuse_expr(expr.left)
        expr.right = _fuse_expr(expr.right)
        return expr
    return expr


def _try_fuse(call: FunctionCall) -> Any:
    """Check if a call is a fusable pattern and rewrite it."""
    if call.name not in _FUSABLE:
        return call
    if len(call.arguments) < 2:
        return call
    inner = call.arguments[0]
    if not isinstance(inner, FunctionCall) or inner.name != call.name:
        return call
    if len(inner.arguments) < 2:
        return call

    # Map fusion: map(map(buf, n, f), n, g) -> map(buf, n, |x| g(f(x)))
    if call.name in ("map_f32", "map_f64"):
        return _fuse_map(call, inner)

    # Scale fusion: scale(scale(buf, n, a), n, b) -> scale(buf, n, a*b)
    if call.name in ("scale_f32", "scale_f64"):
        return _fuse_scale(call, inner)

    # Offset fusion: offset(offset(buf, n, a), n, b) -> offset(buf, n, a+b)
    if call.name in ("offset_f32", "offset_f64"):
        return _fuse_offset(call, inner)

    return call


def _fuse_map(outer: FunctionCall, inner: FunctionCall) -> FunctionCall:
    """Fuse map_T(map_T(buf, n, f), n, g) into map_T(buf, n, |x| g(f(x)))."""
    from flow.parser import Parameter, Type
    buf = inner.arguments[0]
    n = inner.arguments[1]
    f = inner.arguments[2]  # lambda: |x| -> f(x)
    g = outer.arguments[2]  # lambda: |x| -> g(x)

    # Create composed lambda: |x: T| -> g(f(x))
    elem_type = "f32" if outer.name == "map_f32" else "f64"

    # f(x): call f with Variable("x")
    f_call = _apply_lambda(f, Variable("x"))
    # g(f(x)): call g with f_call
    g_call = _apply_lambda(g, f_call)

    composed = Lambda(
        parameters=[Parameter(name="x", type=Type(name=elem_type))],
        return_type=Type(name=elem_type),
        body=Block(statements=[ReturnStatement(value=g_call)]),
    )

    return FunctionCall(outer.name, [buf, n, composed])


def _fuse_scale(outer: FunctionCall, inner: FunctionCall) -> FunctionCall:
    """Fuse scale_T(scale_T(buf, n, a), n, b) into scale_T(buf, n, a*b)."""
    buf = inner.arguments[0]
    n = inner.arguments[1]
    a = inner.arguments[2]
    b = outer.arguments[2]
    product = BinaryOperation(left=a, operator="*", right=b)
    return FunctionCall(outer.name, [buf, n, product])


def _fuse_offset(outer: FunctionCall, inner: FunctionCall) -> FunctionCall:
    """Fuse offset_T(offset_T(buf, n, a), n, b) into offset_T(buf, n, a+b)."""
    buf = inner.arguments[0]
    n = inner.arguments[1]
    a = inner.arguments[2]
    b = outer.arguments[2]
    total = BinaryOperation(left=a, operator="+", right=b)
    return FunctionCall(outer.name, [buf, n, total])


def _apply_lambda(lam: Lambda, arg: Any) -> Any:
    """Substitute the lambda's parameter with arg in its body, returning the result expression.

    For a simple lambda |x| -> expr, this replaces all occurrences of the
    parameter Variable with arg and returns the body expression.
    """
    # Get the parameter name from the lambda's parameters.
    param_name = lam.parameters[0].name if lam.parameters else "x"

    # The body is a Block with a single ReturnStatement.
    if (isinstance(lam.body, Block)
            and len(lam.body.statements) == 1
            and isinstance(lam.body.statements[0], ReturnStatement)):
        result_expr = lam.body.statements[0].value
        return _substitute_var(result_expr, param_name, arg)

    # Fallback: wrap in a call (shouldn't happen for our generated lambdas).
    return result_expr  # type: ignore[return-value]


def _substitute_var(expr: Any, name: str, replacement: Any) -> Any:
    """Replace all Variable references to `name` with `replacement`."""
    if isinstance(expr, Variable):
        if expr.name == name:
            return replacement
        return expr
    if isinstance(expr, BinaryOperation):
        expr.left = _substitute_var(expr.left, name, replacement)
        expr.right = _substitute_var(expr.right, name, replacement)
        return expr
    if isinstance(expr, FunctionCall):
        expr.arguments = [_substitute_var(a, name, replacement) for a in expr.arguments]
        return expr
    if isinstance(expr, UnaryOperation):
        expr.operand = _substitute_var(expr.operand, name, replacement)
        return expr
    return expr
