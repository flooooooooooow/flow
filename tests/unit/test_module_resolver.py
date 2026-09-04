"""Tests for dot-path module resolution and export lists."""

import os
import warnings

import pytest

from flow.module_resolver import ModuleResolver, get_module_resolver
from flow.parser import Lexer, Parser, ImportDecl, ExportDecl, OrPattern
from flow.project_config import load_project_config


FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures", "modules")


class TestProjectConfig:
    def test_load_paths_from_flow_toml(self):
        cfg = load_project_config(FIXTURES)
        assert cfg.paths["testlib"] == "testlib"
        assert os.path.isdir(cfg.stdlib_root)


class TestImportParser:
    def test_parse_dot_import_with_braces(self):
        code = 'import verify.nat { nat_zero_add, nat_add_succ }'
        decls = Parser(Lexer(code)).parse()
        assert len(decls) == 1
        imp = decls[0]
        assert isinstance(imp, ImportDecl)
        assert imp.path == "verify.nat"
        assert imp.symbols == ["nat_zero_add", "nat_add_succ"]
        assert not imp.is_legacy_string

    def test_parse_dot_import_single_symbol(self):
        code = "import verify.nat.nat_zero_add"
        imp = Parser(Lexer(code)).parse()[0]
        assert imp.path == "verify.nat.nat_zero_add"
        assert imp.symbols is None

    def test_parse_relative_import(self):
        code = "import .nat_add_zero { nat_add_zero }"
        imp = Parser(Lexer(code)).parse()[0]
        assert imp.path == ".nat_add_zero"
        assert imp.symbols == ["nat_add_zero"]

    def test_parse_hyphenated_module_path(self):
        code = "import .Group-inv-unique { inv-unique }"
        imp = Parser(Lexer(code)).parse()[0]
        assert imp.path == ".Group-inv-unique"
        assert imp.symbols == ["inv-unique"]

    def test_parse_hyphenated_module_path_multi_segment(self):
        code = "import verify.Ratio-alternando-lemma"
        imp = Parser(Lexer(code)).parse()[0]
        assert imp.path == "verify.Ratio-alternando-lemma"

    def test_parse_hyphenated_import_symbol_list(self):
        code = "import .Nat-plus-assoc { zero-left, succ-right }"
        imp = Parser(Lexer(code)).parse()[0]
        assert imp.symbols == ["zero-left", "succ-right"]

    def test_subtraction_still_works_outside_imports(self):
        # Regression guard: hyphen-merging is scoped to import path/symbol
        # parsing only, so ordinary subtraction must be unaffected.
        code = """
function sub(a: i32, b: i32) -> i32 {
    return a - b
}
"""
        decl = Parser(Lexer(code)).parse()[0]
        assert decl.name == "sub"

    def test_parse_operator_suffixed_module_path(self):
        code = "import verify.Nat/+ { zero-left, succ-right }"
        imp = Parser(Lexer(code)).parse()[0]
        assert imp.path == "verify.Nat/+"
        assert imp.symbols == ["zero-left", "succ-right"]

    def test_parse_operator_suffixed_or_morphism(self):
        code = "import verify.Bool/|| { commutes }"
        imp = Parser(Lexer(code)).parse()[0]
        assert imp.path == "verify.Bool/||"

    def test_parse_named_morphism_module_path(self):
        code = "import verify.RingBuffer/fifo { order-kept }"
        imp = Parser(Lexer(code)).parse()[0]
        assert imp.path == "verify.RingBuffer/fifo"

    def test_parse_morphism_with_facet_import(self):
        # Lexer may emit CLAIM_PATH for Domain/op.facet as one token.
        code = "import verify.Nat/+.zero-right"
        imp = Parser(Lexer(code)).parse()[0]
        assert imp.path == "verify.Nat/+.zero-right"

    def test_division_still_works_outside_imports(self):
        code = """
function div(a: i32, b: i32) -> i32 {
    return a / b
}
"""
        decl = Parser(Lexer(code)).parse()[0]
        assert decl.name == "div"


class TestOrStructPatterns:
    def test_parse_struct_or_pattern(self):
        code = """
struct Point { x: i32, y: i32 }
function f(p: Point) -> i32 {
    match p {
        Point(0, y) | Point(1, y) => { return y }
        _ => { return -1 }
    }
}
"""
        decls = Parser(Lexer(code)).parse()
        fn = decls[1]
        arm = fn.body.statements[0].cases[0]
        assert isinstance(arm.pattern, OrPattern)
        assert len(arm.pattern.patterns) == 2

    def test_struct_or_disagreeing_bindings_is_error(self):
        code = """
struct Point { x: i32, y: i32 }
function f(p: Point) -> i32 {
    match p {
        Point(0, y) | Point(1, z) => { return 0 }
        _ => { return -1 }
    }
}
"""
        with pytest.raises(SyntaxError, match="same names"):
            Parser(Lexer(code)).parse()

    def test_parse_import_alias(self):
        code = "import verify.nat as nat"
        imp = Parser(Lexer(code)).parse()[0]
        assert imp.path == "verify.nat"
        assert imp.alias == "nat"

    def test_parse_legacy_string_import(self):
        code = 'import "stdlib/math.flow"'
        imp = Parser(Lexer(code)).parse()[0]
        assert imp.is_legacy_string
        assert imp.path == "stdlib/math.flow"

    def test_parse_export_list(self):
        code = "export greet, secret_helper"
        decl = Parser(Lexer(code)).parse()[0]
        assert isinstance(decl, ExportDecl)
        assert decl.symbols == ["greet", "secret_helper"]

    def test_export_before_function_still_works(self):
        code = """
export function add(a: i32, b: i32) -> i32 {
    return a + b
}
"""
        decl = Parser(Lexer(code)).parse()[0]
        assert decl.is_exported
        assert decl.name == "add"


class TestModuleResolver:
    def test_get_module_resolver(self):
        root = os.path.join(FIXTURES, "consumer_dot.flow")
        resolver = get_module_resolver(root)
        assert isinstance(resolver, ModuleResolver)
        assert resolver.root_file == os.path.abspath(root)
        assert len(resolver.modules) > 0
        assert "greet" in resolver.symbol_table

    def test_resolve_modules(self):
        from flow.module_resolver import resolve_modules
        root = os.path.join(FIXTURES, "consumer_dot.flow")
        decls = resolve_modules(root)
        assert isinstance(decls, list)
        assert len(decls) > 0

    def test_resolve_dot_import_with_braces(self):
        root = os.path.join(FIXTURES, "consumer_brace.flow")
        resolver = get_module_resolver(root)
        assert "greet" in resolver.symbol_table
        assert resolver.symbol_table["greet"].is_exported
        assert "secret_helper" not in resolver.symbol_table

    def test_resolve_dot_import_single_symbol_path(self):
        root = os.path.join(FIXTURES, "consumer_dot.flow")
        resolver = get_module_resolver(root)
        assert "greet" in resolver.symbol_table

    def test_resolve_relative_sibling_import(self):
        root = os.path.join(FIXTURES, "consumer_sibling.flow")
        resolver = get_module_resolver(root)
        assert "greet" in resolver.symbol_table

    def test_resolve_std_math(self):
        root = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "basics", "hello_world.flow")
        if not os.path.exists(root):
            pytest.skip("hello_world.flow missing")
        # Smoke: project config loads from repo flow.toml
        cfg = load_project_config(root)
        assert "verify" in cfg.paths

    def test_legacy_import_emits_deprecation_warning(self):
        code = """
import "testlib/greeter.flow"

function main() -> i32 {
    return 0
}
"""
        fixture = os.path.join(FIXTURES, "_legacy_consumer.flow")
        with open(fixture, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                get_module_resolver(fixture)
            assert any(
                issubclass(w.category, DeprecationWarning) for w in caught
            )
        finally:
            if os.path.exists(fixture):
                os.remove(fixture)

    def test_hyphenated_citation_import_does_not_require_matching_symbol(self):
        """`import .Sibling-Proof { some-claim }` style citations (used by the
        flow-verify corpus to document a dependency on a sibling proof file)
        should resolve even though no declaration is actually named
        `missing-symbol` (declaration names can never contain hyphens; the
        sibling's real exports are pulled in transitively regardless)."""
        dep = os.path.join(FIXTURES, "Hyphen-Dep-Sibling.flow")
        consumer = os.path.join(FIXTURES, "_hyphen_consumer.flow")
        with open(dep, "w", encoding="utf-8") as f:
            f.write(
                "function helper() -> i32 {\n"
                "    return 1\n"
                "}\n\n"
                "export helper\n"
            )
        with open(consumer, "w", encoding="utf-8") as f:
            f.write(
                "import .Hyphen-Dep-Sibling { missing-symbol }\n\n"
                "function main() -> i32 {\n"
                "    return 0\n"
                "}\n"
            )
        try:
            resolver = get_module_resolver(consumer)
            assert "helper" in resolver.symbol_table
        finally:
            for path in (dep, consumer):
                if os.path.exists(path):
                    os.remove(path)

    def test_import_non_exported_symbol_fails(self):
        code = """
import testlib.greeter { secret_helper }

function main() -> i32 {
    return secret_helper()
}
"""
        fixture = os.path.join(FIXTURES, "_bad_import.flow")
        with open(fixture, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            with pytest.raises(ValueError, match="not exported"):
                get_module_resolver(fixture)
        finally:
            if os.path.exists(fixture):
                os.remove(fixture)

    def test_resolve_operator_suffixed_verify_nat_plus(self):
        """`import verify.Nat/+ { zero-left }` → lib/verify/Nat.flow."""
        repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        nat = os.path.join(repo, "lib", "verify", "Nat.flow")
        order = os.path.join(repo, "lib", "verify", "Nat-order.flow")
        if not os.path.exists(nat) or not os.path.exists(order):
            pytest.skip("lib/verify Nat modules missing")
        # Resolve from a real repo file so flow.toml [paths].verify applies.
        resolver = get_module_resolver(order)
        assert os.path.abspath(nat) in resolver.modules

    def test_verify_citation_import_allows_missing_plain_facet(self):
        """Non-hyphenated facet citations in examples/verify/ are allowed."""
        repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        consumer = os.path.join(
            repo, "examples", "verify", "math", "derived", "Nat-plus-succ-left.flow"
        )
        if not os.path.exists(consumer):
            pytest.skip("Nat-plus-succ-left.flow missing")
        resolver = get_module_resolver(consumer)
        assert resolver.modules  # resolves despite `{ commutes }` citation

class TestModuleBlockFlattening:
    """`module X { ... }` is flattened; the block name is discarded.

    Guards the behavior documented in docs/language/modules-namespacing.md so
    the design note stays accurate. Change these and change that note.
    """

    def test_module_block_declarations_become_globals(self):
        from flow.module_resolver import flatten_module_declarations

        code = """
module audio {
    function gain() -> i32 {
        return 1
    }
}
"""
        decls = flatten_module_declarations(Parser(Lexer(code)).parse())
        assert [getattr(d, "name", None) for d in decls] == ["gain"]

    def test_two_blocks_may_declare_the_same_name(self):
        from flow.module_resolver import flatten_module_declarations

        code = """
module audio {
    function gain() -> i32 {
        return 1
    }
}

module video {
    function gain() -> i32 {
        return 2
    }
}
"""
        decls = flatten_module_declarations(Parser(Lexer(code)).parse())
        # Both survive flattening, so the C backend emits a redefinition.
        assert [getattr(d, "name", None) for d in decls] == ["gain", "gain"]

    def test_symbol_inside_a_block_is_not_importable(self, tmp_path):
        lib = tmp_path / "nsmod.flow"
        lib.write_text(
            "module inner {\n"
            "    function helper() -> i32 {\n"
            "        return 42\n"
            "    }\n"
            "}\n\n"
            "export inner\n",
            encoding="utf-8",
        )
        consumer = tmp_path / "use.flow"
        consumer.write_text(
            "import .nsmod { helper }\n\n"
            "function main() -> i32 {\n"
            "    return helper()\n"
            "}\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="has no symbol 'helper'"):
            get_module_resolver(str(consumer))

    def test_import_inside_a_block_is_never_resolved(self, tmp_path):
        sibling = tmp_path / "alpha.flow"
        sibling.write_text(
            "export function alpha_one() -> i32 {\n    return 1\n}\n", encoding="utf-8"
        )
        root = tmp_path / "root.flow"
        root.write_text(
            "module m {\n"
            "    import .alpha\n\n"
            "    function use_it() -> i32 {\n"
            "        return alpha_one()\n"
            "    }\n"
            "}\n",
            encoding="utf-8",
        )
        resolver = get_module_resolver(str(root))
        # The nested import never becomes a dependency edge.
        assert resolver.get_module_dependencies(str(root)) == []

    @pytest.mark.parametrize(
        "body",
        [
            "export function f() -> i32 { return 1 }",
            "let mut s: i32 = 0",
            "module b { function f() -> i32 { return 1 } }",
        ],
    )
    def test_block_rejects_most_declaration_forms(self, body):
        code = "module a {\n    " + body + "\n}"
        with pytest.raises(SyntaxError, match="Unexpected declaration inside module"):
            Parser(Lexer(code)).parse()

    def test_resolve_modules(self, tmp_path):
        from flow.module_resolver import resolve_modules

        code = """
module audio {
    function gain() -> i32 {
        return 1
    }
}
function video() -> i32 {
    return 2
}
"""
        root = tmp_path / "root.flow"
        root.write_text(code, encoding="utf-8")

        decls = resolve_modules(str(root))

        assert len(decls) == 2
        assert [getattr(d, "name", None) for d in decls] == ["gain", "video"]



class TestSelfImport:
    def test_root_package_self_import(self):
        code_path = os.path.join(FIXTURES, "self_import.flow")
        resolver = get_module_resolver(code_path)
        
        info = resolver.get_module_info(os.path.join(FIXTURES, "foo.flow"))
        assert info is not None
        assert "self_hello" in info.symbols
