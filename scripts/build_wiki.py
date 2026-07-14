#!/usr/bin/env python3
"""Build the Flow wiki static site for VPS deploy."""

from __future__ import annotations

import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"
OUT = ROOT / "build" / "wiki"

SKIP_DOCS = {"playground"}


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def copy_docs() -> None:
    for item in DOCS.iterdir():
        if item.name in SKIP_DOCS or item.name.startswith("."):
            continue
        target = OUT / item.name
        if item.is_dir():
            copy_tree(item, target)
        else:
            shutil.copy2(item, target)


def copy_extras() -> None:
    for name in ("README.md", "mkdocs.yml"):
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, OUT / name)

    grammar = DOCS / "grammar.ebnf"
    if grammar.exists():
        shutil.copy2(grammar, OUT / "grammar.ebnf")

    roadmap = ROOT / "ROADMAP.md"
    if roadmap.exists():
        dest = OUT / "project" / "language-roadmap.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(roadmap, dest)

    assets_src = DOCS / "assets"
    if assets_src.exists():
        copy_tree(assets_src, OUT / "assets")

    playground = DOCS / "playground"
    if playground.exists():
        copy_tree(playground, OUT / "playground")


def proof_title(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("## ") and "Definition" not in line and "Axiom" not in line:
            return line[3:].strip()
    return ""


def proof_summary(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("*") and line.endswith("*") and len(line) > 2:
            return line.strip("*").strip()
    return ""


def short_euclid_label(rel: str) -> str:
    name = Path(rel).stem
    m = re.search(r"prop-(\d+)", name)
    if m:
        return f"Prop {m.group(1)}"
    return name


def proof_group_label(group: str, rows: list[dict]) -> str:
    """Human-readable sidebar label for proof example groups."""
    labels = {
        "analysis": "Analysis",
        "circuits": "Circuits",
        "geometry": "Geometry",
        "math": "Math",
        "math/derived": "Derived Math",
        "systems": "Systems",
        "transforms": "Transforms",
    }
    base = labels.get(group, group.replace("/", " · ").replace("-", " ").title())
    return f"{base} ({len(rows)})"


def page_category(wiki_path: str) -> str:
    p = wiki_path.replace("\\", "/")
    if p.startswith("tutorials/"):
        return "tutorial"
    if "flow-verify" in p or p.endswith(".proof.md"):
        return "proof"
    if p.startswith("library/") or p.startswith("language/") or p in {
        "LANGUAGE_SPEC.md",
        "grammar.ebnf",
    }:
        return "reference"
    if p in {"DEVELOPMENT.md", "python-target.md", "NEXT.md"} or p.startswith("project/"):
        return "tooling" if "CHANGELOG" not in p and "CONTRIBUTING" not in p else "guide"
    if p.startswith("third-party/"):
        return "proof"
    return "guide"


def sync_proofs() -> tuple[list[dict], list[dict]]:
    lib_src = ROOT / "lib" / "verify"
    ex_src = ROOT / "examples" / "verify"
    lib_dst = OUT / "third-party" / "flow-verify" / "proofs" / "lib"
    ex_dst = OUT / "third-party" / "flow-verify" / "proofs" / "examples"

    if (OUT / "third-party" / "flow-verify" / "proofs").exists():
        shutil.rmtree(OUT / "third-party" / "flow-verify" / "proofs")

    lib_dst.mkdir(parents=True, exist_ok=True)
    ex_dst.mkdir(parents=True, exist_ok=True)

    lib_rows: list[dict] = []
    ex_rows: list[dict] = []

    for src, dst, prefix, bucket in (
        (lib_src, lib_dst, "lib", lib_rows),
        (ex_src, ex_dst, "examples", ex_rows),
    ):
        if not src.exists():
            continue
        for path in sorted(src.rglob("*.proof.md")):
            rel = path.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            svg = path.with_suffix(".svg")
            if svg.exists():
                shutil.copy2(svg, target.with_suffix(".svg"))
            text = path.read_text(encoding="utf-8", errors="replace")
            bucket.append(
                {
                    "rel": rel.as_posix(),
                    "title": proof_title(text) or rel.as_posix(),
                    "summary": proof_summary(text),
                    "wiki_path": f"third-party/flow-verify/proofs/{prefix}/{rel.as_posix()}",
                }
            )

    return lib_rows, ex_rows


def group_examples(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for row in rows:
        parts = row["rel"].split("/")
        key = parts[0] if parts else "other"
        if key == "euclid" and len(parts) > 1:
            key = f"euclid/{parts[1]}"
        elif key == "math" and len(parts) > 1:
            key = f"math/{parts[1]}"
        groups.setdefault(key, []).append(row)
    return dict(sorted(groups.items()))


def write_catalog(lib_rows: list[dict], ex_rows: list[dict]) -> None:
    today = date.today().isoformat()
    lines = [
        "# Proof Catalog",
        "",
        f"> **{len(lib_rows)}** core modules · **{len(ex_rows)}** extended proofs · updated {today}",
        "",
        "Use the sidebar **Third-Party → flow-verify** section for direct book access.",
        "",
        "---",
        "",
        "## Core library",
        "",
        "| Module | Summary |",
        "|--------|---------|",
    ]

    for row in lib_rows:
        summary = (row["summary"] or "—").replace("|", "\\|")
        name = Path(row["rel"]).stem
        link = f"[{name}]({row['wiki_path']})"
        lines.append(f"| {link} | {summary} |")

    lines.extend(["", "---", "", "## Extended corpus", ""])

    for group, rows in group_examples(ex_rows).items():
        if group.startswith("euclid/"):
            book = group.split("/")[1]
            index_path = f"third-party/flow-verify/euclid-{book}.md"
            label = book.replace("-", " ").title()
            lines.append(f"### [{label}]({index_path}) ({len(rows)} proofs)")
        else:
            label = group.replace("/", " → ").replace("-", " ").title()
            lines.append(f"### {label} ({len(rows)})")
        lines.append("")
        lines.append("| Proof | Summary |")
        lines.append("|-------|---------|")
        for row in rows[:20] if group.startswith("euclid/") else rows:
            summary = (row["summary"] or "—").replace("|", "\\|")
            title = short_euclid_label(row["rel"]) if group.startswith("euclid/") else Path(row["rel"]).stem
            link = f"[{title}]({row['wiki_path']})"
            lines.append(f"| {link} | {summary} |")
        if group.startswith("euclid/") and len(rows) > 20:
            book = group.split("/")[1]
            lines.append(f"| … | [{len(rows)} total — see Euclid index](third-party/flow-verify/euclid-{book}.md) |")
        lines.append("")

    catalog = OUT / "third-party" / "flow-verify-catalog.md"
    catalog.parent.mkdir(parents=True, exist_ok=True)
    catalog.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_euclid_indexes(ex_rows: list[dict]) -> list[dict]:
    """Generate per-book index pages; return nav items."""
    nav_items: list[dict] = []
    groups = group_examples(ex_rows)

    for group, rows in groups.items():
        if not group.startswith("euclid/"):
            continue
        book = group.split("/")[1]
        roman = {"book-i": "I", "book-ii": "II", "book-iii": "III", "book-iv": "IV", "book-v": "V", "book-vi": "VI"}
        label = f"Euclid Book {roman.get(book, book)}"
        index_path = f"third-party/flow-verify/euclid-{book}.md"
        out_file = OUT / index_path

        lines = [
            f"# {label}",
            "",
            f"> **{len(rows)}** propositions from *Elements*, stepped proofs with numbered deductive traces.",
            "",
            "| # | Proposition |",
            "|---|-------------|",
        ]
        for row in rows:
            prop = short_euclid_label(row["rel"])
            summary = (row["summary"] or row["title"])[:80].replace("|", "\\|")
            link = f"[{prop} — {summary}]({row['wiki_path']})"
            num = re.search(r"prop-(\d+)", row["rel"])
            num_str = num.group(1) if num else "—"
            lines.append(f"| {num_str} | {link} |")

        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        nav_items.append({"label": label, "path": index_path, "badge": str(len(rows))})

    return nav_items


CHANGELOG_HEADING = re.compile(r"^## \[(?P<ver>[^\]]+)\](?: - (?P<date>.+))?$")


def parse_changelog_versions() -> list[dict]:
    changelog = DOCS / "project" / "CHANGELOG.md"
    if not changelog.exists():
        return [{"id": "0.7.0", "label": "v0.7.0", "date": "", "latest": True, "archived": True}]

    seen: set[str] = set()
    versions: list[dict] = []
    for line in changelog.read_text(encoding="utf-8").splitlines():
        m = CHANGELOG_HEADING.match(line.strip())
        if not m:
            continue
        ver = m.group("ver").strip()
        if ver in ("Unreleased",) or ver in seen:
            continue
        seen.add(ver)
        versions.append(
            {
                "id": ver,
                "label": f"v{ver}" if not ver.startswith("v") else ver,
                "date": (m.group("date") or "").strip(),
                "latest": False,
                "archived": False,
            }
        )

    # Newest first (file lists older entries first in some sections — re-sort by semver-ish)
    def ver_key(v: dict) -> tuple:
        parts = []
        for p in re.split(r"[.\-]", v["id"]):
            parts.append(int(p) if p.isdigit() else 0)
        return tuple(parts)

    versions.sort(key=ver_key, reverse=True)
    if versions:
        versions[0]["latest"] = True
        versions[0]["archived"] = True
    return versions


def write_versions_json(versions: list[dict]) -> None:
    current = versions[0]["id"] if versions else "0.7.0"
    payload = {
        "current": current,
        "versions": versions,
    }
    (OUT / "versions.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_releases_index(versions: list[dict]) -> None:
    lines = [
        "# Release History",
        "",
        "> Pick a version from the header dropdown, or jump to release notes below.",
        "",
        "| Version | Date | Status | Notes |",
        "|---------|------|--------|-------|",
    ]
    for v in versions:
        status = "**latest**" if v.get("latest") else ("archived" if v.get("archived") else "snapshot TBD")
        slug = v["id"].lower().replace(".", "-")
        link = f"[{v['label']}](project/CHANGELOG.md#v-{slug})"
        date = v.get("date") or "—"
        lines.append(f"| {link} | {date} | {status} | [Full notes](project/CHANGELOG.md#v-{slug}) |")

    lines.extend(
        [
            "",
            "---",
            "",
            "See the [full changelog](project/CHANGELOG.md) for detailed release notes, "
            "security audits, and migration guides.",
            "",
            "Documentation archives per version are planned — see [Wiki Roadmap](wiki-roadmap.md) Phase 4.",
        ]
    )
    (OUT / "releases.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_tutorial_exercises() -> None:
    """Extract runnable tutorial snippets for the interactive tutorials app."""
    lessons: list[dict] = []
    track_order = {"beginner": 0, "intermediate": 1, "advanced": 2}

    for md_path in sorted((DOCS / "tutorials").glob("*.md")):
        if md_path.name == "README.md":
            continue
        text = md_path.read_text(encoding="utf-8", errors="replace")
        track = md_path.stem
        exercise = 0

        for block in re.finditer(
            r"```(?:flow(?:\s+(?:run|interactive))?)\n(.*?)```",
            text,
            re.DOTALL,
        ):
            code = block.group(1).strip()
            if "function main" not in code:
                continue

            # Find nearest preceding heading
            pos = block.start()
            before = text[:pos]
            sec_m = list(re.finditer(r"^## (.+)$", before, re.MULTILINE))
            sub_m = list(re.finditer(r"^### (.+)$", before, re.MULTILINE))
            section = sec_m[-1].group(1) if sec_m else track.title()
            part_title = sub_m[-1].group(1) if sub_m else "Exercise"
            exercise += 1

            lessons.append(
                {
                    "id": f"{track}-{exercise}",
                    "track": track,
                    "title": part_title,
                    "section": section,
                    "description": f"{section} — edit and run in the browser.",
                    "code": code,
                }
            )

    lessons.sort(key=lambda l: (track_order.get(l["track"], 9), l["id"]))
    out_dir = OUT / "tutorials"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"generated": date.today().isoformat(), "lessons": lessons}
    (out_dir / "exercises.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_nav(lib_rows: list[dict], ex_rows: list[dict], euclid_nav: list[dict]) -> None:
    other_groups = []
    for group, rows in group_examples(ex_rows).items():
        if group.startswith("euclid/"):
            continue
        other_groups.append(
            {
                "label": proof_group_label(group, rows),
                "path": "third-party/flow-verify-catalog.md",
            }
        )

    nav = {
        "default": "wiki-home.md",
        "tabs": [
            {"id": "all", "label": "All"},
            {"id": "start", "label": "Start"},
            {"id": "lang", "label": "Language"},
            {"id": "stdlib", "label": "Library"},
            {"id": "thirdparty", "label": "Third-Party"},
            {"id": "learn", "label": "Tutorials"},
            {"id": "tooling", "label": "Tooling"},
            {"id": "project", "label": "Project"},
        ],
        "sections": [
            {
                "id": "start",
                "tab": "start",
                "title": "Getting Started",
                "items": [
                    {"label": "Home", "path": "wiki-home.md"},
                    {"label": "Quick Start", "path": "getting-started.md"},
                    {"label": "Changelog", "path": "project/CHANGELOG.md"},
                    {"label": "Release History", "path": "releases.md"},
                    {"label": "Comparison", "path": "comparison.md"},
                    {"label": "Interactive Tutorials", "path": "tutorials/index.html", "external": True},
                    {"label": "Playground", "path": "playground/index.html", "external": True},
                ],
            },
            {
                "id": "lang-ref",
                "tab": "lang",
                "title": "Language Reference",
                "items": [
                    {"label": "Language Spec", "path": "LANGUAGE_SPEC.md"},
                    {"label": "Grammar", "path": "language/grammar.md"},
                    {"label": "Formal EBNF", "path": "grammar.ebnf"},
                    {"label": "Overview", "path": "language/overview.md"},
                    {"label": "Syntax", "path": "language/syntax.md"},
                    {"label": "Types", "path": "language/types.md"},
                    {"label": "Variables", "path": "language/variables.md"},
                    {"label": "Functions", "path": "language/functions.md"},
                    {"label": "Modules", "path": "language/modules.md"},
                    {"label": "Graphics", "path": "language/graphics.md"},
                    {"label": "Design Notes", "path": "language/language_design.md"},
                ],
            },
            {
                "id": "stdlib",
                "tab": "stdlib",
                "title": "Standard Library",
                "items": [
                    {"label": "API Reference", "path": "library/stdlib-reference.md"},
                    {"label": "Core", "path": "library/core.md"},
                    {"label": "Autodiff", "path": "library/autodiff.md"},
                    {"label": "Audio DSP", "path": "library/audio.md"},
                    {"label": "Memory", "path": "library/memory.md"},
                ],
            },
            {
                "id": "thirdparty",
                "tab": "thirdparty",
                "title": "Third-Party Libraries",
                "items": [
                    {"label": "Overview", "path": "third-party/README.md"},
                    {"label": "flow-verify", "path": "third-party/flow-verify.md"},
                    {"label": "Proof Catalog", "path": "third-party/flow-verify-catalog.md"},
                ],
            },
            {
                "id": "verify-docs",
                "tab": "thirdparty",
                "title": "flow-verify — Design",
                "items": [
                    {"label": "Verification Spec", "path": "language/verification.md"},
                    {"label": "Claim Paths", "path": "language/epistemology.md"},
                    {"label": "Coordinates", "path": "language/claim-coordinates.md"},
                    {"label": "Proof Book", "path": "language/math-proof-book.md"},
                    {"label": "Mathlib Roadmap", "path": "language/mathlib-equivalence-toc.md"},
                ],
            },
            {
                "id": "proofs-euclid",
                "tab": "thirdparty",
                "title": "flow-verify — Euclid",
                "collapsed": True,
                "items": euclid_nav,
            },
            {
                "id": "proofs-corpus",
                "tab": "thirdparty",
                "title": "flow-verify — Corpus",
                "collapsed": True,
                "items": other_groups,
            },
            {
                "id": "learn",
                "tab": "learn",
                "title": "Tutorials",
                "items": [
                    {"label": "Interactive App", "path": "tutorials/index.html", "external": True},
                    {"label": "Beginner", "path": "tutorials/beginner.md"},
                    {"label": "Intermediate", "path": "tutorials/intermediate.md"},
                    {"label": "Advanced", "path": "tutorials/advanced.md"},
                ],
            },
            {
                "id": "tooling",
                "tab": "tooling",
                "title": "Tooling & Targets",
                "items": [
                    {"label": "Development", "path": "DEVELOPMENT.md"},
                    {"label": "Python Target", "path": "python-target.md"},
                    {"label": "What's Next", "path": "NEXT.md"},
                ],
            },
            {
                "id": "wiki-meta",
                "tab": "project",
                "title": "Documentation",
                "items": [
                    {"label": "Wiki Strategy", "path": "wiki-strategy.md"},
                    {"label": "Wiki Roadmap", "path": "wiki-roadmap.md"},
                    {"label": "Language Roadmap", "path": "project/language-roadmap.md"},
                ],
            },
            {
                "id": "project",
                "tab": "project",
                "title": "Project",
                "items": [
                    {"label": "Contributing", "path": "project/CONTRIBUTING.md"},
                    {"label": "Changelog", "path": "project/CHANGELOG.md"},
                    {"label": "Structure", "path": "project/PROJECT_STRUCTURE.md"},
                ],
            },
            {
                "id": "research",
                "tab": "project",
                "title": "Research",
                "items": [
                    {"label": "Research Paper", "path": "research/FLOW_RESEARCH_PAPER.md"},
                    {"label": "Turing Proof", "path": "research/turing_proof.md"},
                ],
            },
        ],
    }

    (OUT / "wiki-nav.json").write_text(json.dumps(nav, indent=2) + "\n", encoding="utf-8")


def build_search_index(lib_rows: list[dict], ex_rows: list[dict]) -> None:
    entries: list[dict] = []

    def add_page(path: Path, wiki_path: str) -> None:
        if not path.exists() or path.suffix not in {".md", ".ebnf"}:
            return
        text = path.read_text(encoding="utf-8", errors="replace")
        title = proof_title(text) or ""
        if not title:
            for line in text.splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
        title = title or path.stem
        body = re.sub(r"[#*`\[\]()]", " ", text)
        body = re.sub(r"\s+", " ", body)[:2000]
        entries.append(
            {
                "path": wiki_path,
                "title": title,
                "text": body,
                "category": page_category(wiki_path),
            }
        )

    for md in OUT.rglob("*.md"):
        if "flow-verify/proofs" in md.as_posix():
            continue
        add_page(md, md.relative_to(OUT).as_posix())

    for row in lib_rows + ex_rows:
        p = OUT / row["wiki_path"]
        if p.exists():
            text = p.read_text(encoding="utf-8", errors="replace")
            entries.append(
                {
                    "path": row["wiki_path"],
                    "title": row["title"],
                    "text": (row["summary"] + " " + text[:500]).strip(),
                    "category": "proof",
                }
            )

    (OUT / "search-index.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")


def write_llms_txt() -> None:
    """Machine-readable doc index (Mojo-style llms.txt)."""
    lines = [
        "# Flow Programming Language Documentation",
        "",
        "> https://abhishek-shivakumar.com/transpile/",
        "",
        "## Start",
        "- [Home](wiki-home.md): Language overview and quick links",
        "- [Quick Start](getting-started.md): Install and first program",
        "- [Comparison](comparison.md): Flow vs C, Rust, Zig, Mojo",
        "- [Interactive Tutorials](tutorials/index.html): Browser lessons",
        "",
        "## Language Reference",
        "- [Language Spec](LANGUAGE_SPEC.md)",
        "- [Grammar](language/grammar.md)",
        "- [Types](language/types.md)",
        "- [Functions](language/functions.md)",
        "- [Modules](language/modules.md)",
        "",
        "## Standard Library",
        "- [API Reference](library/stdlib-reference.md)",
        "",
        "## Tutorials",
        "- [Beginner](tutorials/beginner.md)",
        "- [Intermediate](tutorials/intermediate.md)",
        "- [Advanced](tutorials/advanced.md)",
        "",
        "## Third-Party",
        "- [flow-verify](third-party/flow-verify.md): Formal math library (optional)",
        "- [Proof Catalog](third-party/flow-verify-catalog.md)",
        "",
        "## Tooling",
        "- [Development](DEVELOPMENT.md)",
        "",
        "Append `.md` to any doc path for raw markdown, e.g. `getting-started.md`.",
    ]
    (OUT / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_site_shell() -> None:
    shell_files = (
        "index.html",
        "wiki.css",
        "wiki.js",
        "grammar-viewer.js",
        "flow-compile.js",
        "tutorial-runner.js",
        "tutorial-runner.css",
    )
    for name in shell_files:
        src = SITE / name
        if src.exists():
            shutil.copy2(src, OUT / name)

    vendor_src = SITE / "vendor"
    if vendor_src.exists():
        copy_tree(vendor_src, OUT / "vendor")

    tutorials_src = SITE / "tutorials"
    if tutorials_src.exists():
        out_tutorials = OUT / "tutorials"
        out_tutorials.mkdir(parents=True, exist_ok=True)
        for item in tutorials_src.iterdir():
            if item.is_file():
                shutil.copy2(item, out_tutorials / item.name)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    copy_docs()
    copy_extras()
    lib_rows, ex_rows = sync_proofs()
    euclid_nav = write_euclid_indexes(ex_rows)
    versions = parse_changelog_versions()
    write_catalog(lib_rows, ex_rows)
    write_versions_json(versions)
    write_releases_index(versions)
    write_nav(lib_rows, ex_rows, euclid_nav)
    build_search_index(lib_rows, ex_rows)
    copy_site_shell()
    build_tutorial_exercises()
    write_llms_txt()

    total = len(lib_rows) + len(ex_rows)
    print(f"Wiki built → {OUT}")
    print(f"  {total} proofs · {len(euclid_nav)} Euclid books · nav + search index generated")


if __name__ == "__main__":
    main()