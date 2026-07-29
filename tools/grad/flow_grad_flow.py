#!/usr/bin/env python3
"""Prototype: generate FLOW code for gradients of a scalar f32 function.

This is the "FLOW side" companion to `tools/grad/flow_grad_c.py`.

Input: a FLOW file containing a function `f(params...) -> f32`.
Output: a FLOW module containing:
- `struct Grad_<f>` with fields: value, d_<param>...
- `function grad_<f>(params...) -> Grad_<f>` that computes the value and grads
  using reverse-mode (static tape) codegen.
- `function grad_<f>_get(g, idx) -> f32` to index gradients

Supported subset:
- f32 literals
- variables (params + let-bound locals)
- let-bindings in the function body
- binary ops: +, -, *, /
- unary ops: -
- calls: sin, cos, exp, log, sqrt, sigmoid
- multi-arg function calls (inlined)

Usage:
  PYTHONPATH=src python3 tools/grad/flow_grad_flow.py <file.flow> <function_name> > out.flow
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

from flow.parser import Lexer, Parser
from flow.parser import (
    FunctionDecl,
    ReturnStatement,
    VarDecl,
    Literal,
    Variable,
    BinaryOperation,
    UnaryOperation,
    FunctionCall,
)


@dataclass
class Node:
    op: str
    a: int
    b: int
    # for const
    const: str | None = None


def _is_f32_literal(lit: Literal) -> bool:
    return lit.type.name == "f32" or "." in str(lit.value) or "e" in str(lit.value).lower()


def _fmt_f32(v: str) -> str:
    # FLOW numeric literals do not use a C-style "f" suffix
    return str(v)


def find_function(decls, name: str) -> Optional[FunctionDecl]:
    for d in decls:
        if isinstance(d, FunctionDecl) and d.name == name:
            return d
    return None


class Graph:
    def __init__(self, params: List[str], all_funcs: Dict[str, FunctionDecl]):
        self.params = params
        self.param_set = set(params)
        self.locals: Dict[str, int] = {}
        self.nodes: List[Node] = []
        self.all_funcs = all_funcs

    def add(self, node: Node) -> int:
        idx = len(self.nodes)
        self.nodes.append(node)
        return idx

    def emit(self, expr) -> int:
        if isinstance(expr, Literal):
            if not _is_f32_literal(expr):
                raise SystemExit("Only f32 literals supported")
            return self.add(Node("const", -1, -1, const=_fmt_f32(expr.value)))

        if isinstance(expr, Variable):
            if expr.name in self.locals:
                return self.locals[expr.name]
            if expr.name not in self.param_set:
                raise SystemExit(f"Unknown variable {expr.name}")
            return self.add(Node(f"var:{expr.name}", -1, -1))

        if isinstance(expr, UnaryOperation):
            if expr.operator != "-":
                raise SystemExit(f"Unsupported unary op {expr.operator}")
            a = self.emit(expr.operand)
            return self.add(Node("neg", a, -1))

        if isinstance(expr, BinaryOperation):
            a = self.emit(expr.left)
            b = self.emit(expr.right)
            op = expr.operator
            if op == "+":
                return self.add(Node("add", a, b))
            if op == "-":
                return self.add(Node("sub", a, b))
            if op == "*":
                return self.add(Node("mul", a, b))
            if op == "/":
                return self.add(Node("div", a, b))
            raise SystemExit(f"Unsupported binary op {op}")

        if isinstance(expr, FunctionCall):
            name = expr.name
            # Built-in single-arg functions
            if name in {"sin", "cos", "exp", "log", "sqrt", "sigmoid"}:
                if len(expr.arguments) != 1:
                    raise SystemExit(f"Built-in {name} requires exactly 1 argument")
                a = self.emit(expr.arguments[0])
                return self.add(Node(name, a, -1))
            
            # Try to inline user-defined functions
            fn_def = self.all_funcs.get(name)
            if fn_def is None:
                raise SystemExit(f"Unknown function: {name}")
            
            if len(expr.arguments) != len(fn_def.parameters):
                raise SystemExit(f"Argument count mismatch for {name}")
            
            # Inline the function by substituting arguments
            return self._inline_call(fn_def, expr.arguments)

        raise SystemExit(f"Unsupported expression node {type(expr).__name__}")

    def _inline_call(self, fn: FunctionDecl, args: List) -> int:
        """Inline a function call by emitting its body with substituted args."""
        # Save current locals
        saved_locals = dict(self.locals)
        
        # Emit argument values and bind to parameter names
        for param, arg_expr in zip(fn.parameters, args):
            arg_idx = self.emit(arg_expr)
            self.locals[param.name] = arg_idx
        
        # Emit the function body
        out = None
        for st in fn.body.statements:
            if isinstance(st, VarDecl):
                if st.initializer is None:
                    raise SystemExit(f"let initializer required in {fn.name}")
                self.locals[st.name] = self.emit(st.initializer)
                continue
            if isinstance(st, ReturnStatement):
                if st.value is None:
                    raise SystemExit(f"return value required in {fn.name}")
                out = self.emit(st.value)
                break  # Only process first return
        
        # Restore locals (remove function-local bindings)
        self.locals = saved_locals
        
        if out is None:
            raise SystemExit(f"No return in {fn.name}")
        return out

    def emit_body(self, fn: FunctionDecl) -> int:
        out = None
        for st in fn.body.statements:
            if isinstance(st, VarDecl):
                if st.initializer is None:
                    raise SystemExit("let initializer required")
                self.locals[st.name] = self.emit(st.initializer)
                continue
            if isinstance(st, ReturnStatement):
                if st.value is None:
                    raise SystemExit("return value required")
                out = self.emit(st.value)
                continue
            raise SystemExit(f"Unsupported statement {type(st).__name__}")
        if out is None:
            raise SystemExit("No return")
        return out


def gen_flow(fn: FunctionDecl, out_idx: int, g: Graph) -> str:
    params = g.params
    nodes = g.nodes

    # forward values as FLOW expressions
    val: List[str] = ["0.0" for _ in nodes]

    def v(i: int) -> str:
        return f"t{i}"

    for i, n in enumerate(nodes):
        if n.op == "const":
            val[i] = n.const or "0.0"
        elif n.op.startswith("var:"):
            val[i] = n.op.split(":", 1)[1]
        elif n.op == "add":
            val[i] = f"({v(n.a)} + {v(n.b)})"
        elif n.op == "sub":
            val[i] = f"({v(n.a)} - {v(n.b)})"
        elif n.op == "mul":
            val[i] = f"({v(n.a)} * {v(n.b)})"
        elif n.op == "div":
            val[i] = f"({v(n.a)} / {v(n.b)})"
        elif n.op == "neg":
            val[i] = f"(-1.0 * {v(n.a)})"
        elif n.op in {"sin", "cos", "exp", "log", "sqrt"}:
            val[i] = f"{n.op}({v(n.a)})"
        elif n.op == "sigmoid":
            val[i] = f"(1.0 / (1.0 + exp(-1.0 * {v(n.a)})))"
        else:
            raise SystemExit(f"Unhandled op {n.op}")

    # reverse-mode adjoints
    contrib: List[List[str]] = [[] for _ in nodes]
    contrib[out_idx].append("1.0")

    def adj(i: int) -> str:
        if not contrib[i]:
            return "0.0"
        return " + ".join(contrib[i])

    # propagate from high -> low (reverse topological)
    for i in range(len(nodes) - 1, -1, -1):
        n = nodes[i]
        ai = adj(i)
        if ai == "0.0":
            continue

        if n.op in {"const"} or n.op.startswith("var:"):
            continue

        if n.op == "add":
            contrib[n.a].append(f"({ai})")
            contrib[n.b].append(f"({ai})")
        elif n.op == "sub":
            contrib[n.a].append(f"({ai})")
            contrib[n.b].append(f"(-1.0 * ({ai}))")
        elif n.op == "mul":
            contrib[n.a].append(f"({ai}) * {v(n.b)}")
            contrib[n.b].append(f"({ai}) * {v(n.a)}")
        elif n.op == "div":
            contrib[n.a].append(f"({ai}) * (1.0 / {v(n.b)})")
            contrib[n.b].append(f"({ai}) * (-1.0 * {v(n.a)} / ({v(n.b)} * {v(n.b)}))")
        elif n.op == "neg":
            contrib[n.a].append(f"(-1.0 * ({ai}))")
        elif n.op == "sin":
            contrib[n.a].append(f"({ai}) * cos({v(n.a)})")
        elif n.op == "cos":
            contrib[n.a].append(f"({ai}) * (-1.0 * sin({v(n.a)}))")
        elif n.op == "exp":
            contrib[n.a].append(f"({ai}) * exp({v(n.a)})")
        elif n.op == "log":
            contrib[n.a].append(f"({ai}) * (1.0 / {v(n.a)})")
        elif n.op == "sqrt":
            contrib[n.a].append(f"({ai}) * (0.5 / sqrt({v(n.a)}))")
        elif n.op == "sigmoid":
            # y = sigmoid(x) => dy/dx = y(1-y)
            contrib[n.a].append(f"({ai}) * ({v(i)} * (1.0 - {v(i)}))")
        else:
            raise SystemExit(f"Unhandled op for backprop {n.op}")

    grad_fields = [f"d_{p}" for p in params]
    struct_name = f"Grad_{fn.name}"
    grad_fn = f"grad_{fn.name}"
    get_fn = f"{grad_fn}_get"

    out_lines: List[str] = []
    out_lines.append(f"struct {struct_name} {{")
    out_lines.append("    value: f32,")
    for p in params:
        out_lines.append(f"    d_{p}: f32,")
    out_lines.append("}")
    out_lines.append("")

    # function signature
    sig_params = ", ".join([f"{p}: f32" for p in params])
    out_lines.append(f"function {grad_fn}({sig_params}) -> {struct_name} {{")

    # forward lets
    for i, n in enumerate(nodes):
        out_lines.append(f"    let {v(i)}: f32 = {val[i]}")

    out_lines.append("")
    out_lines.append(f"    # reverse-mode adjoints")
    for i in range(len(nodes) - 1, -1, -1):
        out_lines.append(f"    let adj{i}: f32 = {adj(i)}")

    out_lines.append("")
    # compute param grads by summing adj of all var nodes referencing that param
    # (each parameter may appear multiple times as separate var nodes)
    # Find indices for var nodes
    var_nodes: Dict[str, List[int]] = {p: [] for p in params}
    for i, n in enumerate(nodes):
        if n.op.startswith("var:"):
            var_nodes[n.op.split(":", 1)[1]].append(i)

    for p in params:
        if not var_nodes[p]:
            out_lines.append(f"    let d_{p}: f32 = 0.0")
        else:
            s = " + ".join([f"adj{idx}" for idx in var_nodes[p]])
            out_lines.append(f"    let d_{p}: f32 = {s}")

    out_lines.append("")
    out_lines.append(f"    return {struct_name} {{")
    out_lines.append(f"        value: {v(out_idx)},")
    for p in params:
        out_lines.append(f"        d_{p}: d_{p},")
    out_lines.append("    }")
    out_lines.append("}")
    out_lines.append("")

    # indexer
    out_lines.append(f"function {get_fn}(g: {struct_name}, idx: i32) -> f32 {{")
    for i, p in enumerate(params):
        out_lines.append(f"    if idx == {i} {{ return g.d_{p} }}")
    out_lines.append("    return 0.0")
    out_lines.append("}")

    return "\n".join(out_lines) + "\n"


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: flow_grad_flow.py <file.flow> <function_name>", file=sys.stderr)
        return 2

    path, fn_name = sys.argv[1], sys.argv[2]
    with open(path, "r") as f:
        code = f.read()

    decls = Parser(Lexer(code)).parse()
    
    # Collect all function definitions for inlining
    all_funcs: Dict[str, FunctionDecl] = {}
    for d in decls:
        if isinstance(d, FunctionDecl):
            all_funcs[d.name] = d
    
    fn = all_funcs.get(fn_name)
    if fn is None:
        raise SystemExit(f"Function {fn_name} not found")

    if fn.return_type.name != "f32":
        raise SystemExit("Prototype expects f32 return")

    params = [p.name for p in fn.parameters]
    g = Graph(params, all_funcs)
    out_idx = g.emit_body(fn)

    sys.stdout.write(gen_flow(fn, out_idx, g))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
