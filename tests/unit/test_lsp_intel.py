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
    # The hover names the file that defines the imported symbol.
    assert "defined in" in value
    assert "lib.flow" in value

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


def test_hover_defining_file_follows_reexport(tmp_path):
    """A re-exported symbol points at its real definition, not the aggregator."""
    dep = tmp_path / "dep.flow"
    dep.write_text(
        "# The real implementation\n"
        "export function compute(x: i32) -> i32 {\n"
        "    return x * 2\n"
        "}\n",
        encoding="utf-8",
    )
    agg = tmp_path / "agg.flow"
    agg.write_text("export import .dep\n", encoding="utf-8")
    main = tmp_path / "main.flow"
    main.write_text(
        "import .agg\n"
        "function main() -> i32 {\n"
        "    return compute(21)\n"
        "}\n",
        encoding="utf-8",
    )
    uri = lsp_intel.path_to_uri(str(main))
    server = FlowLanguageServer()
    server.documents[uri] = main.read_text(encoding="utf-8")
    server._analyze_document(uri)

    # The import map resolves `compute` to dep.flow, not agg.flow.
    assert "compute" in server.import_symbols[uri]
    assert server.import_symbols[uri]["compute"]["uri"].endswith("dep.flow")

    lines = main.read_text(encoding="utf-8").split("\n")
    col = lines[2].index("compute")
    value = _hover(server, uri, 2, col)
    assert value is not None
    assert "function compute" in value          # exported signature
    assert "defined in" in value
    assert "dep.flow" in value
    assert "agg.flow" not in value


def test_hover_defined_in_not_leaked_by_local_shadow(tmp_path):
    """A local symbol shadowing an imported name gets no defined-in note."""
    dep = tmp_path / "dep.flow"
    dep.write_text(
        "export function compute(x: i32) -> i32 {\n"
        "    return x * 2\n"
        "}\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.flow"
    main.write_text(
        "import .dep\n"
        "function compute(x: i32) -> i32 {\n"
        "    return x + 1\n"
        "}\n"
        "function main() -> i32 {\n"
        "    return compute(1)\n"
        "}\n",
        encoding="utf-8",
    )
    uri = lsp_intel.path_to_uri(str(main))
    server = FlowLanguageServer()
    server.documents[uri] = main.read_text(encoding="utf-8")
    server._analyze_document(uri)

    lines = main.read_text(encoding="utf-8").split("\n")
    # Hover the local definition's call site (line 5: return compute(1)).
    col = lines[5].index("compute")
    value = _hover(server, uri, 5, col)
    assert value is not None
    assert "defined in" not in value  # local wins; no import note


def test_symbol_info_prefers_source_stamp():
    """symbol_info_from_decl trusts the resolver's flow_source_file stamp."""
    from flow.parser import (
        Block,
        FunctionDecl,
        Literal,
        ReturnStatement,
        Type,
    )

    decl = FunctionDecl(
        name="shout",
        parameters=[],
        return_type=Type(name="i32"),
        body=Block(
            statements=[
                ReturnStatement(
                    value=Literal(value="0", type=Type(name="i32"))
                )
            ]
        ),
        attributes=[],
    )
    # Simulate the module resolver stamping the real defining file.
    decl.flow_source_file = "/repo/packages/lib.flow"
    info = lsp_intel.symbol_info_from_decl(
        decl, source_uri="file:///repo/packages/agg.flow"
    )
    assert info is not None
    assert info["uri"].endswith("lib.flow")
    assert "agg.flow" not in info["uri"]


def test_receiver_before_dot_helper():
    text = "    return p.x\n"
    assert lsp_intel.receiver_before_dot(text, 0, len("    return p.")) == "p"
    assert lsp_intel.field_access_at(text, 0, text.index("x")) == ("p", "x")
