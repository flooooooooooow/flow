"""Contracts for the data-driven Wiki demo/gallery system.

The generators are Flow programs behind scripts/build_shader_gallery.sh and
scripts/build_demo_overview.sh. Their --check mode regenerates the page and
compares it with the checked-in copy, so the checked-in pages stand for the
generated output here.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def run_shim(name: str, *args: str) -> subprocess.CompletedProcess:
    if shutil.which("cc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler")
    return subprocess.run(
        [str(ROOT / "scripts" / name), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_photoreal_gallery_generator_tracks_all_fsl_entries():
    result = run_shim("build_shader_gallery.sh", "--check")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "shader gallery page is current\n"

    page = (ROOT / "docs/demos/shaders.md").read_text(encoding="utf-8")
    names = re.findall(r'<img src="./shaders/(photoreal_[A-Za-z0-9_]+)\.gif"', page)
    assert len(names) == 64
    assert len(set(names)) == 64
    featured = page.split('<div class="demo-feature-grid">', 1)[1].split("</div>\n\n", 1)[0]
    assert re.findall(r"--name (photoreal_[A-Za-z0-9_]+)", featured) == [
        "photoreal_studio",
        "photoreal_glass",
        "photoreal_marble",
        "photoreal_chrome",
    ]
    assert "photoreal_gold" in names
    assert "photoreal_energy_crystal" in names
    assert "photoreal_underwater" in names
    assert page.count('<figure class="demo-tile') == 64
    assert "record_shader_gallery.py --group photoreal" in page


def test_demo_catalog_is_unique_and_covers_expected_collections():
    catalog = json.loads((ROOT / "docs/demos/catalog.json").read_text(encoding="utf-8"))
    items = catalog["collections"]
    ids = [item["id"] for item in items]

    assert len(ids) == len(set(ids))
    assert len(items) == 12
    assert {"shaders", "games", "morphogenesis", "neuro", "threed", "planet", "wasm"} <= set(ids)
    assert {item["section"] for item in items} == {
        "Rendering",
        "Systems through time",
        "Interactive",
        "Numerics",
    }
    assert all(item["page"].endswith(".md") for item in items)
    assert all(item["preview"].endswith(".gif") for item in items)


def test_demo_overview_is_derived_from_catalog():
    result = run_shim("build_demo_overview.sh", "--check", "--check-previews")
    assert result.returncode == 0, result.stderr
    data = json.loads((ROOT / "docs/demos/catalog.json").read_text(encoding="utf-8"))
    page = (ROOT / "docs/demos/overview.md").read_text(encoding="utf-8")

    assert "# Demo Showcase" in page
    assert page.count('class="demo-collection-card') >= len(data["collections"])
    assert "Photoreal FSL" in page
    assert "Systems through time" in page
    assert "Live WebAssembly" in page


def test_demo_navigation_is_synced_with_catalog():
    result = run_shim("sync_demo_nav.sh", "--check")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "demo navigation is current\n"


def test_wiki_shell_loads_gallery_presentation_assets():
    shell = (ROOT / "site/index.html").read_text(encoding="utf-8")
    assert 'href="assets/demo-gallery.css"' in shell
    assert 'src="assets/gallery-enhance.js"' in shell

    enhancer = (ROOT / "docs/assets/gallery-enhance.js").read_text(encoding="utf-8")
    assert "MutationObserver" in enhancer
    assert "demo-tile-grid-enhanced" in enhancer
