"""Unit tests for rich LSP hover (syntax, doc comments, operators)."""

from __future__ import annotations

import os
import sys

# Ensure src/ is importable when running pytest from repo root.
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SRC = os.path.join(_REPO, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from flow.lsp_syntax import (  # noqa: E402
    SYNTAX_HOVER,
    syntax_hover,
    syntax_token_at_position,
)
from flow.lsp_server import FlowLanguageServer  # noqa: E402


def _hover_value(server: FlowLanguageServer, uri: str, line: int, character: int):
    result = server._handle_hover(
        {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": character},
        }
    )
    if result is None:
        return None
    return result["contents"]["value"]


def test_syntax_token_at_position_finds_pipe():
    text = "xs |> sort\n"
    # Cursor on '|', on '>', and on 'sort'
    assert syntax_token_at_position(text, 0, 3) == "|>"
    assert syntax_token_at_position(text, 0, 4) == "|>"
    assert syntax_token_at_position(text, 0, text.index("sort")) == "sort"


def test_syntax_token_at_position_arrows_and_compare():
    text = "function f() -> i32 { return x => x }\n"
    assert syntax_token_at_position(text, 0, text.index("->")) == "->"
    text2 = "if a == b && c != d {}\n"
    assert syntax_token_at_position(text2, 0, text2.index("==")) == "=="
    assert syntax_token_at_position(text2, 0, text2.index("&&")) == "&&"
    assert syntax_token_at_position(text2, 0, text2.index("!=")) == "!="


def test_pipe_hover_returns_pipe_explanation():
    server = FlowLanguageServer()
    uri = "file:///tmp/pipe.flow"
    text = "xs |> sort\n"
    server.documents[uri] = text
    server._analyze_document(uri)

    value = _hover_value(server, uri, 0, 3)
    assert value is not None
    assert "|>" in value
    assert "pipe" in value.lower() or "pipeline" in value.lower() or "sort" in value.lower()


def test_match_hover_non_empty():
    server = FlowLanguageServer()
    uri = "file:///tmp/match.flow"
    text = "function main() -> i32 {\n    match x {\n        default => 0\n    }\n    return 0\n}\n"
    server.documents[uri] = text
    server._analyze_document(uri)

    # Column of 'm' in match
    value = _hover_value(server, uri, 1, 4)
    assert value is not None
    assert len(value.strip()) > 0
    assert "match" in value.lower()


def test_function_doc_comment_appears_in_hover():
    server = FlowLanguageServer()
    uri = "file:///tmp/docfn.flow"
    text = (
        "# Double the input value\n"
        "# Used by tests\n"
        "function double(x: i32) -> i32 {\n"
        "    return x + x\n"
        "}\n"
        "\n"
        "function main() -> i32 {\n"
        "    return double(21)\n"
        "}\n"
    )
    server.documents[uri] = text
    server._analyze_document(uri)

    # Hover on `double` at the call site
    call_line = 7  # 0-based: return double(21)
    col = text.split("\n")[call_line].index("double")
    value = _hover_value(server, uri, call_line, col)
    assert value is not None
    assert "function double" in value
    assert "Double the input value" in value
    assert "Used by tests" in value


def test_export_function_doc_comment():
    server = FlowLanguageServer()
    uri = "file:///tmp/exportdoc.flow"
    text = (
        "# Add two floats\n"
        "export function add(a: f32, b: f32) -> f32 {\n"
        "    return a + b\n"
        "}\n"
    )
    server.documents[uri] = text
    server._analyze_document(uri)
    syms = server.symbols[uri]
    assert "add" in syms
    assert "Add two floats" in (syms["add"].get("doc") or "")


def test_theorem_metadata_in_doc():
    server = FlowLanguageServer()
    lines = [
        "# @means Adding zero on the right is identity.",
        "# @tier derived",
        "# @needs Nat/+.zero-left",
        "theorem Nat/+.zero-right(n: i32) {",
        "    return",
        "}",
    ]
    # Use the helper directly — theorem parse may require a body the checker accepts.
    doc = server._doc_comment_above(lines, 3)
    assert "@means" in doc or "Adding zero" in doc
    assert "@tier" in doc or "derived" in doc
    assert "@needs" in doc or "zero-left" in doc


def test_syntax_hover_catalog_has_core_tokens():
    for tok in ("|>", "->", "=>", "match", "effect", "handle", "@gpu", "f32", "array"):
        assert tok in SYNTAX_HOVER
        assert syntax_hover(tok)


def test_builtin_math_docs_expanded():
    server = FlowLanguageServer()
    for name in ("sin", "cos", "sqrt", "abs", "min", "max", "pow"):
        assert name in server.builtin_functions
        assert server.builtin_functions[name].get("doc")


def test_stdlib_symbols_indexed():
    server = FlowLanguageServer()
    server._ensure_stdlib_indexed()
    # math.flow exports `add` — should win over autodiff's empty `add`.
    assert "add" in server.stdlib_symbols
    info = server.stdlib_symbols["add"]
    assert info["kind"] == "function"
    assert "math.flow" in (info.get("stdlib_path") or "")
    assert "Add two" in (info.get("doc") or "")

    sin = server.stdlib_symbols.get("sin") or {}
    assert "Sine" in (sin.get("doc") or "")


def test_hover_falls_back_to_stdlib():
    server = FlowLanguageServer()
    server._ensure_stdlib_indexed()
    uri = "file:///tmp/empty_main.flow"
    text = (
        "function main() -> f32 {\n"
        "    return add(1.0, 2.0)\n"
        "}\n"
    )
    server.documents[uri] = text
    server._analyze_document(uri)
    # `add` is not defined in this file; hover should use stdlib cache.
    col = text.split("\n")[1].index("add")
    value = _hover_value(server, uri, 1, col)
    assert value is not None
    assert "function add" in value
    assert "Add two" in value


def test_builtin_sin_enriched_from_stdlib_docs():
    server = FlowLanguageServer()
    uri = "file:///tmp/sin_call.flow"
    text = "function main() -> f32 {\n    return sin(0.0)\n}\n"
    server.documents[uri] = text
    server._analyze_document(uri)
    col = text.split("\n")[1].index("sin")
    value = _hover_value(server, uri, 1, col)
    assert value is not None
    assert "sin" in value
    assert "Sine" in value or "radians" in value.lower()


def test_hover_on_let_binding_shows_type():
    server = FlowLanguageServer()
    uri = "file:///tmp/let_hover.flow"
    text = (
        "function main() -> i32 {\n"
        "    let n: i32 = 41\n"
        "    return n + 1\n"
        "}\n"
    )
    server.documents[uri] = text
    server._analyze_document(uri)
    # Hover on `n` in `return n + 1` (not the 'n' inside `return`)
    import re
    row = text.split("\n")[2]
    col = re.search(r"\bn\b", row).start()
    value = _hover_value(server, uri, 2, col)
    assert value is not None
    assert "n" in value
    assert "i32" in value
    assert "let" in value.lower() or "variable" in value.lower()


def test_hover_on_mut_let_and_param():
    server = FlowLanguageServer()
    uri = "file:///tmp/param_hover.flow"
    text = (
        "function add(a: i32, b: i32) -> i32 {\n"
        "    let mut total: i32 = a\n"
        "    total = total + b\n"
        "    return total\n"
        "}\n"
    )
    server.documents[uri] = text
    server._analyze_document(uri)

    # Parameter `a` at use site in initializer (last `a` on the let line)
    col_a = text.split("\n")[1].rindex("a")
    value_a = _hover_value(server, uri, 1, col_a)
    assert value_a is not None
    assert "a" in value_a
    assert "i32" in value_a
    assert "Parameter" in value_a or "parameter" in value_a.lower()

    # mut local `total` at assignment target
    col_t = text.split("\n")[2].index("total")
    value_t = _hover_value(server, uri, 2, col_t)
    assert value_t is not None
    assert "total" in value_t
    assert "mut" in value_t
    assert "i32" in value_t


def test_hover_prefers_binding_over_ordering_catalog():
    """A param named `sort` should show the binding, not ordering docs."""
    server = FlowLanguageServer()
    uri = "file:///tmp/shadow_sort.flow"
    text = (
        "function pick(sort: i32) -> i32 {\n"
        "    return sort\n"
        "}\n"
    )
    server.documents[uri] = text
    server._analyze_document(uri)
    import re
    row = text.split("\n")[1]
    col = re.search(r"\bsort\b", row).start()
    value = _hover_value(server, uri, 1, col)
    assert value is not None
    assert "i32" in value
    assert "Parameter" in value or "parameter" in value.lower()
    assert "sortBy" not in value  # ordering catalog essay


def test_definition_jumps_to_stdlib():
    server = FlowLanguageServer()
    server._ensure_stdlib_indexed()
    uri = "file:///tmp/goto_stdlib.flow"
    text = (
        "function main() -> f32 {\n"
        "    return add(1.0, 2.0)\n"
        "}\n"
    )
    server.documents[uri] = text
    server._analyze_document(uri)
    col = text.split("\n")[1].index("add")
    loc = server._handle_definition(
        {
            "textDocument": {"uri": uri},
            "position": {"line": 1, "character": col},
        }
    )
    assert loc is not None
    assert "uri" in loc
    assert loc["uri"].endswith("math.flow") or "stdlib" in loc["uri"]


def test_completion_includes_stdlib_and_locals():
    server = FlowLanguageServer()
    uri = "file:///tmp/compl.flow"
    text = (
        "function main() -> f32 {\n"
        "    let answer: f32 = 1.0\n"
        "    return an\n"
        "}\n"
    )
    server.documents[uri] = text
    server._analyze_document(uri)
    # Prefix "an" at end of `return an`
    items = server._handle_completion(
        {
            "textDocument": {"uri": uri},
            "position": {"line": 2, "character": text.split("\n")[2].index("an") + 2},
        }
    )
    labels = {it["label"] for it in items}
    assert "answer" in labels
    # stdlib `add` matches prefix when typed further; check abs via "ab"
    items_ab = server._handle_completion(
        {
            "textDocument": {"uri": uri},
            "position": {"line": 2, "character": 11},
        }
    )
    # Force a completion with prefix "ad"
    server.documents[uri] = (
        "function main() -> f32 {\n"
        "    return ad\n"
        "}\n"
    )
    server._analyze_document(uri)
    items_ad = server._handle_completion(
        {
            "textDocument": {"uri": uri},
            "position": {"line": 1, "character": 13},
        }
    )
    labels_ad = {it["label"] for it in items_ad}
    assert "add" in labels_ad


def test_const_and_effect_indexed():
    server = FlowLanguageServer()
    uri = "file:///tmp/const_effect.flow"
    text = (
        "# Gravity\n"
        "export const G: f64 = 9.81\n"
        "\n"
        "effect State {\n"
        "    get() -> i32\n"
        "}\n"
        "\n"
        "function main() -> f64 {\n"
        "    return G\n"
        "}\n"
    )
    server.documents[uri] = text
    server._analyze_document(uri)
    assert "G" in server.symbols[uri]
    assert server.symbols[uri]["G"]["kind"] == "const"
    assert "State" in server.symbols[uri]
    assert server.symbols[uri]["State"]["kind"] == "effect"
    col = text.split("\n")[8].index("G")
    value = _hover_value(server, uri, 8, col)
    assert value is not None
    assert "G" in value
    assert "f64" in value
    assert "Gravity" in value
