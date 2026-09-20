"""Tests for the in-repo Pygments lexer (editors/pygments/flow_lexer.py).

The test is skipped cleanly when Pygments is not installed, so it never breaks
collection of the wider suite.
"""

import os
import sys

import pytest

pytest.importorskip("pygments")

from pygments.token import (  # noqa: E402
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    String,
)

# The lexer lives under editors/pygments, which is not on PYTHONPATH.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_LEXER_DIR = os.path.join(_REPO_ROOT, "editors", "pygments")
if _LEXER_DIR not in sys.path:
    sys.path.insert(0, _LEXER_DIR)

from flow_lexer import FlowLexer  # noqa: E402


SNIPPET = '''\
# a small Flow program
struct Point {
    x: i32,
    y: f64
}

function greet(name: string) -> string {
    let mut count: i32 = 0
    for i in 0 to 10 {
        count = count + 1
    }
    return "hello ${name}"
}
'''


def _tokens(source):
    return list(FlowLexer().get_tokens(source))


def test_lexer_metadata():
    lexer = FlowLexer()
    assert "flow" in lexer.aliases
    assert "*.flow" in lexer.filenames


def test_keywords_tokenize_as_keywords():
    toks = _tokens(SNIPPET)
    values_by_type = {}
    for ttype, value in toks:
        values_by_type.setdefault(ttype, set())
        values_by_type[ttype].add(value)

    # `function` and `struct` are declaration keywords; `let` too.
    assert "function" in values_by_type.get(Keyword.Declaration, set())
    assert "struct" in values_by_type.get(Keyword.Declaration, set())
    assert "let" in values_by_type.get(Keyword.Declaration, set())

    # Control-flow keywords such as `for`/`return` are plain Keyword.
    assert "for" in values_by_type.get(Keyword, set())
    assert "return" in values_by_type.get(Keyword, set())


def test_primitive_types_tokenize_as_types():
    toks = _tokens("let x: i32 = 0\nlet y: f64 = 1.0\nlet p: ptr = null\n")
    type_values = {value for ttype, value in toks if ttype in Keyword.Type}
    assert "i32" in type_values
    assert "f64" in type_values
    assert "ptr" in type_values


def test_comment_tokenizes_as_comment():
    toks = _tokens("# just a comment\n")
    assert any(ttype in Comment and "comment" in value for ttype, value in toks)


def test_string_literal_and_interpolation():
    toks = _tokens('let s: string = "hello ${name}"\n')
    # The quoted text is a String token.
    assert any(ttype in String for ttype, value in toks)
    # The ${...} marker is flagged as interpolation.
    assert any(ttype is String.Interpol for ttype, value in toks)


def test_numbers_and_operators():
    toks = _tokens("let a: i32 = 0xFF\nlet b: f64 = 3.14\nlet c: i32 = 1 + 2\n")
    number_values = {value for ttype, value in toks if ttype in Number}
    assert "0xFF" in number_values
    assert "3.14" in number_values
    assert any(ttype in Operator and value == "+" for ttype, value in toks)


def test_boolean_constants():
    toks = _tokens("let ok: bool = true\nlet no: bool = false\n")
    const_values = {value for ttype, value in toks if ttype is Keyword.Constant}
    assert "true" in const_values
    assert "false" in const_values


def test_attribute_is_decorator():
    toks = _tokens("@rt_safe\nfunction f() -> i32 { return 0 }\n")
    assert any(ttype is Name.Decorator and value == "@rt_safe"
              for ttype, value in toks)
