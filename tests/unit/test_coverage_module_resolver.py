"""Coverage tests for dashed imports (flow-test-coverage).

Extends tests/unit/test_module_resolver.py with parse and resolution
cases it does not touch: aliases on hyphenated paths, hyphenated
segments in dotted multi-segment paths, the numeric-segment limit,
subtraction coexisting with dashed imports in one file, and resolution
of a hyphenated sibling whose exports are consumed transitively.
"""

import os

import pytest

from flow.module_resolver import get_module_resolver
from flow.parser import FunctionDecl, ImportDecl, Lexer, Parser


FIXTURES = os.path.join(
    os.path.dirname(__file__), "..", "fixtures", "modules"
)


def parse(code: str):
    return Parser(Lexer(code)).parse()


class TestDashedImportParsing:
    def test_alias_on_hyphenated_path(self):
        imp = parse("import verify.Ratio-alternando-lemma as ratio")[0]
        assert imp.path == "verify.Ratio-alternando-lemma"
        assert imp.alias == "ratio"

    def test_hyphenated_segments_in_both_positions(self):
        imp = parse("import proofs-archive.Group-inv-unique")[0]
        assert imp.path == "proofs-archive.Group-inv-unique"

    def test_relative_multi_segment_with_hyphens(self):
        imp = parse("import .Nat-lemmas.plus-assoc { zero-left }")[0]
        assert imp.path == ".Nat-lemmas.plus-assoc"
        assert imp.symbols == ["zero-left"]

    def test_symbol_list_mixes_plain_and_hyphenated_names(self):
        imp = parse("import .Lemmas { plain, multi-part-name, other }")[0]
        assert imp.symbols == ["plain", "multi-part-name", "other"]

    def test_numeric_segment_after_hyphen_is_a_syntax_error(self):
        # Dashed identifiers are IDENT(-IDENT)*; a number after the
        # hyphen is not an identifier. FlowSyntaxError subclasses
        # SyntaxError.
        with pytest.raises(SyntaxError):
            parse("import .Lemma-2")

    def test_import_and_subtraction_coexist_in_one_file(self):
        decls = parse(
            """
import .Group-inv-unique { inv-unique }

function sub(a: i32, b: i32) -> i32 {
    return a - b - 1
}
"""
        )
        assert isinstance(decls[0], ImportDecl)
        assert decls[0].path == ".Group-inv-unique"
        assert isinstance(decls[1], FunctionDecl)
        assert decls[1].name == "sub"


class TestDashedImportResolution:
    def test_hyphenated_sibling_exports_resolve_transitively(self):
        # Multi-hyphen module file plus a hyphenated citation symbol:
        # the consumer sees the sibling's real exported declaration.
        dep = os.path.join(FIXTURES, "Multi-Hyphen-Dep.flow")
        consumer = os.path.join(FIXTURES, "_multi_hyphen_consumer.flow")
        with open(dep, "w", encoding="utf-8") as f:
            f.write(
                "function shared_value() -> i32 {\n"
                "    return 7\n"
                "}\n\n"
                "export shared_value\n"
            )
        with open(consumer, "w", encoding="utf-8") as f:
            f.write(
                "import .Multi-Hyphen-Dep { cited-claim-name }\n\n"
                "function main() -> i32 {\n"
                "    return shared_value() - 7\n"
                "}\n"
            )
        try:
            resolver = get_module_resolver(consumer)
            assert "shared_value" in resolver.symbol_table
            assert resolver.symbol_table["shared_value"].is_exported
        finally:
            for path in (dep, consumer):
                if os.path.exists(path):
                    os.remove(path)

    def test_unexported_symbol_of_hyphenated_sibling_stays_hidden(self):
        dep = os.path.join(FIXTURES, "Hidden-Hyphen-Dep.flow")
        consumer = os.path.join(FIXTURES, "_hidden_hyphen_consumer.flow")
        with open(dep, "w", encoding="utf-8") as f:
            f.write(
                "function public_fn() -> i32 {\n"
                "    return 1\n"
                "}\n\n"
                "function private_fn() -> i32 {\n"
                "    return 2\n"
                "}\n\n"
                "export public_fn\n"
            )
        with open(consumer, "w", encoding="utf-8") as f:
            f.write(
                "import .Hidden-Hyphen-Dep { some-claim }\n\n"
                "function main() -> i32 {\n"
                "    return 0\n"
                "}\n"
            )
        try:
            resolver = get_module_resolver(consumer)
            assert "public_fn" in resolver.symbol_table
            assert "private_fn" not in resolver.symbol_table
        finally:
            for path in (dep, consumer):
                if os.path.exists(path):
                    os.remove(path)
