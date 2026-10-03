"""Unit tests for the Pygments FlowLexer implementation."""

import pygments
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Token,
)

from src.flow.pygments_lexer import FlowLexer


def test_flow_lexer_metadata():
    lexer = FlowLexer()
    assert lexer.name == "Flow"
    assert "flow" in lexer.aliases
    assert "flow-lang" in lexer.aliases
    assert "*.flow" in lexer.filenames


def test_flow_lexer_keywords_and_types():
    code = "let mut x: i32 = 42;"
    tokens = list(pygments.lex(code, FlowLexer()))
    non_ws_tokens = [(tok, val) for tok, val in tokens if tok != Token.Text.Whitespace]

    expected = [
        (Keyword, "let"),
        (Keyword, "mut"),
        (Name, "x"),
        (Punctuation, ":"),
        (Keyword.Type, "i32"),
        (Operator, "="),
        (Number.Integer, "42"),
        (Punctuation, ";"),
    ]
    assert non_ws_tokens == expected


def test_flow_lexer_fn_declaration():
    code = "fn calculate(a: f64) -> f64 { return a * 2.0; }"
    tokens = list(pygments.lex(code, FlowLexer()))
    non_ws_tokens = [(tok, val) for tok, val in tokens if tok != Token.Text.Whitespace]

    assert (Keyword, "fn") in non_ws_tokens
    assert (Name.Function, "calculate") in non_ws_tokens
    assert (Keyword.Type, "f64") in non_ws_tokens
    assert (Operator, "->") in non_ws_tokens
    assert (Keyword, "return") in non_ws_tokens
    assert (Number.Float, "2.0") in non_ws_tokens


def test_flow_lexer_effects_and_handlers():
    code = """
    effect Console {
        fn log(msg: string) -> void;
    }
    handle Console {
        fn log(msg: string) { print(msg); }
    }
    """
    tokens = list(pygments.lex(code, FlowLexer()))
    non_ws_tokens = [(tok, val) for tok, val in tokens if tok != Token.Text.Whitespace]

    assert (Keyword, "effect") in non_ws_tokens
    assert (Keyword, "handle") in non_ws_tokens
    assert (Keyword.Type, "string") in non_ws_tokens
    assert (Keyword.Type, "void") in non_ws_tokens


def test_flow_lexer_comments_and_strings():
    code = """
    // Single line comment
    /* Multi
       line comment */
    let s: string = "hello \\"world\\"";
    """
    tokens = list(pygments.lex(code, FlowLexer()))
    non_ws_tokens = [(tok, val) for tok, val in tokens if tok != Token.Text.Whitespace]

    assert any(tok == Comment.Single for tok, _ in non_ws_tokens)
    assert any(tok == Comment.Multiline for tok, _ in non_ws_tokens)
    assert any(tok == String for tok, _ in non_ws_tokens)
    assert any(tok == String.Escape for tok, _ in non_ws_tokens)


def test_flow_lexer_attributes_and_constants():
    code = "@rt_safe fn run() { let b: bool = true; let p: ptr<u8> = null; }"
    tokens = list(pygments.lex(code, FlowLexer()))
    non_ws_tokens = [(tok, val) for tok, val in tokens if tok != Token.Text.Whitespace]

    assert (Name.Decorator, "@rt_safe") in non_ws_tokens
    assert (Keyword.Constant, "true") in non_ws_tokens
    assert (Keyword.Constant, "null") in non_ws_tokens
