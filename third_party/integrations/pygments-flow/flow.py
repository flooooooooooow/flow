from pygments.lexer import RegexLexer, bygroups, words
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Text


class FlowLexer(RegexLexer):
    name = "Flow"
    aliases = ["flow"]
    filenames = ["*.flow"]
    mimetypes = ["text/x-flow"]

    _declarations = (
        "function", "let", "mut", "const", "struct", "enum", "effect",
        "capability", "import", "export", "module", "extern", "type",
        "distinct", "trait", "impl", "flow", "state", "param", "unit",
    )

    _control = (
        "if", "elif", "else", "while", "for", "parallel", "in", "to",
        "step", "return", "break", "continue", "defer", "match", "default",
        "handle", "with", "when", "always",
    )

    _types = (
        "i8", "i16", "i32", "i64", "i128", "u8", "u16", "u32", "u64",
        "u128", "f32", "f64", "bool", "string", "void", "array", "ptr",
        "vec", "span",
    )

    tokens = {
        "root": [
            (r"\s+", Text),
            (r"#.*$", Comment.Single),
            (r'"(\\.|[^"\\])*"', String.Double),
            (r"\b0x[0-9A-Fa-f]+\b", Number.Hex),
            (r"\b\d+\.\d+(?:[eE][+-]?\d+)?\b", Number.Float),
            (r"\b\d+(?:[eE][+-]?\d+)?\b", Number.Integer),
            (words(("true", "false", "null"), suffix=r"\b"), Keyword.Constant),
            (words(_declarations, suffix=r"\b"), Keyword.Declaration),
            (words(_control, suffix=r"\b"), Keyword),
            (words(("evolves", "as", "and", "or", "not"), suffix=r"\b"), Keyword),
            (words(_types, suffix=r"\b"), Keyword.Type),
            (r"\b(function)(\s+)([A-Za-z_][A-Za-z0-9_]*)",
             bygroups(Keyword.Declaration, Text, Name.Function)),
            (r"\b(struct|enum|effect|capability|trait)(\s+)([A-Za-z_][A-Za-z0-9_]*)",
             bygroups(Keyword.Declaration, Text, Name.Class)),
            (r"[A-Za-z_][A-Za-z0-9_]*(?=\s*\()", Name.Function),
            (r"[A-Za-z_][A-Za-z0-9_]*", Name),
            (r"\|>|->|=>|::|\.\.|==|!=|<=|>=|&&|\|\||<<|>>|[+\-*/%<>=!&|^~.]", Operator),
            (r"[{}()\[\],:;]", Punctuation),
        ]
    }
