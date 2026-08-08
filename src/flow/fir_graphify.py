#!/usr/bin/env python3
"""AST → FIR-G graphification (Phase 1 coarse lowering).

Produces a dense program graph suitable for call-graph / effect / reachability
analyses. Not a full SSA builder yet — calls, returns, and structural shells
are enough for Phase 1 CPU reference algorithms.
"""

from __future__ import annotations

from typing import Any, List, Optional

from .fir_g import (
    EFF_ALLOCATES,
    EFF_FFI,
    EFF_IO,
    EFF_NONE,
    EFF_UNKNOWN,
    EFF_WRITES_MEMORY,
    FirG,
    OpCode,
)
from .parser import (
    Assignment,
    BinaryOperation,
    Block,
    EffectCall,
    FunctionCall,
    FunctionDecl,
    IfStatement,
    Literal,
    MethodCall,
    ReturnStatement,
    VarDecl,
    WhileStatement,
    ForStatement,
    UnaryOperation,
)


_IO_NAMES = {
    "print",
    "println",
    "printf",
    "puts",
    "fprintf",
    "fputs",
    "read",
    "write",
    "fopen",
    "fclose",
}
_ALLOC_NAMES = {"malloc", "calloc", "realloc", "free", "alloc", "arena_alloc"}


def _type_name(t: Any) -> str:
    if t is None:
        return "void"
    name = getattr(t, "name", None)
    return name if isinstance(name, str) else "unknown"


def _guess_effect_for_name(name: str, is_extern: bool) -> int:
    bits = EFF_NONE
    if is_extern:
        bits |= EFF_FFI
    if name in _IO_NAMES or name.startswith("flow_gfx_") or name.startswith("flow_audio_"):
        bits |= EFF_IO
    if name in _ALLOC_NAMES:
        bits |= EFF_ALLOCATES | EFF_WRITES_MEMORY
    return bits


def graphify(declarations: List[Any]) -> FirG:
    """Lower monomorphized declarations into a FIR-G module."""
    g = FirG()
    void_ty = g.intern_type("void")
    i32_ty = g.intern_type("i32")

    # Pass 1: register all functions (including extern).
    for decl in declarations:
        if not isinstance(decl, FunctionDecl):
            continue
        effects = _guess_effect_for_name(decl.name, bool(getattr(decl, "is_extern", False)))
        if getattr(decl, "attributes", None) and "gpu" in (decl.attributes or []):
            from .fir_g import EFF_GPU

            effects |= EFF_GPU
        g.add_function(
            decl.name,
            is_extern=bool(getattr(decl, "is_extern", False)),
            effect_bits=effects,
        )

    # Pass 2: bodies → blocks/ops.
    for decl in declarations:
        if not isinstance(decl, FunctionDecl):
            continue
        fid = g._func_by_name[decl.name]
        if getattr(decl, "is_extern", False) or decl.body is None:
            # Extern / declaration-only: empty entry block.
            g.add_block(fid)
            continue

        bid = g.add_block(fid)
        # Parameters as PARAM ops.
        for p in decl.parameters or []:
            tid = g.intern_type(_type_name(getattr(p, "type", None)))
            g.add_op(OpCode.PARAM, fid, bid, result_type_ids=[tid])

        _lower_block(g, fid, bid, decl.body, i32_ty, void_ty)

        # Ensure at least one terminator if empty.
        if g.block_op_count[bid] == 0:
            g.add_op(OpCode.RET, fid, bid)

    g.finalize_uses()
    g.build_call_graph_csr()
    return g


def _lower_block(
    g: FirG,
    fid: int,
    bid: int,
    block: Optional[Block],
    i32_ty: int,
    void_ty: int,
) -> None:
    if block is None:
        return
    for stmt in block.statements:
        _lower_stmt(g, fid, bid, stmt, i32_ty, void_ty)


def _lower_stmt(
    g: FirG,
    fid: int,
    bid: int,
    stmt: Any,
    i32_ty: int,
    void_ty: int,
) -> None:
    if isinstance(stmt, ReturnStatement):
        ops: List[int] = []
        if getattr(stmt, "value", None) is not None:
            vid = _lower_expr(g, fid, bid, stmt.value, i32_ty)
            if vid is not None:
                ops.append(vid)
        g.add_op(OpCode.RET, fid, bid, operand_values=ops)
        return

    if isinstance(stmt, VarDecl):
        if stmt.initializer is not None:
            vid = _lower_expr(g, fid, bid, stmt.initializer, i32_ty)
            tid = g.intern_type(_type_name(stmt.type))
            # Model as store into an alloca result.
            alloc, _ = g.add_op(OpCode.ALLOCA, fid, bid, result_type_ids=[tid])
            operands = []
            # result of alloca is first result value
            ptr = g.op_result_begin[alloc]
            operands.append(ptr)
            if vid is not None:
                operands.append(vid)
            g.add_op(OpCode.STORE, fid, bid, operand_values=operands)
        return

    if isinstance(stmt, Assignment):
        # value side only for Phase 1 graph edges
        _lower_expr(g, fid, bid, stmt.value, i32_ty)
        g.add_op(OpCode.STORE, fid, bid, flags=0)
        return

    if isinstance(stmt, IfStatement):
        _lower_expr(g, fid, bid, stmt.condition, i32_ty)
        then_b = g.add_block(fid)
        _lower_block(g, fid, then_b, stmt.then_block, i32_ty, void_ty)
        else_b = -1
        if stmt.else_block is not None:
            else_b = g.add_block(fid)
            _lower_block(g, fid, else_b, stmt.else_block, i32_ty, void_ty)
        for _, eblk in getattr(stmt, "elif_blocks", []) or []:
            eb = g.add_block(fid)
            _lower_block(g, fid, eb, eblk, i32_ty, void_ty)
        g.add_op(OpCode.COND_BR, fid, bid)
        return

    if isinstance(stmt, (WhileStatement, ForStatement)):
        body_b = g.add_block(fid)
        if isinstance(stmt, WhileStatement):
            _lower_expr(g, fid, bid, stmt.condition, i32_ty)
            _lower_block(g, fid, body_b, stmt.body, i32_ty, void_ty)
        else:
            _lower_block(g, fid, body_b, stmt.body, i32_ty, void_ty)
        g.add_op(OpCode.BR, fid, bid)
        return

    if isinstance(stmt, (FunctionCall, MethodCall, EffectCall)):
        _lower_expr(g, fid, bid, stmt, i32_ty)
        return

    # Expression statements / unknown: try as expression
    if hasattr(stmt, "__dataclass_fields__") or hasattr(stmt, "operator"):
        try:
            _lower_expr(g, fid, bid, stmt, i32_ty)
        except Exception:
            g.add_op(OpCode.OTHER, fid, bid)


def _lower_expr(
    g: FirG, fid: int, bid: int, expr: Any, default_ty: int
) -> Optional[int]:
    if expr is None:
        return None

    if isinstance(expr, Literal):
        tid = g.intern_type(_type_name(expr.type) if getattr(expr, "type", None) else "i32")
        _, results = g.add_op(OpCode.CONST, fid, bid, result_type_ids=[tid])
        return results[0] if results else None

    if isinstance(expr, BinaryOperation):
        left = _lower_expr(g, fid, bid, expr.left, default_ty)
        right = _lower_expr(g, fid, bid, expr.right, default_ty)
        ops = [v for v in (left, right) if v is not None]
        _, results = g.add_op(
            OpCode.BINOP, fid, bid, operand_values=ops, result_type_ids=[default_ty]
        )
        return results[0] if results else None

    if isinstance(expr, UnaryOperation):
        inner = _lower_expr(g, fid, bid, expr.operand, default_ty)
        ops = [inner] if inner is not None else []
        _, results = g.add_op(
            OpCode.UNOP, fid, bid, operand_values=ops, result_type_ids=[default_ty]
        )
        return results[0] if results else None

    if isinstance(expr, FunctionCall):
        arg_vids: List[int] = []
        for a in expr.arguments or []:
            v = _lower_expr(g, fid, bid, a, default_ty)
            if v is not None:
                arg_vids.append(v)
        callee = g._func_by_name.get(expr.name, -1)
        # Intrinsics / builtins may not be FunctionDecls — still attribute effects.
        if expr.name in _IO_NAMES:
            g.func_effect_bits[fid] |= EFF_IO
        if expr.name in _ALLOC_NAMES:
            g.func_effect_bits[fid] |= EFF_ALLOCATES | EFF_WRITES_MEMORY
        _, results = g.add_op(
            OpCode.CALL,
            fid,
            bid,
            operand_values=arg_vids,
            result_type_ids=[default_ty],
            callee=callee,
        )
        if callee < 0 and expr.name not in _IO_NAMES and expr.name not in _ALLOC_NAMES:
            g.func_effect_bits[fid] |= EFF_UNKNOWN
        return results[0] if results else None

    if isinstance(expr, MethodCall):
        # Treat as call by method name if registered; else OTHER.
        name = getattr(expr, "method", None) or getattr(expr, "name", "")
        callee = g._func_by_name.get(name, -1)
        _, results = g.add_op(
            OpCode.CALL,
            fid,
            bid,
            result_type_ids=[default_ty],
            callee=callee,
        )
        return results[0] if results else None

    if isinstance(expr, EffectCall):
        g.func_effect_bits[fid] |= EFF_UNKNOWN
        _, results = g.add_op(
            OpCode.EFFECT, fid, bid, result_type_ids=[default_ty]
        )
        return results[0] if results else None

    # Variable / other — opaque load
    _, results = g.add_op(OpCode.LOAD, fid, bid, result_type_ids=[default_ty])
    return results[0] if results else None
