#!/usr/bin/env python3
"""Generate the Wiki demo showcase from docs/demos/catalog.json."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs/demos/catalog.json"
OUTPUT = ROOT / "docs/demos/overview.md"


def card(item: dict, *, featured: bool = False) -> str:
    cls = "demo-collection-card demo-collection-featured" if featured else "demo-collection-card"
    title = html.escape(item["title"])
    desc = html.escape(item["description"])
    page = html.escape(item["page"], quote=True)
    preview = html.escape(item["preview"], quote=True)
    runtime = html.escape(item["runtime"])
    count = html.escape(str(item["count"]))
    count_label = html.escape(item["count_label"])
    section = html.escape(item["section"])
    return f'''<article class="{cls}">
  <a class="demo-collection-media" href="{page}" aria-label="Open {title} gallery">
    <img src="{preview}" alt="Preview of the {title} gallery" loading="lazy">
  </a>
  <div class="demo-collection-body">
    <div class="demo-collection-kicker">{section}</div>
    <h3><a href="{page}">{title}</a></h3>
    <p>{desc}</p>
    <div class="demo-collection-meta"><span><strong>{count}</strong> {count_label}</span><span>{runtime}</span></div>
    <a class="demo-collection-open" href="{page}">Open gallery →</a>
  </div>
</article>'''


def build(data: dict) -> str:
    collections = data["collections"]
    featured = [item for item in collections if item.get("featured")]
    sections: list[str] = []
    for item in collections:
        if item["section"] not in sections:
            sections.append(item["section"])

    lines = [
        "# Demo Showcase",
        "",
        "Flow's visual output is organised in three layers: a **demo** is one runnable thing; ",
        "a **gallery** collects related demos; this **showcase** is the curated cross-section. ",
        "That separation keeps the Wiki useful when the example corpus grows instead of turning ",
        "every page into one enormous list.",
        "",
        '<div class="demo-gallery-summary">',
        f'  <span><strong>{len(collections)}</strong> visual collections</span>',
        '  <span><strong>GPU + CPU</strong> rendering paths</span>',
        '  <span><strong>Recorded + live</strong> output</span>',
        '  <span><strong>Source-linked</strong> demos</span>',
        "</div>",
        "",
        "## Start here",
        "",
        "Six collections that show the range of the language without making you understand the ",
        "documentation hierarchy first.",
        "",
        '<div class="demo-showcase-grid">',
    ]
    lines.extend(card(item, featured=True) for item in featured)
    lines.extend(["</div>", "", "## Browse every gallery", ""])

    for section in sections:
        group = [item for item in collections if item["section"] == section]
        lines.extend(
            [
                f"### {section}",
                "",
                '<div class="demo-collection-grid">',
            ]
        )
        lines.extend(card(item) for item in group)
        lines.extend(["</div>", ""])

    lines.extend(
        [
            "## Run and record",
            "",
            "CPU `gfx` demos use the cross-platform headless recorder; FSL shaders use the ",
            "offscreen Metal recorder so the published GIFs are produced by the real shader pipeline.",
            "",
            "```bash",
            "./flow gfx examples/games/tetris_gfx.flow",
            "./flow record examples/morphogenesis/gray_scott.flow --frames 240 --gif out.gif",
            "./flow shader examples/gpu/shader_photoreal.flow --name photoreal_glass",
            "python3 scripts/record_shader_gallery.py --group photoreal",
            "```",
            "",
            "For problem-first code examples rather than visual output, use ",
            "[Solve It the Flow Way](../../examples/flow_way/README.md). For interactive browser ",
            "builds, open the [WebAssembly gallery](wasm.md). Recording internals and regeneration ",
            "commands live in the [demos README](README.md).",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-previews", action="store_true")
    args = parser.parse_args()

    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    ids = [item["id"] for item in data["collections"]]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate demo collection id in docs/demos/catalog.json")

    if args.check_previews:
        missing = [item["preview"] for item in data["collections"] if not (CATALOG.parent / item["preview"]).exists()]
        if missing:
            raise SystemExit("missing gallery preview assets: " + ", ".join(missing))

    generated = build(data)
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != generated:
            raise SystemExit("docs/demos/overview.md is stale; run scripts/build_demo_overview.py")
        print("demo overview is current")
        return 0

    OUTPUT.write_text(generated, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} from {CATALOG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
