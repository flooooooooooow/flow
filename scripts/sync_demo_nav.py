#!/usr/bin/env python3
"""Keep the Wiki's Gallery tab aligned with docs/demos/catalog.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAV = ROOT / "docs/nav.json"
CATALOG = ROOT / "docs/demos/catalog.json"

LABELS = {
    "shaders": "Photoreal FSL",
    "games": "Games",
    "morphogenesis": "Morphogenesis",
    "neuro": "Neurons & Networks",
    "social": "Opinion Dynamics",
    "threed": "3D",
    "evoleco": "Evolutionary Biology",
    "planet": "Planets",
    "procgen": "Procedural Generation",
    "numerical": "Numerical Methods",
    "evolution": "Evolution Suite",
    "wasm": "WebAssembly",
}


def nav_item(item: dict) -> dict:
    return {
        "label": LABELS.get(item["id"], item["title"]),
        "path": f"demos/{item['page']}",
    }


def build_sections(catalog: dict) -> list[dict]:
    by_id = {item["id"]: item for item in catalog["collections"]}

    def items(*ids: str) -> list[dict]:
        return [nav_item(by_id[item_id]) for item_id in ids]

    return [
        {
            "id": "gallery-showcase",
            "tab": "gallery",
            "title": "Showcase",
            "items": [
                {"label": "Demo Showcase", "path": "demos/overview.md"},
                {"label": "Solve It the Flow Way", "path": "examples/flow_way/README.md"},
            ],
        },
        {
            "id": "gallery-rendering",
            "tab": "gallery",
            "title": "Rendering & generation",
            "items": items("shaders", "threed", "planet", "procgen"),
        },
        {
            "id": "gallery-systems",
            "tab": "gallery",
            "title": "Systems through time",
            "items": items(
                "morphogenesis",
                "neuro",
                "social",
                "evoleco",
                "evolution",
                "numerical",
            ),
        },
        {
            "id": "gallery-interactive",
            "tab": "gallery",
            "title": "Interactive",
            "items": items("games", "wasm")
            + [
                {
                    "label": "Live WASM demos",
                    "path": "wasm/index.html",
                    "external": True,
                }
            ],
        },
    ]


def sync(nav: dict, catalog: dict) -> dict:
    sections = nav["sections"]

    # Replace the Start tab's redundant gallery list with a deliberately small
    # set of entry points. The full taxonomy belongs in the Gallery tab.
    for section in sections:
        if section.get("id") == "start-galleries":
            section["title"] = "Popular demos"
            section["items"] = [
                {"label": "Demo Showcase", "path": "demos/overview.md"},
                {"label": "Photoreal FSL", "path": "demos/shaders.md"},
                {"label": "Games", "path": "demos/games.md"},
                {"label": "Morphogenesis", "path": "demos/morphogenesis.md"},
                {"label": "Live WASM demos", "path": "wasm/index.html", "external": True},
            ]
            break

    gallery_positions = [i for i, section in enumerate(sections) if section.get("tab") == "gallery"]
    insert_at = gallery_positions[0] if gallery_positions else 1
    sections[:] = [section for section in sections if section.get("tab") != "gallery"]
    for offset, section in enumerate(build_sections(catalog)):
        sections.insert(insert_at + offset, section)
    return nav


def rendered() -> str:
    nav = json.loads(NAV.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    sync(nav, catalog)
    return json.dumps(nav, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = rendered()
    if args.check:
        current = NAV.read_text(encoding="utf-8")
        if current != expected:
            raise SystemExit("docs/nav.json demo sections are stale; run scripts/sync_demo_nav.py")
        print("demo navigation is current")
        return 0

    NAV.write_text(expected, encoding="utf-8")
    print("updated docs/nav.json gallery navigation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
