"""Tests for Flow package install behavior."""

from pathlib import Path

from flow.module_resolver import get_module_resolver
from flow.package import FlowPackage, FlowPackageManager
from flow.project_config import load_project_config


def test_package_config_round_trips_path_dependency():
    package = FlowPackage(
        name="consumer",
        dependencies={"mathkit": {"path": "../mathkit"}},
    )

    loaded = FlowPackage.from_toml(package.to_toml())

    assert loaded.dependencies["mathkit"] == {"path": "../mathkit"}


def test_install_path_dependency_copies_package_and_updates_lock(tmp_path):
    dep = tmp_path / "mathkit"
    dep_src = dep / "src"
    dep_src.mkdir(parents=True)
    (dep / "flow.toml").write_text(
        '[package]\nname = "mathkit"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (dep_src / "ops.flow").write_text(
        "export function add_one(x: i32) -> i32 {\n"
        "    return x + 1\n"
        "}\n",
        encoding="utf-8",
    )

    app = tmp_path / "app"
    app.mkdir()
    (app / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n'
        "[dependencies]\n"
        'mathkit = { path = "../mathkit" }\n',
        encoding="utf-8",
    )

    manager = FlowPackageManager(str(app))

    assert manager.install()
    assert (app / "flow_packages" / "mathkit" / "src" / "ops.flow").exists()
    assert '"source": "path"' in (app / "flow.lock").read_text(encoding="utf-8")


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


def test_registry_dependency_without_source_fails_honestly(tmp_path, capsys):
    (tmp_path / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n'
        "[dependencies]\n"
        'missing = "1.0.0"\n',
        encoding="utf-8",
    )

    manager = FlowPackageManager(str(tmp_path))

    assert not manager.install()
    assert "Registry dependency 'missing' is not supported yet" in capsys.readouterr().out
