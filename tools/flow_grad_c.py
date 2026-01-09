#!/usr/bin/env python3
"""Generate a tiny C program that computes gradients via a reverse-mode tape.

This is a **prototype**: it supports a subset of FLOW and emits C.

Supported:
- f32 literals
- variables (function parameters)
- let-bindings inside the function body (SSA-ish)
- binary ops: +, -, *, /
- unary ops: -
- calls: sin, cos, exp, log, sqrt, sigmoid

Usage:
  PYTHONPATH=src python3 tools/flow_grad_c.py <file.flow> <function_name>

Then compile the emitted C:
  clang -O2 out.c -lm -o out
"""

from __future__ import annotations

import sys
from typing import Dict, List, Tuple

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
    StructLiteral,
)


def _fmt_f32(v: str) -> str:
    s = str(v)
    if not s.endswith("f"):
        s += "f"
    return s


class TapeBuilder:
    def __init__(self, params: List[str]):
        self.params = params
        self.var_to_idx: Dict[str, int] = {name: i for i, name in enumerate(params)}
        self.locals: Dict[str, int] = {}  # let name -> node index
        self.nodes: List[Tuple[str, int, int]] = []  # (op, a, b)
        self.const_vals: List[str] = []

    def new_node(self, op: str, a: int = -1, b: int = -1, const: str | None = None) -> int:
        idx = len(self.nodes)
        self.nodes.append((op, a, b))
        if op == "const":
            self.const_vals.append(const or "0.0f")
        return idx

    def emit_expr(self, expr) -> int:
        if isinstance(expr, Literal):
            if expr.type.name != "f32" and "." not in str(expr.value) and "e" not in str(expr.value).lower():
                raise SystemExit("Prototype supports only f32 literals")
            return self.new_node("const", const=_fmt_f32(expr.value))

        if isinstance(expr, Variable):
            if expr.name in self.locals:
                return self.locals[expr.name]
            if expr.name not in self.var_to_idx:
                raise SystemExit(f"Unknown variable {expr.name}")
            return self.new_node(f"var{self.var_to_idx[expr.name]}")

        if isinstance(expr, UnaryOperation):
            if expr.operator == "-":
                x = self.emit_expr(expr.operand)
                return self.new_node("neg", x)
            raise SystemExit(f"Unsupported unary op: {expr.operator}")

        if isinstance(expr, BinaryOperation):
            a = self.emit_expr(expr.left)
            b = self.emit_expr(expr.right)
            op = expr.operator
            if op == "+":
                return self.new_node("add", a, b)
            if op == "-":
                return self.new_node("sub", a, b)
            if op == "*":
                return self.new_node("mul", a, b)
            if op == "/":
                return self.new_node("div", a, b)
            raise SystemExit(f"Unsupported binary op: {op}")

        if isinstance(expr, FunctionCall):
            if len(expr.arguments) != 1:
                raise SystemExit("Only single-arg calls supported")
            x = self.emit_expr(expr.arguments[0])
            name = expr.name
            if name in {"sin", "cos", "exp", "log", "sqrt", "sigmoid"}:
                return self.new_node(name, x)
            raise SystemExit(f"Unsupported call: {name}")

        if isinstance(expr, StructLiteral):
            raise SystemExit("Prototype expects scalar return, not struct")

        raise SystemExit(f"Unsupported expression node: {type(expr).__name__}")

    def emit_body(self, fn: FunctionDecl) -> int:
        out_idx = None
        for st in fn.body.statements:
            if isinstance(st, VarDecl):
                if st.initializer is None:
                    raise SystemExit("Prototype requires let initializers")
                self.locals[st.name] = self.emit_expr(st.initializer)
                continue
            if isinstance(st, ReturnStatement):
                if st.value is None:
                    raise SystemExit("Prototype requires return value")
                out_idx = self.emit_expr(st.value)
                continue
            raise SystemExit(f"Unsupported statement in prototype: {type(st).__name__}")

        if out_idx is None:
            raise SystemExit("No return found")
        return out_idx


def find_function(decls, name: str) -> FunctionDecl:
    for d in decls:
        if isinstance(d, FunctionDecl) and d.name == name:
            return d
    raise SystemExit(f"Function {name} not found")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: flow_grad_c.py <file.flow> <function_name>", file=sys.stderr)
        return 2

    path, fn_name = sys.argv[1], sys.argv[2]
    with open(path, "r") as f:
        code = f.read()

    decls = Parser(Lexer(code)).parse()
    fn = find_function(decls, fn_name)

    params = [p.name for p in fn.parameters]
    if not params:
        raise SystemExit("Need at least 1 parameter")

    tb = TapeBuilder(params)
    out_idx = tb.emit_body(fn)

    # op codes
    ops = {
        "const": 0,
        "add": 1,
        "sub": 2,
        "mul": 3,
        "div": 4,
        "neg": 5,
        "sin": 6,
        "cos": 7,
        "exp": 8,
        "log": 9,
        "sqrt": 10,
        "sigmoid": 11,
    }

    # materialize nodes with explicit op/a/b
    nodes: List[Tuple[int, int, int, str]] = []
    const_i = 0
    for op, a, b in tb.nodes:
        if op.startswith("var"):
            nodes.append((1000 + int(op[3:]), -1, -1, "0.0f"))
        elif op == "const":
            nodes.append((ops["const"], -1, -1, tb.const_vals[const_i]))
            const_i += 1
        else:
            nodes.append((ops[op], a, b, "0.0f"))

    print("#include <math.h>")
    print("#include <stdio.h>")
    print("#include <stdlib.h>")
    print("")
    print("typedef struct { int op; int a; int b; float val; float adj; } Node;")
    print("")

    print(f"#define N {len(nodes)}")
    print(f"#define NV {len(params)}")
    print("")

    print("static inline float sigmoidf(float x) { return 1.0f / (1.0f + expf(-x)); }")

    print("int main(int argc, char** argv) {")
    print("  if (argc != NV + 1) {")
    print("    fprintf(stderr, \"usage: %s\", argv[0]);")
    print("    for (int i=0;i<NV;i++) fprintf(stderr, \" x%d\", i);")
    print("    fprintf(stderr, \"\\n\");")
    print("    return 2;")
    print("  }")
    print("  float x[NV];")
    for i in range(len(params)):
        print(f"  x[{i}] = (float)atof(argv[{i+1}]);")

    print("  Node t[N];")
    for i, (op, a, b, v) in enumerate(nodes):
        print(f"  t[{i}].op = {op}; t[{i}].a = {a}; t[{i}].b = {b}; t[{i}].val = {v}; t[{i}].adj = 0.0f;")

    print("\n  // forward")
    print("  for (int i=0;i<N;i++) {")
    print("    int op = t[i].op;")
    print("    if (op >= 1000) { t[i].val = x[op-1000]; continue; }")
    print("    switch (op) {")
    print("      case 0: /* const */ break;")
    print("      case 1: t[i].val = t[t[i].a].val + t[t[i].b].val; break;")
    print("      case 2: t[i].val = t[t[i].a].val - t[t[i].b].val; break;")
    print("      case 3: t[i].val = t[t[i].a].val * t[t[i].b].val; break;")
    print("      case 4: t[i].val = t[t[i].a].val / t[t[i].b].val; break;")
    print("      case 5: t[i].val = -t[t[i].a].val; break;")
    print("      case 6: t[i].val = sinf(t[t[i].a].val); break;")
    print("      case 7: t[i].val = cosf(t[t[i].a].val); break;")
    print("      case 8: t[i].val = expf(t[t[i].a].val); break;")
    print("      case 9: t[i].val = logf(t[t[i].a].val); break;")
    print("      case 10: t[i].val = sqrtf(t[t[i].a].val); break;")
    print("      case 11: t[i].val = sigmoidf(t[t[i].a].val); break;")
    print("      default: fprintf(stderr, \"bad op %d\\n\", op); return 3;")
    print("    }")
    print("  }")

    print(f"\n  // backward")
    print(f"  t[{out_idx}].adj = 1.0f;")
    print("  float g[NV]; for (int i=0;i<NV;i++) g[i]=0.0f;")
    print("  for (int i=N-1;i>=0;i--) {")
    print("    int op = t[i].op;")
    print("    float adj = t[i].adj;")
    print("    if (op >= 1000) { g[op-1000] += adj; continue; }")
    print("    switch (op) {")
    print("      case 0: break;")
    print("      case 1: t[t[i].a].adj += adj; t[t[i].b].adj += adj; break;")
    print("      case 2: t[t[i].a].adj += adj; t[t[i].b].adj -= adj; break;")
    print("      case 3: t[t[i].a].adj += adj * t[t[i].b].val; t[t[i].b].adj += adj * t[t[i].a].val; break;")
    print("      case 4: {")
    print("        float a = t[t[i].a].val; float b = t[t[i].b].val;")
    print("        t[t[i].a].adj += adj * (1.0f/b);")
    print("        t[t[i].b].adj += adj * (-a/(b*b));")
    print("        break; }")
    print("      case 5: t[t[i].a].adj += -adj; break;")
    print("      case 6: t[t[i].a].adj += adj * cosf(t[t[i].a].val); break;")
    print("      case 7: t[t[i].a].adj += adj * (-sinf(t[t[i].a].val)); break;")
    print("      case 8: t[t[i].a].adj += adj * expf(t[t[i].a].val); break;")
    print("      case 9: t[t[i].a].adj += adj * (1.0f / t[t[i].a].val); break;")
    print("      case 10: t[t[i].a].adj += adj * (0.5f / sqrtf(t[t[i].a].val)); break;")
    print("      case 11: {")
    print("        float y = t[i].val; /* sigmoid(x) */")
    print("        t[t[i].a].adj += adj * (y * (1.0f - y));")
    print("        break; }")
    print("      default: break;")
    print("    }")
    print("  }")

    print(f"\n  printf(\"value = %.7g\\n\", t[{out_idx}].val);")
    for i, name in enumerate(params):
        print(f"  printf(\"d/d{name} = %.7g\\n\", g[{i}]);")
    print("  return 0;")
    print("}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
