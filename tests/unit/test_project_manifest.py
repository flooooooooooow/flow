"""Project manifest reading on the Python front end (MLIR path).

The package commands are the Flow package manager (compiler/src/pkg.flow),
checked by scripts/check_pkg_parity.sh (install, add, sync, search, info)
and scripts/check_pkg_commands.sh (init, publish, build, build-native,
run-native, clean). What stays here is the manifest reading that
module_resolver.py, used by the MLIR backend, still does in Python.
"""

from flow.module_resolver import get_module_resolver
from flow.project_config import load_project_config
from flow.toml_compat import _fallback_loads


def test_toml_fallback_reads_inline_path_dependencies():
    data = _fallback_loads(
        '[package]\nname = "app"\n\n[dependencies]\n'
        'flow_audio = { path = "../flow-audio" }\n'
    )

    assert data["dependencies"]["flow_audio"] == {"path": "../flow-audio"}


def test_dot_import_resolves_installed_path_dependency(tmp_path):
    app = tmp_path / "app"
    package_src = app / "flow_packages" / "mathkit" / "src"
    package_src.mkdir(parents=True)
    (app / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n'
        "[dependencies]\n"
        'mathkit = { path = "../mathkit" }\n',
        encoding="utf-8",
    )
    (package_src / "ops.flow").write_text(
        "export function add_one(x: i32) -> i32 {\n"
        "    return x + 1\n"
        "}\n",
        encoding="utf-8",
    )
    main = app / "main.flow"
    main.write_text(
        "import mathkit.ops { add_one }\n\n"
        "function main() -> i32 {\n"
        "    return add_one(0)\n"
        "}\n",
        encoding="utf-8",
    )

    cfg = load_project_config(str(main))
    resolver = get_module_resolver(str(main))

    assert "mathkit" in cfg.dependencies
    assert "add_one" in resolver.symbol_table
