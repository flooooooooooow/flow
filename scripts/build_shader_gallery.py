#!/usr/bin/env python3
"""Build docs/demos/shaders.md from the canonical FSL gallery sources.

The gallery page is generated so adding/removing a `shader fill photoreal_*`
entry cannot silently drift away from the Wiki. Material section comments in
shader_photoreal_materials.flow become gallery groups, and every fill gets a
GIF tile pointing at docs/demos/shaders/<fill>.gif.
"""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENES = ROOT / "examples/gpu/shader_photoreal.flow"
MATERIALS = ROOT / "examples/gpu/shader_photoreal_materials.flow"
OUTPUT = ROOT / "docs/demos/shaders.md"
ASSET_DIR = ROOT / "docs/demos/shaders"

FILL_RE = re.compile(r"^\s*shader\s+fill\s+(photoreal_[A-Za-z0-9_]+)\s*\{")
HEADING_RE = re.compile(r"^#\s+([A-Z][A-Za-z0-9 &/+\-]{1,52})\s*$")


@dataclass(frozen=True)
class Demo:
    name: str
    title: str
    category: str
    source: Path


def human_title(name: str) -> str:
    text = name.removeprefix("photoreal_").replace("_", " ")
    words = []
    for word in text.split():
        if word.lower() == "abs":
            words.append("ABS")
        elif word.lower() == "pbr":
            words.append("PBR")
        else:
            words.append(word.capitalize())
    return " ".join(words)


def parse_scenes() -> list[Demo]:
    demos = []
    for line in SCENES.read_text(encoding="utf-8").splitlines():
        match = FILL_RE.match(line)
        if match:
            name = match.group(1)
            demos.append(Demo(name, human_title(name), "Scene studies", SCENES))
    return demos


def parse_materials() -> list[Demo]:
    demos = []
    category = "Materials"
    for line in MATERIALS.read_text(encoding="utf-8").splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            candidate = heading.group(1).strip()
            # File-header prose contains punctuation or long phrases and does
            # not match this deliberately narrow heading grammar.
            category = candidate
            continue
        match = FILL_RE.match(line)
        if match:
            name = match.group(1)
            demos.append(Demo(name, human_title(name), category, MATERIALS))
    return demos


def source_href(demo: Demo) -> str:
    return "../../examples/gpu/" + demo.source.name


def asset_href(demo: Demo) -> str:
    return f"./shaders/{demo.name}.gif"


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def tile(demo: Demo, *, featured: bool = False) -> str:
    cls = "demo-tile demo-tile-featured" if featured else "demo-tile"
    title = html.escape(demo.title)
    category = html.escape(demo.category)
    src = html.escape(source_href(demo), quote=True)
    gif = html.escape(asset_href(demo), quote=True)
    command = html.escape(
        f"./flow shader examples/gpu/{demo.source.name} --name {demo.name}"
    )
    return f'''<figure class="{cls}">
  <a class="demo-tile-media" href="{src}" aria-label="Open {title} source">
    <img src="{gif}" alt="{title} rendered by Flow FSL" loading="lazy">
  </a>
  <figcaption>
    <div class="demo-tile-title"><strong>{title}</strong><span class="demo-badge">{category}</span></div>
    <code class="demo-run">{command}</code>
    <div class="demo-actions"><a href="{src}">Source</a><a href="../language/shaders.md">FSL guide</a></div>
  </figcaption>
</figure>'''


def build_page(demos: list[Demo]) -> str:
    scenes = [d for d in demos if d.category == "Scene studies"]
    materials = [d for d in demos if d.category != "Scene studies"]
    categories: list[str] = []
    for demo in materials:
        if demo.category not in categories:
            categories.append(demo.category)

    lines = [
        "# Photoreal FSL Gallery",
        "",
        "64 shaders, recorded from the real Flow Shader Language → Metal pipeline. ",
        "These are not mock-ups or screenshots reconstructed in another renderer: each GIF is ",
        "captured offscreen from the generated Metal fragment shader with deterministic time.",
        "",
        '<div class="demo-gallery-summary">',
        '  <span><strong>64</strong> runnable shaders</span>',
        '  <span><strong>4</strong> ray-marched scenes</span>',
        '  <span><strong>60</strong> material studies</span>',
        '  <span><strong>0</strong> external textures</span>',
        "</div>",
        "",
        "```bash",
        "./flow shader examples/gpu/shader_photoreal.flow",
        "./flow shader examples/gpu/shader_photoreal_materials.flow --name photoreal_gold",
        "python3 scripts/record_shader_gallery.py --group photoreal",
        "```",
        "",
        "## Scene studies",
        "",
        "The large studies exercise SDF composition, finite-difference normals, soft shadows, ",
        "ambient occlusion, Fresnel response, reflection/refraction and procedural environments.",
        "",
        '<div class="demo-feature-grid">',
    ]
    lines.extend(tile(demo, featured=True) for demo in scenes)
    lines.extend(["</div>", "", "## Material library", ""])

    lines.append('<nav class="demo-chip-row" aria-label="Material categories">')
    lines.extend(
        f'  <a class="demo-chip" href="#{slug(category)}">{html.escape(category)}</a>'
        for category in categories
    )
    lines.extend(["</nav>", ""])

    for category in categories:
        group = [demo for demo in materials if demo.category == category]
        lines.extend(
            [
                f"### {category}",
                "",
                f'<p class="demo-section-meta">{len(group)} runnable studies</p>',
                "",
                '<div class="demo-tile-grid">',
            ]
        )
        lines.extend(tile(demo) for demo in group)
        lines.extend(["</div>", ""])

    lines.extend(
        [
            "## Recording contract",
            "",
            "`scripts/record_shader_gallery.py` compiles the same FSL files used by `./flow shader`, ",
            "renders them with `runtime/shader_record_metal.m`, and passes the resulting PPM frames ",
            "through the shared GIF encoder. Capture time is `frame / fps`, so animations do not ",
            "depend on wall-clock scheduling. The recorder requires macOS with an exposed Metal device.",
            "",
            "Related: [all galleries](overview.md) · [FSL language guide](../language/shaders.md) · ",
            "[GPU examples](../../examples/gpu/) · [how recordings are produced](README.md)",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if shaders.md is stale")
    parser.add_argument("--check-assets", action="store_true", help="require every referenced GIF")
    args = parser.parse_args()

    demos = parse_scenes() + parse_materials()
    names = [demo.name for demo in demos]
    if len(demos) != 64 or len(set(names)) != 64:
        raise SystemExit(
            f"shader gallery contract violated: expected 64 unique entries, got "
            f"{len(demos)} entries / {len(set(names))} unique"
        )

    if args.check_assets:
        missing = [demo.name for demo in demos if not (ASSET_DIR / f"{demo.name}.gif").exists()]
        if missing:
            raise SystemExit("missing shader GIFs: " + ", ".join(missing))

    generated = build_page(demos)
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != generated:
            raise SystemExit("docs/demos/shaders.md is stale; run scripts/build_shader_gallery.py")
        print("shader gallery page is current")
        return 0

    OUTPUT.write_text(generated, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} with {len(demos)} demos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
