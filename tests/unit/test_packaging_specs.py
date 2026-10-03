"""Tests for packaging specifications across distributions (Homebrew, Nix, Debian, Arch, Scoop)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TestPackagingSpecs:
    def test_packaging_readme_exists(self):
        readme = ROOT / "packaging" / "README.md"
        assert readme.exists()
        text = readme.read_text(encoding="utf-8")
        assert "Homebrew" in text
        assert "Nix" in text
        assert "Debian" in text
        assert "Arch Linux" in text
        assert "Scoop" in text

    def test_nix_specs_exist_and_contain_version(self):
        default_nix = ROOT / "packaging" / "nix" / "default.nix"
        flake_nix = ROOT / "packaging" / "nix" / "flake.nix"
        assert default_nix.exists()
        assert flake_nix.exists()

        content = default_nix.read_text(encoding="utf-8")
        assert 'pname = "flow";' in content
        assert "version =" in content
        assert "pkgs.fetchFromGitHub" in content

        flake_content = flake_nix.read_text(encoding="utf-8")
        assert "inputs = {" in flake_content
        assert "outputs = {" in flake_content

    def test_debian_control_and_build_script(self):
        control = ROOT / "packaging" / "deb" / "debian" / "control"
        rules = ROOT / "packaging" / "deb" / "debian" / "rules"
        changelog = ROOT / "packaging" / "deb" / "debian" / "changelog"
        build_script = ROOT / "packaging" / "deb" / "build-deb.sh"

        assert control.exists()
        assert rules.exists()
        assert changelog.exists()
        assert build_script.exists()

        ctrl_text = control.read_text(encoding="utf-8")
        assert "Package: flow" in ctrl_text
        assert "Depends:" in ctrl_text
        assert "Description:" in ctrl_text

        rules_text = rules.read_text(encoding="utf-8")
        assert "dh $@" in rules_text

    def test_arch_pkgbuild_exists_and_valid(self):
        pkgbuild = ROOT / "packaging" / "arch" / "PKGBUILD"
        assert pkgbuild.exists()
        text = pkgbuild.read_text(encoding="utf-8")
        assert "pkgname=flow-language" in text
        assert "pkgver=" in text
        assert "package() {" in text

    def test_scoop_json_valid(self):
        scoop_json = ROOT / "packaging" / "scoop" / "flow.json"
        assert scoop_json.exists()
        data = json.loads(scoop_json.read_text(encoding="utf-8"))
        assert "version" in data
        assert data["bin"] == "flow"
        assert "architecture" in data
        assert "64bit" in data["architecture"]
        assert "url" in data["architecture"]["64bit"]

    def test_getting_started_docs_reference_packages(self):
        getting_started = ROOT / "docs" / "getting-started.md"
        assert getting_started.exists()
        text = getting_started.read_text(encoding="utf-8")
        assert "Homebrew" in text
        assert "Nix" in text
        assert "Debian" in text
        assert "Arch Linux" in text
        assert "Scoop" in text
