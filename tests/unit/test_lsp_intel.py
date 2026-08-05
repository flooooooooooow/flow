"""LSP intelligence: imports, typed hover, field completion."""

from __future__ import annotations

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SRC = os.path.join(_REPO, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from flow.lsp_server import FlowLanguageServer  # noqa: E402
from flow import lsp_intel  # noqa: E402


def _hover(server, uri, line, col):
    result = server._handle_hover(
        {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": col},
        }
    )
    if result is None:
        return None
    return result["contents"]["value"]


def test_import_symbols_indexed_and_definition():
    main_path = os.path.join(
        _REPO, "examples/packages/use_hello_lib/src/main.flow"
    )
    with open(main_path, encoding="utf-8") as f:
        text = f.read()
    uri = lsp_intel.path_to_uri(main_path)
    server = FlowLanguageServer()
    server.documents[uri] = text
    server._analyze_document(uri)

    assert "add" in server.import_symbols[uri]
    assert "greet" in server.import_symbols[uri]
    info = server.import_symbols[uri]["add"]
    assert info.get("imported")
    assert info.get("uri", "").endswith("lib.flow")

    # Hover on add( at call site
    lines = text.split("\n")
    call_line = next(i for i, row in enumerate(lines) if "add(2, 3)" in row)
    col = lines[call_line].index("add")
    value = _hover(server, uri, call_line, col)
    assert value is not None
    assert "add" in value
    assert "function" in value.lower() or "i32" in value

    loc = server._handle_definition(
        {
            "textDocument": {"uri": uri},
            "position": {"line": call_line, "character": col},
        }
    )
    assert loc is not None
    assert loc["uri"].endswith("lib.flow")


def test_field_completion_after_dot():
    server = FlowLanguageServer()
    uri = "file:///tmp/field_compl.flow"
    text = (
        "struct Point { x: f32, y: f32 }\n"
        "\n"
        "function main() -> f32 {\n"
        "    let p: Point = Point { x: 1.0, y: 2.0 }\n"
        "    return p.\n"
        "}\n"
    )
    server.documents[uri] = text
    server._analyze_document(uri)
    # Cursor after `p.`
    line = 4
    character = text.split("\n")[line].index(".") + 1
    items = server._handle_completion(
        {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": character},
        }
    )
    labels = {it["label"] for it in items}
    assert "x" in labels
    assert "y" in labels


def test_field_hover():
    server = FlowLanguageServer()
    uri = "file:///tmp/field_hover.flow"
    text = (
        "struct Point { x: f32, y: f32 }\n"
        "\n"
        "function main() -> f32 {\n"
        "    let p: Point = Point { x: 1.0, y: 2.0 }\n"
        "    return p.x\n"
        "}\n"
    )
    server.documents[uri] = text
    server._analyze_document(uri)
    line = 4
    col = text.split("\n")[line].index("x")
    value = _hover(server, uri, line, col)
    assert value is not None
    assert "x" in value
    assert "f32" in value
    assert "Point" in value


def test_typed_local_from_checker():
    server = FlowLanguageServer()
    uri = "file:///tmp/infer_local.flow"
    text = (
        "function main() -> i32 {\n"
        "    let n: i32 = 1\n"
        "    let m: i32 = n + 2\n"
        "    return m\n"
        "}\n"
    )
    server.documents[uri] = text
    server._analyze_document(uri)
    # binding for m should be enriched
    binds = [b for b in server.bindings[uri] if b["name"] == "m"]
    assert binds
    assert binds[0]["type"] == "i32"
    line = 3
    import re
    col = re.search(r"\bm\b", text.split("\n")[line]).start()
    value = _hover(server, uri, line, col)
    assert value is not None
    assert "i32" in value


def test_receiver_before_dot_helper():
    text = "    return p.x\n"
    assert lsp_intel.receiver_before_dot(text, 0, len("    return p.")) == "p"
    assert lsp_intel.field_access_at(text, 0, text.index("x")) == ("p", "x")
