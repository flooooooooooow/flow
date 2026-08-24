"""Contracts for the data-driven Wiki demo/gallery system."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_photoreal_gallery_generator_tracks_all_fsl_entries():
    gallery = load_script("build_shader_gallery.py")
    demos = gallery.parse_scenes() + gallery.parse_materials()
    names = [demo.name for demo in demos]

    assert len(demos) == 64
    assert len(set(names)) == 64
    assert [demo.name for demo in gallery.parse_scenes()] == [
        "photoreal_studio",
        "photoreal_glass",
        "photoreal_marble",
        "photoreal_chrome",
    ]
    assert "photoreal_gold" in names
    assert "photoreal_energy_crystal" in names
    assert "photoreal_underwater" in names

    page = gallery.build_page(demos)
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
    overview = load_script("build_demo_overview.py")
    data = json.loads((ROOT / "docs/demos/catalog.json").read_text(encoding="utf-8"))
    page = overview.build(data)

    assert "# Demo Showcase" in page
    assert page.count('class="demo-collection-card') >= len(data["collections"])
    assert "Photoreal FSL" in page
    assert "Systems through time" in page
    assert "Live WebAssembly" in page


def test_wiki_shell_loads_gallery_presentation_assets():
    shell = (ROOT / "site/index.html").read_text(encoding="utf-8")
    assert 'href="assets/demo-gallery.css"' in shell
    assert 'src="assets/gallery-enhance.js"' in shell

    enhancer = (ROOT / "docs/assets/gallery-enhance.js").read_text(encoding="utf-8")
    assert "MutationObserver" in enhancer
    assert "demo-tile-grid-enhanced" in enhancer
