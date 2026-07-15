#!/usr/bin/env python3
"""
Programmable geometry diagram language (Turing-complete).

Supports variables, functions, loops, conditionals, and sampled curves —
enough to script Taylor-series geometric proofs and arbitrary plane figures.

Example (taylor-sin.geom):

    title Taylor approximations to sin(x)
    size 520 380
    axes 80 290 55 -3.5 3.5 -1.2 1.2
    plot sin(x) from -3.14 to 3.14 color #2c3e50 width 2.5
    def taylor_sin(x, k) { ... }
    for order in 1..3 { plot taylor_sin(x, order - 1) from -2.5 to 2.5 dash }
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from flow.geometry_diagram import (
    AxesSpec,
    CurvePath,
    DiagramLabel,
    GeometryDiagram,
    fill_between_curves,
)


class GeomScriptError(Exception):
    pass


@dataclass
class _Function:
    params: List[str]
    body: List[str]
    closure: Dict[str, Any]


class _Tokenizer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.tokens: List[Tuple[str, Any]] = []
        self._tokenize()

    def _tokenize(self) -> None:
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch.isspace():
                self.pos += 1
                continue
            if ch in "(){}[],:;+-*/^<>=!":
                if self.text[self.pos : self.pos + 2] in ("..", "<=", ">=", "==", "!="):
                    tok = self.text[self.pos : self.pos + 2]
                    self.tokens.append((tok, tok))
                    self.pos += 2
                    continue
                self.tokens.append((ch, ch))
                self.pos += 1
                continue
            if ch in "\"'":
                quote = ch
                self.pos += 1
                start = self.pos
                while self.pos < len(self.text) and self.text[self.pos] != quote:
                    self.pos += 1
                self.tokens.append(("STRING", self.text[start : self.pos]))
                self.pos += 1
                continue
            if ch == "#":
                while self.pos < len(self.text) and self.text[self.pos] != "\n":
                    self.pos += 1
                continue
            if ch.isdigit() or (ch == "." and self._peek_digit()):
                start = self.pos
                while self.pos < len(self.text) and (
                    self.text[self.pos].isdigit() or self.text[self.pos] == "."
                ):
                    self.pos += 1
                self.tokens.append(("NUMBER", float(self.text[start : self.pos])))
                continue
            if ch.isalpha() or ch == "_":
                start = self.pos
                while self.pos < len(self.text) and (
                    self.text[self.pos].isalnum() or self.text[self.pos] == "_"
                ):
                    self.pos += 1
                word = self.text[start : self.pos]
                if word == "true":
                    self.tokens.append(("NUMBER", 1.0))
                elif word == "false":
                    self.tokens.append(("NUMBER", 0.0))
                else:
                    self.tokens.append(("IDENT", word))
                continue
            raise GeomScriptError(f"Unexpected character {ch!r} at {self.pos}")

    def _peek_digit(self) -> bool:
        return self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit()


class _Parser:
    def __init__(self, tokens: List[Tuple[str, Any]]) -> None:
        self.tokens = tokens
        self.i = 0

    def _peek(self) -> Tuple[str, Any]:
        if self.i >= len(self.tokens):
            return ("EOF", None)
        return self.tokens[self.i]

    def _eat(self, kind: Optional[str] = None) -> Tuple[str, Any]:
        tok = self._peek()
        if kind and tok[0] != kind:
            raise GeomScriptError(f"Expected {kind}, got {tok[0]}")
        self.i += 1
        return tok

    def parse_expr(self) -> Any:
        return self._parse_or()

    def _parse_or(self) -> Any:
        left = self._parse_and()
        while self._peek()[0] == "||":
            self._eat()
            right = self._parse_and()
            left = ("||", left, right)
        return left

    def _parse_and(self) -> Any:
        left = self._parse_compare()
        while self._peek()[0] == "&&":
            self._eat()
            right = self._parse_compare()
            left = ("&&", left, right)
        return left

    def _parse_compare(self) -> Any:
        left = self._parse_add()
        while self._peek()[0] in ("<", ">", "<=", ">=", "==", "!="):
            op = self._eat()[0]
            right = self._parse_add()
            left = (op, left, right)
        return left

    def _parse_add(self) -> Any:
        left = self._parse_mul()
        while self._peek()[0] in ("+", "-"):
            op = self._eat()[0]
            right = self._parse_mul()
            left = (op, left, right)
        return left

    def _parse_mul(self) -> Any:
        left = self._parse_pow()
        while self._peek()[0] in ("*", "/"):
            op = self._eat()[0]
            right = self._parse_pow()
            left = (op, left, right)
        return left

    def _parse_pow(self) -> Any:
        left = self._parse_unary()
        if self._peek()[0] == "^":
            self._eat()
            right = self._parse_pow()
            return ("^", left, right)
        return left

    def _parse_unary(self) -> Any:
        if self._peek()[0] == "-":
            self._eat()
            return ("-", self._parse_unary())
        if self._peek()[0] == "+":
            self._eat()
            return self._parse_unary()
        return self._parse_atom()

    def _parse_atom(self) -> Any:
        tok = self._peek()
        if tok[0] == "NUMBER":
            self._eat()
            return tok[1]
        if tok[0] == "IDENT":
            name = self._eat()[1]
            if self._peek()[0] == "(":
                self._eat("(")
                args: List[Any] = []
                if self._peek()[0] != ")":
                    args.append(self.parse_expr())
                    while self._peek()[0] == ",":
                        self._eat(",")
                        args.append(self.parse_expr())
                self._eat(")")
                return ("call", name, args)
            return ("var", name)
        if tok[0] == "(":
            self._eat("(")
            expr = self.parse_expr()
            self._eat(")")
            return expr
        raise GeomScriptError(f"Unexpected token {tok}")


class GeometryScriptEngine:
    """Execute geometry scripts and produce a GeometryDiagram."""

    _PALETTE = ["#2c3e50", "#c0392b", "#2980b9", "#27ae60", "#8e44ad", "#d35400"]

    def __init__(self) -> None:
        self.env: Dict[str, Any] = self._default_env()
        self.diagram = GeometryDiagram(title="Scripted figure")
        self._block_stack: List[Dict[str, Any]] = []

    def _default_env(self) -> Dict[str, Any]:
        return {
            "pi": math.pi,
            "e": math.e,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "exp": math.exp,
            "log": math.log,
            "sqrt": math.sqrt,
            "abs": abs,
            "pow": pow,
            "min": min,
            "max": max,
            "fact": self._builtin_fact,
            "palette": self._builtin_palette,
            "taylor_sin": self._builtin_taylor_sin,
            "taylor_exp": self._builtin_taylor_exp,
            "x": 0.0,
        }

    @staticmethod
    def _builtin_fact(n: float) -> float:
        k = int(round(n))
        if k < 0:
            return 1.0
        out = 1.0
        for i in range(2, k + 1):
            out *= i
        return out

    def _builtin_palette(self, i: float) -> str:
        idx = int(round(i)) % len(self._PALETTE)
        return self._PALETTE[idx]

    @staticmethod
    def _builtin_taylor_sin(x: float, order: float) -> float:
        k = int(round(order))
        total = 0.0
        for i in range(k + 1):
            p = 2 * i + 1
            total += ((-1.0) ** i) * (x**p) / math.factorial(p)
        return total

    @staticmethod
    def _builtin_taylor_exp(x: float, order: float) -> float:
        k = int(round(order))
        total = 0.0
        for i in range(k + 1):
            total += (x**i) / math.factorial(i)
        return total

    def run(self, source: str) -> GeometryDiagram:
        lines = source.splitlines()
        i = 0
        while i < len(lines):
            raw = lines[i].strip()
            i += 1
            if not raw or raw.startswith("#"):
                continue
            if raw.endswith("{"):
                header = raw[:-1].strip()
                block_lines: List[str] = []
                depth = 1
                while i < len(lines) and depth > 0:
                    line = lines[i]
                    i += 1
                    stripped = line.strip()
                    depth += stripped.count("{") - stripped.count("}")
                    if depth > 0:
                        block_lines.append(line)
                self._exec_block_header(header, block_lines)
                continue
            self._exec_line(raw)
        return self.diagram

    def _exec_block_header(self, header: str, body: List[str]) -> None:
        if header.startswith("def "):
            rest = header[4:].strip()
            if "(" not in rest:
                raise GeomScriptError(f"Invalid def: {header}")
            name, rest = rest.split("(", 1)
            params_part = rest.rsplit(")", 1)[0]
            params = [p.strip() for p in params_part.split(",") if p.strip()]
            self.env[name.strip()] = _Function(params, body, dict(self.env))
            return
        if header.startswith("if "):
            cond = self._eval_expr(self._parse_expr(header[3:].strip()))
            if cond:
                self._run_lines(body)
            return
        if header.startswith("while "):
            cond_src = header[6:].strip()
            guard = 0
            while self._eval_expr(self._parse_expr(cond_src)) and guard < 100_000:
                self._run_lines(body)
                guard += 1
            if guard >= 100_000:
                raise GeomScriptError("while loop exceeded 100000 iterations")
            return
        if header.startswith("for "):
            rest = header[4:].strip()
            if " in " not in rest:
                raise GeomScriptError(f"Invalid for: {header}")
            var, rng = rest.split(" in ", 1)
            var = var.strip()
            lo, hi = self._parse_range(rng.strip())
            for n in range(lo, hi + 1):
                self.env[var] = float(n)
                self._run_lines(body)
            return
        raise GeomScriptError(f"Unknown block: {header}")

    def _run_lines(self, lines: List[str]) -> None:
        src = "\n".join(lines)
        sub = GeometryScriptEngine()
        sub.env = dict(self.env)
        sub.diagram = self.diagram
        sub.run(src)
        self.env = sub.env

    def _parse_range(self, text: str) -> Tuple[int, int]:
        if ".." in text:
            left, right = text.split("..", 1)
            return int(self._eval_expr(self._parse_expr(left.strip()))), int(
                self._eval_expr(self._parse_expr(right.strip()))
            )
        raise GeomScriptError(f"Expected range with .., got {text}")

    def _parse_expr(self, text: str) -> Any:
        tokens = _Tokenizer(text).tokens
        return _Parser(tokens).parse_expr()

    def _eval_expr(self, ast: Any) -> Any:
        if isinstance(ast, float):
            return ast
        if isinstance(ast, tuple) and ast[0] == "var":
            name = ast[1]
            if name not in self.env:
                raise GeomScriptError(f"Undefined variable: {name}")
            return self.env[name]
        if isinstance(ast, tuple) and ast[0] == "call":
            name, args = ast[1], ast[2]
            vals = [self._eval_expr(a) for a in args]
            if name in self.env and isinstance(self.env[name], _Function):
                fn = self.env[name]
                local = dict(fn.closure)
                for p, v in zip(fn.params, vals):
                    local[p] = v
                sub = GeometryScriptEngine()
                sub.env = local
                sub.diagram = self.diagram
                sub._run_lines(fn.body)
                if "_return" in sub.env:
                    return sub.env["_return"]
                return 0.0
            if name not in self.env:
                raise GeomScriptError(f"Undefined function: {name}")
            fn = self.env[name]
            if not callable(fn):
                raise GeomScriptError(f"{name} is not callable")
            return fn(*vals)
        if isinstance(ast, tuple) and ast[0] == "-":
            return -self._eval_expr(ast[1])
        if isinstance(ast, tuple) and ast[0] in ("+", "-", "*", "/", "^"):
            op, left, right = ast[0], self._eval_expr(ast[1]), self._eval_expr(ast[2])
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                return left / right
            if op == "^":
                return left**right
        if isinstance(ast, tuple) and ast[0] in ("<", ">", "<=", ">=", "==", "!="):
            op, left, right = ast[0], self._eval_expr(ast[1]), self._eval_expr(ast[2])
            if op == "<":
                return left < right
            if op == ">":
                return left > right
            if op == "<=":
                return left <= right
            if op == ">=":
                return left >= right
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
        if isinstance(ast, tuple) and ast[0] in ("||", "&&"):
            if ast[0] == "||":
                return self._eval_expr(ast[1]) or self._eval_expr(ast[2])
            return self._eval_expr(ast[1]) and self._eval_expr(ast[2])
        return ast

    def _exec_line(self, line: str) -> None:
        if line.startswith("return "):
            self.env["_return"] = self._eval_expr(self._parse_expr(line[7:].strip()))
            return
        if line.startswith("let "):
            rest = line[4:].strip()
            if "=" not in rest:
                raise GeomScriptError(f"Invalid let: {line}")
            name, expr = rest.split("=", 1)
            self.env[name.strip()] = self._eval_expr(self._parse_expr(expr.strip()))
            return
        if line.startswith("title "):
            self.diagram.title = self._string_arg(line[6:])
            return
        if line.startswith("caption "):
            self.diagram.caption = self._string_arg(line[8:])
            return
        if line.startswith("size "):
            parts = line[5:].split()
            self.diagram.width = int(float(parts[0]))
            self.diagram.height = int(float(parts[1]))
            return
        if line.startswith("axes "):
            parts = line[5:].split()
            if len(parts) < 7:
                raise GeomScriptError("axes ox oy scale xmin xmax ymin ymax")
            self.diagram.axes = AxesSpec(
                origin_x=float(parts[0]),
                origin_y=float(parts[1]),
                scale=float(parts[2]),
                x_min=float(parts[3]),
                x_max=float(parts[4]),
                y_min=float(parts[5]),
                y_max=float(parts[6]),
            )
            return
        if line.startswith("plot "):
            self._cmd_plot(line[5:])
            return
        if line.startswith("fill "):
            self._cmd_fill(line[5:])
            return
        if line.startswith("text "):
            self._cmd_text(line[5:])
            return
        raise GeomScriptError(f"Unknown statement: {line}")

    def _string_arg(self, text: str) -> str:
        text = text.strip()
        if (text.startswith('"') and text.endswith('"')) or (
            text.startswith("'") and text.endswith("'")
        ):
            return text[1:-1]
        return text

    def _parse_plot_clause(self, text: str) -> Tuple[Any, float, float, Dict[str, Any]]:
        opts: Dict[str, Any] = {
            "color": "#2980b9",
            "width": 2.2,
            "dash": False,
            "label": "",
            "samples": 160,
        }
        expr_src = text
        if " from " in text:
            expr_src, range_part = text.split(" from ", 1)
            if " to " not in range_part:
                raise GeomScriptError(f"plot range needs 'to': {text}")
            lo_s, rest = range_part.split(" to ", 1)
            rest_parts = rest.split()
            hi_s = rest_parts[0]
            lo = self._eval_expr(self._parse_expr(lo_s.strip()))
            hi = self._eval_expr(self._parse_expr(hi_s.strip()))
            if len(rest_parts) > 1:
                text = " ".join(rest_parts[1:])
            else:
                text = ""
        else:
            lo, hi = -3.14, 3.14

        for key in ("color", "width", "label", "samples"):
            m = re.search(rf"\b{key}\s+(\S+)", text)
            if m:
                val: Any = m.group(1)
                if key in ("width", "samples"):
                    val = float(val)
                if key == "dash":
                    val = True
                opts[key] = val
                text = text.replace(m.group(0), "")
        if re.search(r"\bdash\b", text):
            opts["dash"] = True
            text = re.sub(r"\bdash\b", "", text)

        ast = self._parse_expr(expr_src.strip())
        return ast, float(lo), float(hi), opts

    def _sample_curve(self, ast: Any, lo: float, hi: float, samples: int) -> List[Tuple[float, float]]:
        pts: List[Tuple[float, float]] = []
        if samples < 2:
            samples = 2
        for i in range(samples):
            t = lo + (hi - lo) * i / (samples - 1)
            self.env["x"] = t
            y = float(self._eval_expr(ast))
            pts.append((t, y))
        return pts

    def _cmd_plot(self, text: str) -> None:
        ast, lo, hi, opts = self._parse_plot_clause(text)
        math_pts = self._sample_curve(ast, lo, hi, int(opts["samples"]))
        pixel_pts = self._math_to_pixel(math_pts)
        self.diagram.curves.append(
            CurvePath(
                points=pixel_pts,
                stroke=str(opts["color"]),
                stroke_width=float(opts["width"]),
                dashed=bool(opts["dash"]),
                label=str(opts.get("label", "")),
            )
        )

    def _cmd_fill(self, text: str) -> None:
        # fill between expr1 and expr2 from lo to hi color #rrggbb@alpha
        m = re.match(
            r"between\s+(.+?)\s+and\s+(.+?)\s+from\s+(.+?)\s+to\s+(.+?)(?:\s+color\s+(\S+))?",
            text,
            re.I,
        )
        if not m:
            raise GeomScriptError(f"fill syntax: between f and g from a to b [color #hex@alpha]")
        e1, e2, lo_s, hi_s, color = m.groups()
        lo = float(self._eval_expr(self._parse_expr(lo_s.strip())))
        hi = float(self._eval_expr(self._parse_expr(hi_s.strip())))
        ast1 = self._parse_expr(e1.strip())
        ast2 = self._parse_expr(e2.strip())
        pts1 = self._math_to_pixel(self._sample_curve(ast1, lo, hi, 80))
        pts2 = self._math_to_pixel(self._sample_curve(ast2, lo, hi, 80))
        fill = color or "#f39c12@25"
        self.diagram.fills.append(fill_between_curves(pts1, pts2, fill))

    def _cmd_text(self, text: str) -> None:
        # text ox oy "label"  OR  text 0.5 1.1 math "sin(x)" with axes
        parts = text.split(None, 2)
        if len(parts) < 3:
            raise GeomScriptError("text x y \"label\"")
        x = float(parts[0]) if self.diagram.axes is None else float(parts[0])
        y = float(parts[1])
        label = self._string_arg(parts[2])
        if self.diagram.axes:
            ax = self.diagram.axes
            px = ax.origin_x + x * ax.scale
            py = ax.origin_y - y * ax.scale
        else:
            px, py = x, y
        self.diagram.labels.append(DiagramLabel(px, py, label))

    def _math_to_pixel(self, pts: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        if not self.diagram.axes:
            raise GeomScriptError("plot/fill requires axes (set axes ox oy scale xmin xmax ymin ymax)")
        ax = self.diagram.axes
        out: List[Tuple[float, float]] = []
        for mx, my in pts:
            px = ax.origin_x + mx * ax.scale
            py = ax.origin_y - my * ax.scale
            out.append((px, py))
        return out


def run_geometry_script(source: str) -> GeometryDiagram:
    return GeometryScriptEngine().run(source)


def run_geometry_script_file(path: str) -> GeometryDiagram:
    text = Path(path).read_text(encoding="utf-8")
    return run_geometry_script(text)


def load_script_for_theorem(
    meta_diagram_script: str,
    *,
    flow_file_dir: Optional[str] = None,
) -> Optional[GeometryDiagram]:
    """Load inline script or path relative to the .flow file."""
    src = meta_diagram_script.strip()
    if not src:
        return None
    if "\n" in src or src.strip().startswith(("title ", "axes ", "plot ", "let ", "def ")):
        return run_geometry_script(src)
    path = Path(src)
    if not path.is_absolute() and flow_file_dir:
        path = Path(flow_file_dir) / path
    if path.is_file():
        return run_geometry_script_file(str(path))
    # bundled name under examples/verify/geometry/scripts/
    root = Path(__file__).resolve().parents[2]
    alt = root / "examples" / "verify" / "geometry" / "scripts" / src
    if alt.is_file():
        return run_geometry_script_file(str(alt))
    raise GeomScriptError(f"Diagram script not found: {src}")