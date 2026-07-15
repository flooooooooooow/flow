"""Tests for dot-path module resolution and export lists."""

import os
import warnings

import pytest

from flow.module_resolver import ModuleResolver, get_module_resolver
from flow.parser import Lexer, Parser, ImportDecl, ExportDecl
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