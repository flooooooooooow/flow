"""Tiny FLOW fill-shader surface language.

Example
-------
```flow
shader fill plasma {
    let u = uv.x
    let v = uv.y
    color = vec4(
        0.5 + 0.5 * sin(u * 10.0 + time),
        0.5 + 0.5 * cos(v * 8.0 - time),
        0.5 + 0.5 * sin(time),
        1.0
    )
}
```

Builtins: `uv` (vec2), `time` (f32), `color` (vec4, required assign).
Helpers: sin/cos/abs/sqrt/min/max/fract/length/mix/smoothstep/pow,
         vec2/vec3/vec4, swizzles (.xyzw / .rgb).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union


@dataclass
class FillShader:
    name: str
    body: str  # raw body text between braces
    line: int = 1


_SHADER_HEAD = re.compile(
    r"shader\s+fill\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{",
    re.MULTILINE,
)


def extract_fill_shaders(source: str) -> List[FillShader]:
    """Pull `shader fill Name { ... }` blocks from a .flow source file."""
    shaders: List[FillShader] = []
    for match in _SHADER_HEAD.finditer(source):
        name = match.group(1)
        start = match.end()
        depth = 1
        i = start
        while i < len(source) and depth > 0:
            ch = source[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            i += 1
        if depth != 0:
            raise SyntaxError(f"Unclosed shader fill '{name}'")
        body = source[start : i - 1]
        line = source.count("\n", 0, match.start()) + 1
        shaders.append(FillShader(name=name, body=body, line=line))
    return shaders


# ── Body lexer / parser (tiny expression language) ──────────────────

class _Tok:
    def __init__(self, kind: str, value: str, pos: int):
        self.kind = kind
        self.value = value
        self.pos = pos


_TOKEN_SPEC = [
    ("NUMBER", r"\d+\.\d+|\d+\.|\.\d+|\d+"),
    ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP", r"\+|\-|\*|\/"),
    ("COMPARE", r"<=|>=|==|!=|<|>"),
    ("ASSIGN", r"="),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("COMMA", r","),
    ("DOT", r"\."),
    ("SEMI", r";"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t\r]+"),
    ("COMMENT", r"\#[^\n]*"),
]


def _tokenize(body: str) -> List[_Tok]:
    master = "|".join(f"(?P<{n}>{p})" for n, p in _TOKEN_SPEC)
    rx = re.compile(master)
    tokens: List[_Tok] = []
    pos = 0
    for m in rx.finditer(body):
        kind = m.lastgroup or "SKIP"
        if kind in ("SKIP", "COMMENT"):
            continue
        tokens.append(_Tok(kind, m.group(), m.start()))
        pos = m.end()
    if pos < len(body.strip()):
        # ignore trailing whitespace only
        rest = body[pos:].strip()
        if rest:
            raise SyntaxError(f"Unexpected shader text near: {rest[:40]!r}")
    tokens.append(_Tok("EOF", "", len(body)))
    return tokens


Expr = Union[
    "Number",
    "Name",
    "Unary",
    "Binary",
    "Call",
    "Swizzle",
]


@dataclass
class Number:
    value: str


@dataclass
class Name:
    value: str


@dataclass
class Unary:
    op: str
    expr: Expr


@dataclass
class Binary:
    op: str
    left: Expr
    right: Expr


@dataclass
class Call:
    name: str
    args: List[Expr]


@dataclass
class Swizzle:
    base: Expr
    fields: str


@dataclass
class LetStmt:
    name: str
    expr: Expr


@dataclass
class AssignStmt:
    name: str
    expr: Expr


@dataclass
class IfStmt:
    cond: Expr
    then_body: List[Union[LetStmt, AssignStmt, "IfStmt"]]
    else_body: List[Union[LetStmt, AssignStmt, "IfStmt"]] = field(default_factory=list)


Stmt = Union[LetStmt, AssignStmt, IfStmt]


class _Parser:
    def __init__(self, tokens: List[_Tok]):
        self.tokens = tokens
        self.i = 0

    def cur(self) -> _Tok:
        return self.tokens[self.i]

    def advance(self) -> _Tok:
        t = self.cur()
        self.i += 1
        return t

    def match(self, kind: str, value: Optional[str] = None) -> bool:
        t = self.cur()
        if t.kind != kind:
            return False
        if value is not None and t.value != value:
            return False
        self.advance()
        return True

    def expect(self, kind: str, value: Optional[str] = None) -> _Tok:
        t = self.cur()
        if t.kind != kind or (value is not None and t.value != value):
            raise SyntaxError(
                f"Shader parse error: expected {kind}"
                + (f" '{value}'" if value else "")
                + f", got {t.kind} '{t.value}'"
            )
        return self.advance()

    def skip_newlines(self) -> None:
        while self.cur().kind == "NEWLINE":
            self.advance()

    def parse_stmts(self) -> List[Stmt]:
        stmts: List[Stmt] = []
        self.skip_newlines()
        while self.cur().kind != "EOF":
            if self.cur().kind == "IDENT" and self.cur().value == "let":
                stmts.append(self.parse_let())
            elif self.cur().kind == "IDENT" and self.cur().value == "if":
                stmts.append(self.parse_if())
            elif self.cur().kind == "IDENT":
                stmts.append(self.parse_assign())
            else:
                raise SyntaxError(
                    f"Shader statement expected, got {self.cur().kind} '{self.cur().value}'"
                )
            self.match("SEMI")
            self.skip_newlines()
        return stmts

    def parse_let(self) -> LetStmt:
        self.expect("IDENT", "let")
        name = self.expect("IDENT").value
        self.expect("ASSIGN")
        expr = self.parse_expr()
        return LetStmt(name, expr)

    def parse_assign(self) -> AssignStmt:
        name = self.expect("IDENT").value
        self.expect("ASSIGN")
        expr = self.parse_expr()
        return AssignStmt(name, expr)

    def parse_if(self) -> IfStmt:
        self.expect("IDENT", "if")
        cond = self.parse_expr()
        # then: either `{ ... }` block or single assign/let until newline
        then_body: List[Stmt] = []
        else_body: List[Stmt] = []
        if self.match("IDENT", "then"):
            pass
        # We use brace blocks for if
        # But our lexer doesn't have braces as tokens in body of if if we
        # already stripped outer braces. Support: if cond { stmts }
        # Need LBRACE - add to lexer... For v1, use single-statement if:
        #   if u > 0.5
        #       color = vec4(1,0,0,1)
        # Optional: else
        self.skip_newlines()
        if self.cur().kind == "IDENT" and self.cur().value == "let":
            then_body.append(self.parse_let())
        else:
            then_body.append(self.parse_assign())
        self.skip_newlines()
        if self.cur().kind == "IDENT" and self.cur().value == "else":
            self.advance()
            self.skip_newlines()
            if self.cur().kind == "IDENT" and self.cur().value == "let":
                else_body.append(self.parse_let())
            else:
                else_body.append(self.parse_assign())
        return IfStmt(cond, then_body, else_body)

    def parse_expr(self) -> Expr:
        return self.parse_compare()

    def parse_compare(self) -> Expr:
        left = self.parse_term()
        while self.cur().kind == "COMPARE":
            op = self.advance().value
            right = self.parse_term()
            left = Binary(op, left, right)
        return left

    def parse_term(self) -> Expr:
        left = self.parse_factor()
        while self.cur().kind == "OP" and self.cur().value in ("+", "-"):
            op = self.advance().value
            right = self.parse_factor()
            left = Binary(op, left, right)
        return left

    def parse_factor(self) -> Expr:
        left = self.parse_unary()
        while self.cur().kind == "OP" and self.cur().value in ("*", "/"):
            op = self.advance().value
            right = self.parse_unary()
            left = Binary(op, left, right)
        return left

    def parse_unary(self) -> Expr:
        if self.cur().kind == "OP" and self.cur().value == "-":
            self.advance()
            return Unary("-", self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self) -> Expr:
        expr = self.parse_primary()
        while self.cur().kind == "DOT":
            self.advance()
            fields = self.expect("IDENT").value
            expr = Swizzle(expr, fields)
        return expr

    def parse_primary(self) -> Expr:
        self.skip_newlines()
        t = self.cur()
        if t.kind == "NUMBER":
            self.advance()
            val = t.value
            if "." not in val:
                val = val + ".0"
            return Number(val)
        if t.kind == "IDENT":
            name = self.advance().value
            if self.match("LPAREN"):
                args: List[Expr] = []
                self.skip_newlines()
                if not self.match("RPAREN"):
                    while True:
                        self.skip_newlines()
                        args.append(self.parse_expr())
                        self.skip_newlines()
                        if self.match("COMMA"):
                            continue
                        self.expect("RPAREN")
                        break
                return Call(name, args)
            return Name(name)
        if self.match("LPAREN"):
            self.skip_newlines()
            expr = self.parse_expr()
            self.skip_newlines()
            self.expect("RPAREN")
            return expr
        raise SyntaxError(f"Shader expression expected, got {t.kind} '{t.value}'")


def parse_shader_body(body: str) -> List[Stmt]:
    return _Parser(_tokenize(body)).parse_stmts()
