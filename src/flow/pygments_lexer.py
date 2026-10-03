"""Pygments Lexer for the Flow programming language."""

from pygments.lexer import RegexLexer, words, bygroups
from pygments.token import (
    Comment,
    Operator,
    Keyword,
    Name,
    String,
    Number,
    Punctuation,
    Whitespace,
)

__all__ = ["FlowLexer"]


class FlowLexer(RegexLexer):
    """Lexer for Flow programming language source code."""

    name = "Flow"
    url = "https://flow-lang.org"
    aliases = ["flow", "flow-lang"]
    filenames = ["*.flow"]
    mimetypes = ["text/x-flow", "application/x-flow"]

    KEYWORDS = (
        "fn",
        "let",
        "mut",
        "const",
        "static",
        "struct",
        "enum",
        "type",
        "distinct",
        "effect",
        "capability",
        "handle",
        "perform",
        "trait",
        "impl",
        "if",
        "else",
        "elif",
        "match",
        "while",
        "for",
        "in",
        "to",
        "step",
        "down",
        "return",
        "break",
        "continue",
        "defer",
        "evolves",
        "as",
        "extern",
        "import",
        "export",
        "from",
        "use",
        "module",
        "layout",
        "expect",
        "parallel",
        "dsys",
    )

    BUILTIN_TYPES = (
        "i8",
        "i16",
        "i32",
        "i64",
        "i128",
        "u8",
        "u16",
        "u32",
        "u64",
        "u128",
        "f32",
        "f64",
        "bool",
        "string",
        "void",
        "ptr",
        "span",
        "memref",
        "tensor",
        "vector",
        "index",
    )

    CONSTANTS = ("true", "false", "null")

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            (r"//.*$", Comment.Single),
            (r"/\*", Comment.Multiline, "comment"),
            # Function definitions
            (
                r"(fn)(\s+)([a-zA-Z_]\w*)",
                bygroups(Keyword, Whitespace, Name.Function),
            ),
            (
                words(KEYWORDS, prefix=r"\b", suffix=r"\b"),
                Keyword,
            ),
            (
                words(CONSTANTS, prefix=r"\b", suffix=r"\b"),
                Keyword.Constant,
            ),
            (
                words(BUILTIN_TYPES, prefix=r"\b", suffix=r"\b"),
                Keyword.Type,
            ),
            # Decorators / Attributes
            (r"@[a-zA-Z_]\w*", Name.Decorator),
            # Numbers
            (r"0x[0-9a-fA-F_]+", Number.Hex),
            (r"0b[01_]+", Number.Bin),
            (r"0o[0-7_]+", Number.Oct),
            (r"[0-9][0-9_]*\.[0-9][0-9_]*([eE][+-]?[0-9_]+)?", Number.Float),
            (r"[0-9][0-9_]*[eE][+-]?[0-9_]+", Number.Float),
            (r"[0-9][0-9_]*", Number.Integer),
            # Strings
            (r'"', String, "string"),
            (r"'(\\\\|\\'|[^'\\])'", String.Char),
            # Operators
            (r"(=>|->|==|!=|<=|>=|&&|\|\||<<|>>|\.\.|::)", Operator),
            (r"[+\-*/%&=<>!^|~]", Operator),
            # Punctuation
            (r"[{}()\[\];,.:]", Punctuation),
            # Identifiers
            (r"[a-zA-Z_]\w*", Name),
        ],
        "comment": [
            (r"[^*/]+", Comment.Multiline),
            (r"/\*", Comment.Multiline, "#push"),
            (r"\*/", Comment.Multiline, "#pop"),
            (r"[*/]", Comment.Multiline),
        ],
        "string": [
            (r'[^\\"]+', String),
            (r'\\.', String.Escape),
            (r'"', String, "#pop"),
        ],
    }
