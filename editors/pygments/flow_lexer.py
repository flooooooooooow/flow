"""Pygments lexer for the Flow programming language.

Flow is a systems language with an effect system, a self-hosting compiler, and
a `#` line-comment syntax. This lexer follows the real lexical surface defined
by the self-hosted lexer in ``compiler/src/lexer.flow`` and the keyword table in
``compiler/src/token.flow``, cross-checked against ``docs/language/syntax.md``.

Distribution note: this is an in-repo lexer. Per Pygments' contribution guide, a
brand-new language should ship as a plugin until it has a sizable community, so
this file is the plugin source rather than an upstream submission.
"""

from pygments.lexer import RegexLexer, bygroups, include, words
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
    """Lexer for Flow source (``*.flow``)."""

    name = "Flow"
    aliases = ["flow"]
    filenames = ["*.flow"]
    mimetypes = ["text/x-flow"]

    # Declaration and definition keywords.
    _declaration_keywords = (
        "function", "let", "mut", "const", "struct", "enum", "type",
        "trait", "impl", "extern", "import", "export", "effect",
        "capability", "unit",
    )

    # Control flow and statement keywords.
    _keywords = (
        "if", "elif", "else", "while", "for", "in", "to", "return",
        "match", "break", "continue", "defer", "handle", "with",
        "parallel", "test", "dbg", "expect", "default", "shader",
    )

    # Literal keywords.
    _constants = ("true", "false", "null")

    # Word-shaped operators.
    _word_operators = ("and", "or", "not", "as")

    # Primitive and built-in types.
    _types = (
        "i8", "i16", "i32", "i64", "i128",
        "u8", "u16", "u32", "u64", "u128",
        "f32", "f64", "bool", "string", "span", "ptr",
    )

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            # Line comments start with '#' and run to end of line.
            (r"#[^\n]*", Comment.Single),

            # Attributes such as @lifetime, @rt_safe, @module.
            (r"@[A-Za-z_][A-Za-z0-9_]*", Name.Decorator),

            # Strings, with ${...} interpolation.
            (r'"', String, "string"),

            # A function definition name, before the bare keyword rule.
            (r"(function)(\s+)([A-Za-z_][A-Za-z0-9_]*)",
             bygroups(Keyword.Declaration, Whitespace, Name.Function)),

            # Word operators before general keywords so precedence is explicit.
            (words(_word_operators, prefix=r"\b", suffix=r"\b"), Operator.Word),
            (words(_constants, prefix=r"\b", suffix=r"\b"), Keyword.Constant),
            (words(_types, prefix=r"\b", suffix=r"\b"), Keyword.Type),
            (words(_declaration_keywords, prefix=r"\b", suffix=r"\b"),
             Keyword.Declaration),
            (words(_keywords, prefix=r"\b", suffix=r"\b"), Keyword),

            # Numbers: hex, float (with exponent), then integer.
            (r"0[xX][0-9A-Fa-f]+", Number.Hex),
            (r"[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?", Number.Float),
            (r"[0-9]+[eE][+-]?[0-9]+", Number.Float),
            (r"[0-9]+", Number.Integer),

            # Multi-character operators before single-character ones.
            (r"->|=>|\|>|<<|>>|==|!=|<=|>=|&&|\|\||"
             r"\+=|-=|\*=|/=|%=|\.\.", Operator),
            (r"[+\-*/%=<>!&|\^~]", Operator),

            # Punctuation.
            (r"[()\[\]{}:;,.]", Punctuation),

            # Identifiers.
            (r"[A-Za-z_][A-Za-z0-9_]*", Name),
        ],
        "string": [
            (r'"', String, "#pop"),
            (r"\\.", String.Escape),
            # $${ is a literal ${ (escaped interpolation).
            (r"\$\$\{", String),
            (r"\$\{", String.Interpol, "interp"),
            (r"[^\"\\$]+", String),
            (r"\$", String),
        ],
        "interp": [
            (r"\}", String.Interpol, "#pop"),
            include("root"),
        ],
    }
