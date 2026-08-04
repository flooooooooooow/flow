"""FLOW Shader Language (FSL) — fragment fill shaders.

A small but real shading language embedded in `.flow` files:

```flow
fn palette(t: f32) -> vec3 {
    return vec3(0.5) + vec3(0.5) * cos(6.28318 * (vec3(1.0, 0.7, 0.4) * t + vec3(0.0, 0.15, 0.2)))
}

shader fill plasma {
    let p: vec2 = uv * 2.0 - vec2(1.0)
    let t: f32 = time * 0.4
    var col: vec3 = vec3(0.0)
    for i in 0 to 4 {
        col = col + palette(length(p) + f32(i) * 0.1 + t) * 0.25
    }
    color = vec4(col, 1.0)
}
```

Builtins: `uv`, `time`, `resolution`, `color` (out).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class FillShader:
    name: str
    body: str
    line: int = 1


@dataclass
class ShaderFunc:
    name: str
    params: List[tuple]  # (name, type_str)
    return_type: str
    body: str
    line: int = 1


@dataclass
class ShaderModule:
    funcs: List[ShaderFunc] = field(default_factory=list)
    fills: List[FillShader] = field(default_factory=list)


def _extract_brace_block(source: str, open_brace_index: int) -> tuple:
    """Given index of `{`, return (inner_text, index_after_closing_brace)."""
    assert source[open_brace_index] == "{"
    depth = 0
    i = open_brace_index
    while i < len(source):
        ch = source[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[open_brace_index + 1 : i], i + 1
        i += 1
    raise SyntaxError("Unclosed '{' in shader module")


_FN_HEAD = re.compile(
    r"\bfn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)\s*->\s*([A-Za-z0-9_<>,\s]+)\s*\{",
    re.MULTILINE,
)
_SHADER_HEAD = re.compile(
    r"\bshader\s+fill\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{",
    re.MULTILINE,
)


def _parse_params(raw: str) -> List[tuple]:
    raw = raw.strip()
    if not raw:
        return []
    params = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise SyntaxError(f"Shader fn param needs name: type, got '{part}'")
        name, typ = part.split(":", 1)
        params.append((name.strip(), typ.strip()))
    return params


def extract_shader_module(source: str) -> ShaderModule:
    """Extract top-level `fn` helpers and `shader fill` blocks."""
    mod = ShaderModule()
    # Find all heads with positions, process in order so nested braces work
    events = []
    for m in _FN_HEAD.finditer(source):
        events.append(("fn", m))
    for m in _SHADER_HEAD.finditer(source):
        events.append(("fill", m))
    events.sort(key=lambda e: e[1].start())

    occupied_until = -1
    for kind, m in events:
        if m.start() < occupied_until:
            continue
        brace_at = source.find("{", m.start())
        body, end = _extract_brace_block(source, brace_at)
        occupied_until = end
        line = source.count("\n", 0, m.start()) + 1
        if kind == "fn":
            mod.funcs.append(
                ShaderFunc(
                    name=m.group(1),
                    params=_parse_params(m.group(2)),
                    return_type=m.group(3).strip(),
                    body=body,
                    line=line,
                )
            )
        else:
            mod.fills.append(FillShader(name=m.group(1), body=body, line=line))
    return mod


def extract_fill_shaders(source: str) -> List[FillShader]:
    return extract_shader_module(source).fills


# ── Lexer / parser ──────────────────────────────────────────────────

class _Tok:
    __slots__ = ("kind", "value", "pos")

    def __init__(self, kind: str, value: str, pos: int):
        self.kind = kind
        self.value = value
        self.pos = pos


_TOKEN_SPEC = [
    ("NUMBER", r"\d+\.\d+|\d+\.|\.\d+|\d+"),
    ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP", r"\+|\-|\*|\/|%"),
    ("COMPARE", r"<=|>=|==|!=|<|>"),
    ("AND", r"&&"),
    ("OR", r"\|\|"),
    ("NOT", r"!"),
    ("ASSIGN", r"="),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("COMMA", r","),
    ("COLON", r":"),
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
    for m in rx.finditer(body):
        kind = m.lastgroup or "SKIP"
        if kind in ("SKIP", "COMMENT"):
            continue
        tokens.append(_Tok(kind, m.group(), m.start()))
    tokens.append(_Tok("EOF", "", len(body)))
    return tokens


@dataclass
class Number:
    value: str


@dataclass
class Name:
    value: str


@dataclass
class Unary:
    op: str
    expr: "Expr"


@dataclass
class Binary:
    op: str
    left: "Expr"
    right: "Expr"


@dataclass
class Call:
    name: str
    args: List["Expr"]


@dataclass
class Swizzle:
    base: "Expr"
    fields: str


@dataclass
class Cast:
    typ: str
    expr: "Expr"


Expr = Union[Number, Name, Unary, Binary, Call, Swizzle, Cast]


@dataclass
class LetStmt:
    name: str
    typ: Optional[str]
    expr: Expr
    mutable: bool = False


@dataclass
class AssignStmt:
    name: str
    expr: Expr


@dataclass
class ReturnStmt:
    expr: Optional[Expr]


@dataclass
class IfStmt:
    cond: Expr
    then_body: List["Stmt"]
    else_body: List["Stmt"] = field(default_factory=list)


@dataclass
class ForStmt:
    var: str
    start: Expr
    end: Expr
    body: List["Stmt"]


Stmt = Union[LetStmt, AssignStmt, ReturnStmt, IfStmt, ForStmt]


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

    def skip_nl(self) -> None:
        while self.cur().kind == "NEWLINE":
            self.advance()

    def parse_stmts(self) -> List[Stmt]:
        stmts: List[Stmt] = []
        self.skip_nl()
        while self.cur().kind not in ("EOF", "RBRACE"):
            stmts.append(self.parse_stmt())
            self.match("SEMI")
            self.skip_nl()
        return stmts

    def parse_block(self) -> List[Stmt]:
        self.expect("LBRACE")
        self.skip_nl()
        body = self.parse_stmts()
        self.expect("RBRACE")
        return body

    def parse_stmt(self) -> Stmt:
        self.skip_nl()
        t = self.cur()
        if t.kind == "IDENT" and t.value in ("let", "var"):
            return self.parse_let()
        if t.kind == "IDENT" and t.value == "if":
            return self.parse_if()
        if t.kind == "IDENT" and t.value == "for":
            return self.parse_for()
        if t.kind == "IDENT" and t.value == "return":
            self.advance()
            if self.cur().kind in ("NEWLINE", "SEMI", "RBRACE", "EOF"):
                return ReturnStmt(None)
            return ReturnStmt(self.parse_expr())
        if t.kind == "IDENT":
            return self.parse_assign()
        raise SyntaxError(f"Shader statement expected, got {t.kind} '{t.value}'")

    def parse_let(self) -> LetStmt:
        mut = self.cur().value == "var"
        self.advance()  # let | var
        name = self.expect("IDENT").value
        typ = None
        if self.match("COLON"):
            typ = self.expect("IDENT").value
        self.expect("ASSIGN")
        expr = self.parse_expr()
        return LetStmt(name, typ, expr, mutable=mut)

    def parse_assign(self) -> AssignStmt:
        name = self.expect("IDENT").value
        self.expect("ASSIGN")
        return AssignStmt(name, self.parse_expr())

    def parse_if(self) -> IfStmt:
        self.expect("IDENT", "if")
        cond = self.parse_expr()
        self.skip_nl()
        if self.cur().kind == "LBRACE":
            then_body = self.parse_block()
        else:
            then_body = [self.parse_stmt()]
        self.skip_nl()
        else_body: List[Stmt] = []
        if self.cur().kind == "IDENT" and self.cur().value == "else":
            self.advance()
            self.skip_nl()
            if self.cur().kind == "IDENT" and self.cur().value == "if":
                else_body = [self.parse_if()]
            elif self.cur().kind == "LBRACE":
                else_body = self.parse_block()
            else:
                else_body = [self.parse_stmt()]
        return IfStmt(cond, then_body, else_body)

    def parse_for(self) -> ForStmt:
        # for i in 0 to 10 { ... }
        self.expect("IDENT", "for")
        var = self.expect("IDENT").value
        if not (self.cur().kind == "IDENT" and self.cur().value == "in"):
            raise SyntaxError("Expected 'in' after for variable")
        self.advance()
        start = self.parse_expr()
        if not (self.cur().kind == "IDENT" and self.cur().value == "to"):
            raise SyntaxError("Expected 'to' in for-range")
        self.advance()
        end = self.parse_expr()
        self.skip_nl()
        body = self.parse_block() if self.cur().kind == "LBRACE" else [self.parse_stmt()]
        return ForStmt(var, start, end, body)

    def parse_expr(self) -> Expr:
        return self.parse_or()

    def parse_or(self) -> Expr:
        left = self.parse_and()
        while self.cur().kind == "OR":
            self.advance()
            left = Binary("||", left, self.parse_and())
        return left

    def parse_and(self) -> Expr:
        left = self.parse_compare()
        while self.cur().kind == "AND":
            self.advance()
            left = Binary("&&", left, self.parse_compare())
        return left

    def parse_compare(self) -> Expr:
        left = self.parse_term()
        while self.cur().kind == "COMPARE":
            op = self.advance().value
            left = Binary(op, left, self.parse_term())
        return left

    def parse_term(self) -> Expr:
        left = self.parse_factor()
        while self.cur().kind == "OP" and self.cur().value in ("+", "-"):
            op = self.advance().value
            left = Binary(op, left, self.parse_factor())
        return left

    def parse_factor(self) -> Expr:
        left = self.parse_unary()
        while self.cur().kind == "OP" and self.cur().value in ("*", "/", "%"):
            op = self.advance().value
            left = Binary(op, left, self.parse_unary())
        return left

    def parse_unary(self) -> Expr:
        if self.cur().kind == "OP" and self.cur().value == "-":
            self.advance()
            return Unary("-", self.parse_unary())
        if self.cur().kind == "NOT":
            self.advance()
            return Unary("!", self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self) -> Expr:
        expr = self.parse_primary()
        while self.cur().kind == "DOT":
            self.advance()
            fields = self.expect("IDENT").value
            expr = Swizzle(expr, fields)
        return expr

    def parse_primary(self) -> Expr:
        self.skip_nl()
        t = self.cur()
        if t.kind == "NUMBER":
            self.advance()
            val = t.value
            if "." not in val:
                val = val + ".0"
            return Number(val)
        if t.kind == "IDENT":
            name = self.advance().value
            # cast form: f32(expr) / vec2(...) already via Call
            if self.match("LPAREN"):
                args: List[Expr] = []
                self.skip_nl()
                if not self.match("RPAREN"):
                    while True:
                        self.skip_nl()
                        args.append(self.parse_expr())
                        self.skip_nl()
                        if self.match("COMMA"):
                            continue
                        self.expect("RPAREN")
                        break
                if name in ("f32", "i32", "bool") and len(args) == 1:
                    return Cast(name, args[0])
                return Call(name, args)
            return Name(name)
        if self.match("LPAREN"):
            self.skip_nl()
            expr = self.parse_expr()
            self.skip_nl()
            self.expect("RPAREN")
            return expr
        raise SyntaxError(f"Shader expression expected, got {t.kind} '{t.value}'")


def parse_shader_body(body: str) -> List[Stmt]:
    return _Parser(_tokenize(body)).parse_stmts()
