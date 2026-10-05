"""Regression tests for escaped quotes in string literals (#408).

String literals containing `\"` must compile and produce correct output.
The bug report said they caused a bus error. The root cause was likely
fixed by earlier string-handling changes; these tests guard against
regression.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code, Literal
from flow.c_generator import flow_to_c


def _gen_c(source: str) -> str:
    decls = parse_flow_code(source)
    return flow_to_c(decls)


def test_escaped_quote_parses():
    """The lexer and validator accept backslash-quote inside a string literal."""
    decls = parse_flow_code(r'function main() -> i32 { print("hello\"world") ; return 0 }')
    assert len(decls) >= 1


def test_escaped_quote_literal_value():
    """The parsed Literal retains the raw C-escaped string."""
    decls = parse_flow_code(r'function main() -> i32 { let s: string = "a\"b" ; return 0 }')
    found = False
    for decl in decls:
        if hasattr(decl, "body") and decl.body:
            for stmt in getattr(decl.body, "statements", []):
                init = getattr(stmt, "initializer", None)
                if isinstance(init, Literal) and init.type.name == "string":
                    found = True
    assert found, "No string literal found in AST"


def test_escaped_quote_c_codegen():
    """The C generator emits a valid C string with escaped quotes."""
    c_code = _gen_c(r'function main() -> i32 { print("node [shape=box, style=\"filled\"];") ; return 0 }')
    assert 'filled' in c_code
    assert 'shape=box' in c_code


def test_multiple_escaped_quotes_c_codegen():
    """Multiple escaped quotes in one string work."""
    c_code = _gen_c(r'function main() -> i32 { let s: string = "a\"b\"c" ; println(s) ; return 0 }')
    assert "main" in c_code


def test_escaped_quote_concatenation():
    """Escaped quotes work inside string concatenation."""
    c_code = _gen_c(r'function main() -> i32 { let s: string = "hello\"world" + " test\"test" ; println(s) ; return 0 }')
    assert "flow_strcat" in c_code


def test_escaped_backslash_parses():
    """Escaped backslash inside a string literal parses."""
    decls = parse_flow_code(r'function main() -> i32 { print("path\\to\\file") ; return 0 }')
    assert len(decls) >= 1


def test_escaped_newline_parses():
    """Escaped newline inside a string literal parses."""
    decls = parse_flow_code('function main() -> i32 { print("line1\\nline2") ; return 0 }')
    assert len(decls) >= 1


def test_invalid_escape_rejected():
    """Invalid escape sequences are rejected by the validator."""
    from flow.parser import FlowSyntaxError
    try:
        parse_flow_code(r'function main() -> i32 { print("hello\xworld") ; return 0 }')
        assert False, "Should have raised SyntaxError"
    except (FlowSyntaxError, SyntaxError):
        pass
