"""Pygments lexer for the Flow programming language."""

from __future__ import annotations

from pygments.lexer import RegexLexer, bygroups, words
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Whitespace,
)

__all__ = ["FlowLexer"]


class FlowLexer(RegexLexer):
    """Pygments lexer for the Flow programming language."""

    name = "Flow"
    url = "https://github.com/flooooooooooow/flow"
    aliases = ["flow", "flow-lang"]
    filenames = ["*.flow"]
    mimetypes = ["text/x-flow"]

    keywords = (
        "function",
        "fn",
        "let",
        "mut",
        "const",
        "struct",
        "enum",
        "trait",
        "type",
        "alias",
        "capability",
        "effect",
        "dsys",
        "flow",
        "extern",
        "if",
        "else",
        "match",
        "while",
        "for",
        "in",
        "return",
        "break",
        "continue",
        "perform",
        "handle",
        "with",
        "yield",
        "evolves",
        "as",
        "pub",
        "export",
        "import",
        "static",
        "inline",
        "async",
        "await",
        "and",
        "or",
        "not",
    )

    types = (
        "i8",
        "i16",
        "i32",
        "i64",
        "u8",
        "u16",
        "u32",
        "u64",
        "f32",
        "f64",
        "bool",
        "string",
        "str",
        "char",
        "void",
        "unit",
        "ptr",
        "slice",
        "self",
        "Self",
    )

    constants = (
        "true",
        "false",
        "null",
        "nil",
    )

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            (r"#.*$", Comment.Single),
            (r"//.*$", Comment.Single),
            (r"/\*", Comment.Multiline, "comment"),
            (r"@[a-zA-Z_]\w*", Name.Decorator),
            (
                r"\b(fn|function)\b(\s+)([a-zA-Z_]\w*)(?=\s*[\(<])",
                bygroups(Keyword, Whitespace, Name.Function),
            ),
            (
                r"\b(struct|enum|trait|type|alias|effect|capability)\b(\s+)([a-zA-Z_]\w*)(?=\s*[\{:=<])",
                bygroups(Keyword, Whitespace, Name.Class),
            ),
            (words(keywords, prefix=r"\b", suffix=r"\b"), Keyword),
            (words(types, prefix=r"\b", suffix=r"\b"), Keyword.Type),
            (words(constants, prefix=r"\b", suffix=r"\b"), Keyword.Constant),
            (r"0x[0-9a-fA-F_]+", Number.Hex),
            (r"0b[01_]+", Number.Bin),
            (r"0o[0-7_]+", Number.Oct),
            (r"([0-9][0-9_]*\.[0-9][0-9_]*([eE][+-]?[0-9_]+)?|[0-9][0-9_]*[eE][+-]?[0-9_]+)", Number.Float),
            (r"[0-9][0-9_]*", Number.Integer),
            (r'"(\\\\|\\"|[^"])*"', String),
            (r"'(\\\\|\\'|[^'])*'", String.Char),
            (r"->|=>|==|!=|<=|>=|\+=|-=|\*=|/=|%=|::|\.\.|&&|\|\||[+\-*/%=<>&|^~!]", Operator),
            (r"[(){}\[\];,.:]", Punctuation),
            (r"([a-zA-Z_]\w*)(\s*)(\()", bygroups(Name.Function, Whitespace, Punctuation)),
            (r"[A-Z]\w*", Name.Class),
            (r"[a-z_]\w*", Name),
        ],
        "comment": [
            (r"[^*/]+", Comment.Multiline),
            (r"/\*", Comment.Multiline, "#push"),
            (r"\*/", Comment.Multiline, "#pop"),
            (r"[*/]", Comment.Multiline),
        ],
    }
