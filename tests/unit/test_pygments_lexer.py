import pytest
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
    Whitespace,
)

from flow.pygments_lexer import FlowLexer


def test_flow_lexer_direct_instantiation() -> None:
    lexer = FlowLexer()
    assert lexer.name == "Flow"
    assert "flow" in lexer.aliases
    assert "flow-lang" in lexer.aliases
    assert "*.flow" in lexer.filenames


def test_flow_lexer_entry_point_discovery() -> None:
    lexer_by_flow = get_lexer_by_name("flow")
    assert isinstance(lexer_by_flow, FlowLexer)

    lexer_by_alias = get_lexer_by_name("flow-lang")
    assert isinstance(lexer_by_alias, FlowLexer)

    lexer_by_filename = get_lexer_for_filename("main.flow")
    assert isinstance(lexer_by_filename, FlowLexer)


def test_flow_lexer_tokenizes_keywords() -> None:
    lexer = FlowLexer()
    code = "function fn let mut const struct enum trait type capability effect dsys flow extern if else match while for in return perform handle evolves as"
    tokens = list(lexer.get_tokens(code))
    keywords_found = [text for tok, text in tokens if tok is Keyword]
    expected_keywords = [
        "function",
        "fn",
        "let",
        "mut",
        "const",
        "struct",
        "enum",
        "trait",
        "type",
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
        "perform",
        "handle",
        "evolves",
        "as",
    ]
    for kw in expected_keywords:
        assert kw in keywords_found


def test_flow_lexer_tokenizes_types_and_constants() -> None:
    lexer = FlowLexer()
    code = "let x: i32 = 42\nlet y: f64 = 3.14\nlet flag: bool = true\nlet ptr_val: ptr = null"
    tokens = list(lexer.get_tokens(code))

    types_found = [text for tok, text in tokens if tok is Keyword.Type]
    assert "i32" in types_found
    assert "f64" in types_found
    assert "bool" in types_found
    assert "ptr" in types_found

    constants_found = [text for tok, text in tokens if tok is Keyword.Constant]
    assert "true" in constants_found
    assert "null" in constants_found


def test_flow_lexer_tokenizes_decorators() -> None:
    lexer = FlowLexer()
    code = "@rt_safe\n@inline\nfunction foo() -> void {}"
    tokens = list(lexer.get_tokens(code))

    decorators = [text for tok, text in tokens if tok is Name.Decorator]
    assert "@rt_safe" in decorators
    assert "@inline" in decorators


def test_flow_lexer_tokenizes_numbers() -> None:
    lexer = FlowLexer()
    code = "123 0xDEADBEEF 0b1010 0o755 3.14159 1e-10"
    tokens = list(lexer.get_tokens(code))

    nums = [(tok, text) for tok, text in tokens if tok in (Number.Integer, Number.Hex, Number.Bin, Number.Oct, Number.Float)]
    tok_map = {text: tok for tok, text in nums}

    assert tok_map.get("123") == Number.Integer
    assert tok_map.get("0xDEADBEEF") == Number.Hex
    assert tok_map.get("0b1010") == Number.Bin
    assert tok_map.get("0o755") == Number.Oct
    assert tok_map.get("3.14159") == Number.Float
    assert tok_map.get("1e-10") == Number.Float


def test_flow_lexer_tokenizes_comments() -> None:
    lexer = FlowLexer()
    code = "# single line hash\n// single line slash\n/* multi line\n   comment */"
    tokens = list(lexer.get_tokens(code))

    comments = [text for tok, text in tokens if tok in (Comment.Single, Comment.Multiline)]
    joined_comments = "".join(comments)
    assert "# single line hash" in joined_comments
    assert "// single line slash" in joined_comments
    assert "multi line" in joined_comments


def test_flow_lexer_tokenizes_strings() -> None:
    lexer = FlowLexer()
    code = '"hello world" \'a\''
    tokens = list(lexer.get_tokens(code))

    strings = [text for tok, text in tokens if tok in (String, String.Char)]
    assert '"hello world"' in strings
    assert "'a'" in strings


def test_flow_lexer_tokenizes_complete_function() -> None:
    lexer = FlowLexer()
    code = """
struct Point {
    x: f64,
    y: f64,
}

@rt_safe
function distance(p: Point) -> f64 {
    let mut d = p.x * p.x + p.y * p.y
    return d
}
"""
    tokens = list(lexer.get_tokens(code))

    token_types = [tok for tok, text in tokens if tok not in (Whitespace, Text)]
    assert Keyword in token_types
    assert Name.Class in token_types
    assert Keyword.Type in token_types
    assert Name.Decorator in token_types
    assert Name.Function in token_types
    assert Operator in token_types
    assert Punctuation in token_types
