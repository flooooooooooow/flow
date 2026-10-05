"""Tests for the Flow package registry."""

from flow.package import FlowPackageManager
from flow.registry import (
    FlowRegistry,
    parse_semver,
    resolve_version,
    version_matches,
)


def test_semver_parse_and_match():
    assert parse_semver("1.2.3") == (1, 2, 3)
    assert version_matches("*", "9.9.9")
    assert version_matches("0.1.0", "0.1.0")
    assert version_matches("^1.2.0", "1.9.0")
    assert not version_matches("^1.2.0", "2.0.0")
    assert version_matches("^0.1.0", "0.1.5")
    assert not version_matches("^0.1.0", "0.2.0")
    assert version_matches(">=0.1.0", "0.2.0")


def test_bundled_index_has_hello_lib():
    reg = FlowRegistry()
    pkg = reg.get("hello_lib")
    assert pkg is not None
    latest = resolve_version(pkg, "*")
    assert latest is not None
    assert latest.version == "0.1.0"
    assert latest.path == "registry/packages/hello_lib"
    assert reg.name == "flow-packages"


def test_bundled_index_has_ecosystem_seed_packages():
    reg = FlowRegistry()
    names = (
        "json", "toml", "http", "sqlite", "sqlkit", "compress", "image",
        "cli", "collectionsx", "strings", "dns", "serde", "log", "testing", "ffi",
    )
    for name in names:
        pkg = reg.get(name)
        assert pkg is not None, name
        latest = resolve_version(pkg, "*")
        assert latest is not None, name
        assert latest.version == "0.1.0"
        assert latest.path == f"registry/packages/{name}"


def test_search_finds_hello():
    hits = FlowRegistry().search("hello")
    assert any(c.name == "hello_lib" for c in hits)


def test_add_registry_package_installs(tmp_path):
    (tmp_path / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n[dependencies]\n',
        encoding="utf-8",
    )
    mgr = FlowPackageManager(str(tmp_path))
    assert mgr.add("hello_lib")
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
    mgr = FlowPackageManager(str(tmp_path))
    assert mgr.install()
    assert (tmp_path / "flow_packages" / "hello_lib" / "flow.toml").exists()


def test_unknown_registry_package_fails_honestly(tmp_path, capsys):
    (tmp_path / "flow.toml").write_text(
        '[package]\nname = "app"\nversion = "0.1.0"\n\n'
        "[dependencies]\n"
        'missing_pkg_xyz = "1.0.0"\n',
        encoding="utf-8",
    )
    mgr = FlowPackageManager(str(tmp_path))
    assert not mgr.install()
    out = capsys.readouterr().out
    assert "Unknown dependency" in out or "not found" in out.lower()


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
    reg = FlowRegistry(index)
    assert reg.get("mypkg") is not None
    assert resolve_version(reg.get("mypkg"), "*").git.endswith("mypkg.git")
