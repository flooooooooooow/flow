"""Tests for Flow package install behavior."""

from pathlib import Path

from flow.module_resolver import get_module_resolver
from flow.package import FlowPackage, FlowPackageManager
from flow.project_config import load_project_config
from flow.toml_compat import _fallback_loads


def test_toml_fallback_reads_inline_path_dependencies():
    data = _fallback_loads(
        '[package]\nname = "app"\n\n[dependencies]\n'
        'flow_audio = { path = "../flow-audio" }\n'
    )

    assert data["dependencies"]["flow_audio"] == {"path": "../flow-audio"}


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


def test_sync_for_program_discovers_nearest_project(tmp_path):
    dep = tmp_path / "mathkit"
    (dep / "src").mkdir(parents=True)
    (dep / "flow.toml").write_text(
        '[package]\nname = "mathkit"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (dep / "src" / "ops.flow").write_text(
        "export function add_one(x: i32) -> i32 { return x + 1 }\n",
        encoding="utf-8",
    )
    app = tmp_path / "app"
    (app / "src").mkdir(parents=True)
    (app / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n'
        '[dependencies]\nmathkit = { path = "../mathkit" }\n',
        encoding="utf-8",
    )
    main = app / "src" / "main.flow"
    main.write_text("function main() -> i32 { return 0 }\n", encoding="utf-8")

    assert FlowPackageManager.sync_for_program(str(main))
    assert (app / "flow_packages" / "mathkit" / "src" / "ops.flow").exists()


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


def test_unknown_registry_dependency_fails_honestly(tmp_path, capsys):
    (tmp_path / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n'
        "[dependencies]\n"
        'missing = "1.0.0"\n',
        encoding="utf-8",
    )

    manager = FlowPackageManager(str(tmp_path))

    assert not manager.install()
    out = capsys.readouterr().out
    assert "Unknown dependency" in out or "not found" in out.lower()


def test_git_url_helpers():
    assert FlowPackageManager._looks_like_git_url(
        "https://github.com/org/mylib.git"
    )
    assert FlowPackageManager._looks_like_git_url("git@github.com:org/mylib.git")
    assert FlowPackageManager._infer_git_name(
        "https://github.com/org/mylib.git"
    ) == "mylib"
    assert FlowPackageManager._normalize_git_url(
        "git+https://github.com/org/mylib.git"
    ) == "https://github.com/org/mylib.git"


def test_add_git_url_shorthand_and_lock_rev(tmp_path):
    import subprocess

    # Bare-ish repo with a Flow package at root
    repo = tmp_path / "mylib.git"
    work = tmp_path / "mylib-work"
    work.mkdir()
    (work / "flow.toml").write_text(
        '[package]\nname = "mylib"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (work / "src").mkdir()
    (work / "src" / "lib.flow").write_text(
        "export function one() -> i32 { return 1 }\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init"], cwd=work, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=work,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "test"],
        cwd=work,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=work, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=work,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "clone", "--bare", str(work), str(repo)],
        check=True,
        capture_output=True,
    )

    app = tmp_path / "app"
    app.mkdir()
    (app / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n[dependencies]\n',
        encoding="utf-8",
    )

    manager = FlowPackageManager(str(app))
    assert manager.add(f"file://{repo}")
    assert (app / "flow_packages" / "mylib" / "src" / "lib.flow").exists()
    lock = (app / "flow.lock").read_text(encoding="utf-8")
    assert '"source": "git"' in lock
    assert '"rev"' in lock
    toml = (app / "flow.toml").read_text(encoding="utf-8")
    assert "mylib" in toml and "git" in toml


def test_git_subdir_install(tmp_path):
    import subprocess

    work = tmp_path / "mono-work"
    pkg = work / "packages" / "ring"
    pkg.mkdir(parents=True)
    (pkg / "flow.toml").write_text(
        '[package]\nname = "ring"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (pkg / "src").mkdir()
    (pkg / "src" / "lib.flow").write_text(
        "export function capacity() -> i32 { return 8 }\n",
        encoding="utf-8",
    )
    (work / "README.md").write_text("mono\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=work, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=work,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "test"],
        cwd=work,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=work, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=work,
        check=True,
        capture_output=True,
    )
    bare = tmp_path / "mono.git"
    subprocess.run(
        ["git", "clone", "--bare", str(work), str(bare)],
        check=True,
        capture_output=True,
    )

    app = tmp_path / "app"
    app.mkdir()
    (app / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n[dependencies]\n',
        encoding="utf-8",
    )
    manager = FlowPackageManager(str(app))
    assert manager.add(
        "ring",
        git=f"file://{bare}",
        subdir="packages/ring",
    )
    assert (app / "flow_packages" / "ring" / "src" / "lib.flow").exists()
    assert not (app / "flow_packages" / "ring" / "README.md").exists()


def test_collect_dependency_native_from_installed_package(tmp_path):
    dep = tmp_path / "httpish"
    (dep / "native").mkdir(parents=True)
    (dep / "src").mkdir(parents=True)
    (dep / "flow.toml").write_text(
        '[package]\nname = "httpish"\nversion = "0.1.0"\n\n'
        "[native]\n"
        'sources = ["native/bridge.c"]\n'
        'libs = ["curl"]\n',
        encoding="utf-8",
    )
    (dep / "native" / "bridge.c").write_text("int x;\n", encoding="utf-8")
    (dep / "src" / "lib.flow").write_text("export function n() -> i32 { return 1 }\n", encoding="utf-8")

    app = tmp_path / "app"
    app.mkdir()
    (app / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n'
        "[dependencies]\n"
        'httpish = { path = "../httpish" }\n',
        encoding="utf-8",
    )
    mgr = FlowPackageManager(str(app))
    assert mgr.install()
    config = mgr.load_config()
    sources, frameworks, libs, cflags, ldflags = mgr._collect_dependency_native(config)
    assert any(s.endswith("bridge.c") for s in sources)
    assert "curl" in libs
    assert frameworks == []
    assert cflags == []
    assert ldflags == []
