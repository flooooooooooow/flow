"""Tests for the Flow package registry."""

import json
import subprocess
from pathlib import Path

from flow.package import FlowPackageManager
from flow.registry import FlowRegistry, parse_semver

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "registry" / "index.json"


def flow_pkg(cwd, *args):
    """Run the Flow package manager (compiler/src/pkg.flow) through flow-driver."""
    return subprocess.run(
        ["bash", str(ROOT / "flow-driver"), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_semver_parse():
    assert parse_semver("1.2.3") == (1, 2, 3)
    assert parse_semver("v2.0.0-beta") == (2, 0, 0)


def test_bundled_index_has_ecosystem_seed_packages():
    packages = json.loads(INDEX.read_text(encoding="utf-8"))["packages"]
    names = (
        "hello_lib", "json", "toml", "http", "sqlite", "sqlkit", "compress",
        "image", "cli", "collectionsx", "strings", "dns", "serde", "log",
        "testing", "ffi",
    )
    for name in names:
        versions = packages[name]["versions"]
        assert versions[0]["version"] == "0.1.0", name
        assert versions[0]["path"] == f"registry/packages/{name}", name
    assert FlowRegistry().name == "flow-packages"


def test_search_finds_hello(tmp_path):
    result = flow_pkg(tmp_path, "search", "hello")
    assert result.returncode == 0
    assert "hello_lib" in result.stdout


def test_add_registry_package_installs(tmp_path):
    (tmp_path / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n[dependencies]\n',
        encoding="utf-8",
    )
    assert flow_pkg(tmp_path, "add", "hello_lib").returncode == 0
    assert (tmp_path / "flow_packages" / "hello_lib" / "src" / "lib.flow").exists()
    toml = (tmp_path / "flow.toml").read_text(encoding="utf-8")
    assert "hello_lib" in toml
    lock = (tmp_path / "flow.lock").read_text(encoding="utf-8")
    assert '"source": "registry"' in lock


def test_install_version_string_from_registry(tmp_path):
    (tmp_path / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n'
        "[dependencies]\n"
        'hello_lib = "0.1.0"\n',
        encoding="utf-8",
    )
    assert flow_pkg(tmp_path, "sync").returncode == 0
    assert (tmp_path / "flow_packages" / "hello_lib" / "flow.toml").exists()


def test_unknown_registry_package_fails_honestly(tmp_path):
    (tmp_path / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n'
        "[dependencies]\n"
        'missing_pkg_xyz = "1.0.0"\n',
        encoding="utf-8",
    )
    result = flow_pkg(tmp_path, "sync")
    assert result.returncode == 1
    assert "Unknown dependency" in result.stdout


def test_publish_local_updates_index(tmp_path, monkeypatch):
    index = tmp_path / "index.json"
    index.write_text(
        '{"version": 1, "name": "test-reg", "packages": {}}\n', encoding="utf-8"
    )
    monkeypatch.setenv("FLOW_REGISTRY_PATH", str(index))

    pkg_dir = tmp_path / "mypkg"
    pkg_dir.mkdir()
    (pkg_dir / "flow.toml").write_text(
        '[package]\nname = "mypkg"\nversion = "0.2.0"\n'
        'description = "demo"\nlicense = "MIT"\n',
        encoding="utf-8",
    )
    mgr = FlowPackageManager(str(pkg_dir))
    # Outside repo → need --git
    assert not mgr.publish()
    assert mgr.publish(git="https://example.com/mypkg.git", tag="v0.2.0")
    data = json.loads(index.read_text(encoding="utf-8"))
    versions = data["packages"]["mypkg"]["versions"]
    assert versions[0]["version"] == "0.2.0"
    assert versions[0]["git"].endswith("mypkg.git")
