"""Regression tests for module entry-point isolation (#621)."""

from flow.module_resolver import get_module_resolver, resolve_modules


def _write_programs(tmp_path, *, export_library_main: bool = False):
    library = tmp_path / "lib.flow"
    main_prefix = "export " if export_library_main else ""
    library.write_text(
        "export function helper() -> i32 { return 42 }\n\n"
        f"{main_prefix}function main() -> i32 {{ return 7 }}\n",
        encoding="utf-8",
    )

    root = tmp_path / "app.flow"
    root.write_text(
        "import .lib\n\n"
        "function main() -> i32 { return helper() }\n",
        encoding="utf-8",
    )
    return library, root


def test_imported_main_is_not_emitted_or_globally_bound(tmp_path):
    library, root = _write_programs(tmp_path)

    declarations = resolve_modules(str(root))
    mains = [decl for decl in declarations if getattr(decl, "name", None) == "main"]
    assert len(mains) == 1

    resolver = get_module_resolver(str(root))
    assert resolver.symbol_table["main"].source_file == str(root.resolve())

    library_info = resolver.get_module_info(str(library))
    assert library_info is not None
    assert "main" in library_info.symbols
    assert not library_info.symbols["main"].is_exported


def test_imported_main_stays_private_even_when_marked_export(tmp_path):
    library, root = _write_programs(tmp_path, export_library_main=True)

    declarations = resolve_modules(str(root))
    mains = [decl for decl in declarations if getattr(decl, "name", None) == "main"]
    assert len(mains) == 1

    resolver = get_module_resolver(str(root))
    assert resolver.symbol_table["main"].source_file == str(root.resolve())

    library_info = resolver.get_module_info(str(library))
    assert library_info is not None
    assert not library_info.symbols["main"].is_exported
