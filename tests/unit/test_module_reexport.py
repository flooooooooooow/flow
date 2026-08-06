"""Tests for `export import` re-export.

`export import <module>` forwards every symbol that module exports;
`export import <module> { a, b }` forwards a selection. See
docs/language/modules.md.
"""

import os
import shutil
import subprocess
import sys
import textwrap

import pytest

from flow.module_resolver import (
    ModuleResolver,
    SymbolCollisionError,
    get_module_resolver,
    resolve_modules,
)
from flow.parser import ImportDecl, Lexer, Parser


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FIXTURES = os.path.join(REPO_ROOT, "tests", "fixtures", "modules")
TESTLIB = os.path.join(FIXTURES, "testlib")


def _fixture(name):
    return os.path.join(FIXTURES, name)


def _write_package(root, files):
    """Write a throwaway package: flow.toml with a `testlib` path root."""
    os.makedirs(os.path.join(root, "testlib"), exist_ok=True)
    with open(os.path.join(root, "flow.toml"), "w", encoding="utf-8") as f:
        f.write(
            '[package]\nname = "reexport-fixtures"\nversion = "0.0.1"\n\n'
            '[paths]\ntestlib = "testlib"\n'
        )
    for rel, body in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(body).lstrip())
    return root


class TestReexportParsing:
    def test_export_import_sets_reexport_flag(self):
        imp = Parser(Lexer("export import .alpha")).parse()[0]
        assert isinstance(imp, ImportDecl)
        assert imp.path == ".alpha"
        assert imp.is_reexport
        assert imp.symbols is None

    def test_export_import_with_selection(self):
        imp = Parser(Lexer("export import testlib.beta { beta_one }")).parse()[0]
        assert imp.is_reexport
        assert imp.symbols == ["beta_one"]

    def test_plain_import_is_not_a_reexport(self):
        imp = Parser(Lexer("import .alpha")).parse()[0]
        assert not imp.is_reexport

    def test_export_import_legacy_string_path(self):
        imp = Parser(Lexer('export import "testlib/alpha.flow"')).parse()[0]
        assert imp.is_reexport
        assert imp.is_legacy_string
        assert imp.path == "testlib/alpha.flow"

    def test_export_import_as_alias_is_rejected(self):
        with pytest.raises(SyntaxError, match="not supported"):
            Parser(Lexer("export import testlib.alpha as a")).parse()


class TestReexportResolution:
    def test_reexport_all_forwards_every_export(self):
        resolver = get_module_resolver(_fixture("consumer_reexport.flow"))
        agg = os.path.join(TESTLIB, "agg.flow")
        assert sorted(resolver.list_exported_symbols(agg)) == [
            "agg_own",
            "alpha_one",
            "alpha_two",
            "beta_one",
        ]

    def test_reexport_does_not_forward_private_symbols(self):
        resolver = get_module_resolver(_fixture("consumer_reexport.flow"))
        agg = os.path.join(TESTLIB, "agg.flow")
        assert "alpha_private" not in resolver.get_module_info(agg).symbols

    def test_selection_forwards_only_the_named_symbols(self):
        resolver = get_module_resolver(_fixture("consumer_reexport.flow"))
        agg_syms = resolver.get_module_info(os.path.join(TESTLIB, "agg.flow")).symbols
        assert "beta_one" in agg_syms
        # beta.flow exports beta_two as well; agg.flow forwarded only beta_one.
        assert "beta_two" not in agg_syms

    def test_forwarded_symbol_keeps_its_declaring_file(self):
        resolver = get_module_resolver(_fixture("consumer_reexport.flow"))
        sym = resolver.get_module_info(os.path.join(TESTLIB, "agg.flow")).symbols[
            "alpha_one"
        ]
        assert sym.source_file == os.path.join(TESTLIB, "alpha.flow")
        assert sym.is_exported

    def test_reexports_map_records_the_origin(self):
        resolver = get_module_resolver(_fixture("consumer_reexport.flow"))
        reexports = resolver.get_module_info(
            os.path.join(TESTLIB, "agg.flow")
        ).reexports
        assert reexports["alpha_one"] == os.path.join(TESTLIB, "alpha.flow")
        assert reexports["beta_one"] == os.path.join(TESTLIB, "beta.flow")
        assert "agg_own" not in reexports

    def test_reexport_chains(self):
        resolver = get_module_resolver(_fixture("consumer_reexport_chain.flow"))
        chain = os.path.join(TESTLIB, "agg_chain.flow")
        assert sorted(resolver.list_exported_symbols(chain)) == [
            "agg_own",
            "alpha_one",
            "alpha_two",
            "beta_one",
        ]


class TestConsumerVisibility:
    def test_consumer_imports_forwarded_symbols_by_the_aggregator_name(self):
        # consumer_reexport.flow: import testlib.agg { alpha_one, ... }
        resolver = get_module_resolver(_fixture("consumer_reexport.flow"))
        for name in ("alpha_one", "alpha_two", "beta_one", "agg_own"):
            assert name in resolver.symbol_table

    def test_consumer_cannot_import_an_unforwarded_symbol(self, tmp_path):
        root = _write_package(
            str(tmp_path),
            {
                "testlib/beta.flow": """
                    export function beta_one() -> i32 { return 10 }
                    export function beta_two() -> i32 { return 20 }
                """,
                "testlib/agg.flow": "export import .beta { beta_one }\n",
                "main.flow": """
                    import testlib.agg { beta_two }
                    function main() -> i32 { return beta_two() }
                """,
            },
        )
        with pytest.raises(ValueError, match="has no symbol 'beta_two'"):
            get_module_resolver(os.path.join(root, "main.flow"))

    def test_plain_import_does_not_forward(self, tmp_path):
        # Same shape, but the aggregator uses a plain `import`.
        root = _write_package(
            str(tmp_path),
            {
                "testlib/beta.flow": "export function beta_one() -> i32 { return 10 }\n",
                "testlib/agg.flow": "import .beta\n",
                "main.flow": """
                    import testlib.agg { beta_one }
                    function main() -> i32 { return beta_one() }
                """,
            },
        )
        with pytest.raises(ValueError, match="has no symbol 'beta_one'"):
            get_module_resolver(os.path.join(root, "main.flow"))


class TestNoDuplicateEmission:
    def test_declaration_list_has_one_entry_per_symbol(self):
        decls = resolve_modules(_fixture("consumer_reexport.flow"))
        names = [getattr(d, "name", None) for d in decls]
        for name in ("alpha_one", "alpha_two", "beta_one", "agg_own"):
            assert names.count(name) == 1

    def test_chained_reexport_does_not_duplicate(self):
        decls = resolve_modules(_fixture("consumer_reexport_chain.flow"))
        names = [getattr(d, "name", None) for d in decls]
        assert names.count("alpha_one") == 1
        assert names.count("beta_one") == 1

    def test_generated_c_defines_each_function_once(self, tmp_path):
        c_file = tmp_path / "out.c"
        env = dict(os.environ)
        env["PYTHONPATH"] = os.path.join(REPO_ROOT, "src") + os.pathsep + env.get(
            "PYTHONPATH", ""
        )
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "flow.transpiler",
                _fixture("consumer_reexport.flow"),
                "--c",
                "--strict",
                "-o",
                str(c_file),
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env=env,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        source = c_file.read_text(encoding="utf-8")
        for name in ("alpha_one", "alpha_two", "beta_one", "agg_own"):
            # One prototype, one definition — never two of either.
            assert source.count(f"int32_t {name}(void);") == 1, name
            assert source.count(f"int32_t {name}(void) {{") == 1, name


class TestReexportCollisions:
    def test_two_sources_export_the_same_name(self, tmp_path):
        root = _write_package(
            str(tmp_path),
            {
                "testlib/dup_a.flow": "export function dup_fn() -> i32 { return 1 }\n",
                "testlib/dup_b.flow": "export function dup_fn() -> i32 { return 2 }\n",
                "testlib/agg.flow": "export import .dup_a\nexport import .dup_b\n",
            },
        )
        with pytest.raises(SymbolCollisionError) as excinfo:
            get_module_resolver(os.path.join(root, "testlib", "agg.flow"))
        message = str(excinfo.value)
        assert "dup_fn" in message
        assert "Re-export collision" in message
        # Both source modules are named.
        assert "dup_a.flow" in message
        assert "dup_b.flow" in message

    def test_local_declaration_shadows_a_reexport(self, tmp_path):
        root = _write_package(
            str(tmp_path),
            {
                "testlib/alpha.flow": "export function alpha_one() -> i32 { return 1 }\n",
                "testlib/agg.flow": """
                    export import .alpha

                    export function alpha_one() -> i32 { return 7 }
                """,
            },
        )
        with pytest.raises(SymbolCollisionError) as excinfo:
            get_module_resolver(os.path.join(root, "testlib", "agg.flow"))
        message = str(excinfo.value)
        assert "alpha_one" in message
        assert "alpha.flow" in message
        assert "agg.flow" in message
        assert "declared locally" in message

    def test_collision_error_is_a_value_error(self):
        assert issubclass(SymbolCollisionError, ValueError)

    def test_diamond_reexport_is_not_a_collision(self, tmp_path):
        # Two aggregators forward the same declaration; a third forwards both.
        # Same source file on both paths, so this is one symbol, not a clash.
        root = _write_package(
            str(tmp_path),
            {
                "testlib/leaf.flow": "export function leaf_fn() -> i32 { return 5 }\n",
                "testlib/left.flow": "export import .leaf\n",
                "testlib/right.flow": "export import .leaf\n",
                "testlib/top.flow": "export import .left\nexport import .right\n",
                "main.flow": """
                    import testlib.top { leaf_fn }
                    function main() -> i32 { return leaf_fn() }
                """,
            },
        )
        resolver = get_module_resolver(os.path.join(root, "main.flow"))
        assert "leaf_fn" in resolver.symbol_table


class TestCompileAndRun:
    @pytest.mark.skipif(shutil.which("clang") is None, reason="clang not available")
    def test_reexport_program_compiles_and_returns_expected_exit_code(self, tmp_path):
        # alpha_one() + alpha_two() + beta_one() + agg_own() = 1 + 2 + 10 + 100
        c_file = tmp_path / "prog.c"
        exe = tmp_path / "prog"
        env = dict(os.environ)
        env["PYTHONPATH"] = os.path.join(REPO_ROOT, "src") + os.pathsep + env.get(
            "PYTHONPATH", ""
        )
        transpile = subprocess.run(
            [
                sys.executable,
                "-m",
                "flow.transpiler",
                _fixture("consumer_reexport.flow"),
                "--c",
                "--strict",
                "-o",
                str(c_file),
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env=env,
        )
        assert transpile.returncode == 0, transpile.stdout + transpile.stderr

        compile_result = subprocess.run(
            ["clang", "-Wno-everything", str(c_file), "-o", str(exe), "-lm"],
            capture_output=True,
            text=True,
        )
        assert compile_result.returncode == 0, compile_result.stderr

        run = subprocess.run([str(exe)], capture_output=True)
        assert run.returncode == 113


class TestLspFollowsReexports:
    def test_import_index_sees_forwarded_symbols(self):
        from flow.lsp_intel import index_imports, parse_source

        path = _fixture("consumer_reexport.flow")
        with open(path, encoding="utf-8") as f:
            declarations = parse_source(f.read())
        symbols, _ = index_imports(path, declarations)
        assert "alpha_one" in symbols
        assert "beta_one" in symbols
        # Definition location points at the declaring file, not the aggregator.
        assert symbols["alpha_one"]["uri"].endswith("alpha.flow")


class TestFormatterRoundTrip:
    def test_formatter_keeps_the_export_prefix(self):
        from flow.formatter import Formatter

        source = (
            "export import .alpha\n"
            "export import .beta { beta_one }\n"
            "import verify.nat as nat\n"
        )
        out = Formatter().format_file(source)
        assert "export import .alpha" in out
        assert "export import .beta { beta_one }" in out
        assert "import verify.nat as nat" in out
