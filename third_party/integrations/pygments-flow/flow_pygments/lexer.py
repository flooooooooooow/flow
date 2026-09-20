from pygments.lexer import RegexLexer, bygroups, words
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Text


class FlowLexer(RegexLexer):
    """Pygments lexer for the Flow programming language."""

    name = "Flow"
    aliases = ["flow", "flowlang"]
    filenames = ["*.flow"]
    mimetypes = ["text/x-flow"]

    _declarations = (
        "function", "struct", "enum", "type", "trait", "impl", "effect",
        "capability", "extern", "const", "flow", "state", "param", "solver",
        "import", "module", "export", "theorem", "assume", "shader",
    )

    _control = (
        "if", "elif", "else", "while", "for", "in", "to", "step", "parallel",
        "return", "match", "default", "handle", "with", "break", "continue",
        "when", "always", "every", "evolves", "as",
    )

    _operators = ("and", "or", "not")

    _types = (
        "i8", "i16", "i32", "i64", "i128",
        "u8", "u16", "u32", "u64", "u128",
        "f32", "f64", "bool", "string", "void",
        "array", "ptr", "vec",
    )

    tokens = {
        "root": [
            (r"\s+", Text.Whitespace),
            (r"#.*$", Comment.Single),
            (r'"(?:\\.|[^"\\])*"', String.Double),
            (words(_declarations, prefix=r"\b", suffix=r"\b"), Keyword.Declaration),
            (words(_control, prefix=r"\b", suffix=r"\b"), Keyword),
            (words(_operators, prefix=r"\b", suffix=r"\b"), Operator.Word),
            (words(_types, prefix=r"\b", suffix=r"\b"), Keyword.Type),
            (words(("true", "false", "null"), prefix=r"\b", suffix=r"\b"), Keyword.Constant),
            (r"@[A-Za-z_][A-Za-z0-9_]*", Name.Decorator),
            (
                r"(function)(\s+)([A-Za-z_][A-Za-z0-9_]*)",
                bygroups(Keyword.Declaration, Text.Whitespace, Name.Function),
            ),
            (
                r"(struct|enum|type|trait|effect|capability|flow)(\s+)([A-Za-z_][A-Za-z0-9_]*)",
                bygroups(Keyword.Declaration, Text.Whitespace, Name.Class),
            ),
            (r"0x[0-9A-Fa-f]+", Number.Hex),
            (r"[0-9][0-9_]*\.[0-9][0-9_]*(?:[eE][+-]?[0-9][0-9_]*)?", Number.Float),
            (r"[0-9][0-9_]*(?:[eE][+-]?[0-9][0-9_]*)", Number.Float),
            (r"[0-9][0-9_]*", Number.Integer),
            (r"\|>|->|=>|==|!=|<=|>=|<<|>>|\+=|-=|\*=|/=|%=|\.\.", Operator),
            (r"[+\-*/%=&|^~!<>]", Operator),
            (r"[{}()\[\],.:;]", Punctuation),
            (r"[A-Za-z_][A-Za-z0-9_]*(?=\s*\()", Name.Function),
            (r"[A-Za-z_][A-Za-z0-9_]*", Name),
        ]
    }
