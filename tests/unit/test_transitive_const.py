"""Regression tests for transitive const visibility (#411).

export const from an imported module should be visible in downstream
modules that import the importer.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.module_resolver import resolve_modules
from flow.parser import ConstDecl


def _write_module(tmpdir: Path, relpath: str, source: str) -> str:
    full = tmpdir / relpath
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(source)
    return str(full)


def test_export_const_visible_through_import_chain():
    """export const in A is visible in C which imports B which imports A."""
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        _write_module(tmpdir, "lib/a.flow", "export const FOO: i32 = 42\n")
        _write_module(tmpdir, "lib/b.flow",
                       "import .a\n"
                       "export function get_foo() -> i32 { return FOO }\n")
        main_path = _write_module(tmpdir, "main.flow",
                                   "import .lib.b\n"
                                   "function main() -> i32 { let x: i32 = FOO ; return x }\n")
        decls = resolve_modules(main_path)
        consts = [d for d in decls if isinstance(d, ConstDecl) and d.name == "FOO"]
        assert len(consts) == 1
        assert consts[0].is_exported


def test_export_const_value_correct():
    """The const value is correct through the import chain."""
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        _write_module(tmpdir, "lib/a.flow", "export const FOO: i32 = 42\n")
        _write_module(tmpdir, "lib/b.flow",
                       "import .a\n"
                       "export function get_foo() -> i32 { return FOO }\n")
        main_path = _write_module(tmpdir, "main.flow",
                                   "import .lib.b\n"
                                   "function main() -> i32 { let x: i32 = FOO ; return x }\n")
        decls = resolve_modules(main_path)
        consts = [d for d in decls if isinstance(d, ConstDecl) and d.name == "FOO"]
        assert len(consts) == 1
        val = consts[0].value
        assert hasattr(val, "value")
        assert str(val.value) == "42"


def test_non_exported_const_also_visible():
    """Non-exported const in A is also visible through the import chain.

    The module resolver currently adds all declarations from recursively
    resolved modules, not just exported ones. This test documents that
    behavior.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        _write_module(tmpdir, "lib/a.flow", "const FOO: i32 = 42\n")
        _write_module(tmpdir, "lib/b.flow",
                       "import .a\n"
                       "export function get_foo() -> i32 { return FOO }\n")
        main_path = _write_module(tmpdir, "main.flow",
                                   "import .lib.b\n"
                                   "function main() -> i32 { let x: i32 = FOO ; return x }\n")
        decls = resolve_modules(main_path)
        consts = [d for d in decls if isinstance(d, ConstDecl) and d.name == "FOO"]
        assert len(consts) >= 1
