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

VERIFY_LIB_ROOT = ROOT / "lib" / "verify"
VERIFY_EXAMPLES_ROOT = ROOT / "examples" / "verify"
IMPORT_LINE_RE = re.compile(r"^\s*import\s+(\S+)", re.MULTILINE)


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


def rewrite_repo_href_for_wiki(href: str) -> str:
    """Map docs/ VISION links in ROADMAP.md to wiki paths under project/."""
    path, frag = (href.split("#", 1) + [""])[:2]
    frag = f"#{frag}" if frag else ""

    if path.startswith("docs/"):
        return f"../{path[len('docs/'):]}{frag}"
    if path == "VISION.md":
        return f"../VISION.md{frag}"
    # examples/, benchmarks/, compiler/ stay repo-relative; the link checker
    # accepts those when the files exist in the checkout.
    return href


def rewrite_repo_links_for_wiki(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return f"]({rewrite_repo_href_for_wiki(match.group(1))})"

    return re.sub(r"\]\(([^)]+)\)", repl, text)


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
        dest.write_text(
            rewrite_repo_links_for_wiki(roadmap.read_text(encoding="utf-8")),
            encoding="utf-8",
        )

    results = ROOT / "benchmarks" / "suite" / "RESULTS.md"
    if results.exists():
        dest = OUT / "project" / "benchmark-results.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(results, dest)

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
            # foo.proof.md → foo.proof.svg (with_suffix only replaces .md)
            svg = path.with_name(path.name.replace(".proof.md", ".proof.svg"))
            if not svg.exists():
                svg = path.with_suffix(".svg")
            if svg.exists():
                shutil.copy2(svg, target.parent / svg.name)
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


def build_proof_graph() -> dict:
    """Static proof-dependency graph for the flow-verify catalog (issue #133).

    Design choice — nodes are *modules* (one per .flow file), not individual
    theorems: a module holds dozens of theorems, so per-theorem nodes would
    blow past any sane node budget without adding real structure to a
    dependency view. `lib/verify` is small (~24 files) and is included in
    full as the graph's anchor set. Of `examples/verify`, only
    `math/derived/*.flow` actually uses the `import` mechanism — every other
    example directory (euclid, geometry, circuits, analysis, transforms,
    systems, …) is a self-contained, zero-import proof — so those ~1000
    files contribute no edges and are left out entirely rather than padding
    the graph with disconnected nodes. In practice this keeps the graph at a
    few hundred nodes, comfortably under the ~800 cap called out in the
    issue, with no sampling/truncation needed.
    """

    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    edge_seen: set[tuple[str, str]] = set()

    def ensure_node(node_id: str, label: str, group: str, path: str | None) -> None:
        if node_id not in nodes:
            entry = {"id": node_id, "label": label, "group": group}
            if path:
                entry["path"] = path
            nodes[node_id] = entry
        elif path and "path" not in nodes[node_id]:
            nodes[node_id]["path"] = path

    def proof_doc_path(prefix: str, rel: str) -> str | None:
        proof_rel = rel[: -len(".flow")] + ".proof.md"
        src_root = VERIFY_LIB_ROOT if prefix == "lib" else VERIFY_EXAMPLES_ROOT
        if not (src_root / proof_rel).exists():
            return None
        return f"third-party/flow-verify/proofs/{prefix}/{proof_rel}"

    def resolve_target(token: str, home_dotted_dir: str) -> tuple[str, str, str, str | None] | None:
        token = token.strip()
        if not token:
            return None
        if token.startswith('"'):
            # Quoted file-path import (e.g. a stdlib companion) — outside the
            # verify/examples module tree, kept as a small "external" leaf.
            raw = token.strip('"')
            return f"external.{raw}", Path(raw).stem, "external", None
        if token.startswith("."):
            # Relative import: `.Sibling` resolves inside the importer's own directory.
            name = token[1:].split("/")[0]
            if not name:
                return None
            node_id = f"{home_dotted_dir}.{name}"
            if node_id.startswith("verify."):
                group, id_prefix = "lib", "verify"
            else:
                group, id_prefix = "examples", "examples"
            rel = node_id[len(id_prefix) + 1 :].replace(".", "/") + ".flow"
            return node_id, name, group, proof_doc_path(group, rel)
        # Absolute module path, e.g. "verify.Nat" or "verify.Nat/+" (operator import).
        base = token.split("/")[0]
        label = base.split(".")[-1]
        if base.startswith("verify."):
            rel = base[len("verify.") :].replace(".", "/") + ".flow"
            return base, label, "lib", proof_doc_path("lib", rel)
        return base, label, "external", None

    # (root, id-prefix used inside node ids, group label, include-even-without-imports)
    sources = (
        (VERIFY_LIB_ROOT, "verify", "lib", True),
        (VERIFY_EXAMPLES_ROOT, "examples", "examples", False),
    )
    for root_dir, id_prefix, group, include_all in sources:
        if not root_dir.exists():
            continue
        for flow_path in sorted(root_dir.rglob("*.flow")):
            rel = flow_path.relative_to(root_dir).as_posix()
            text = flow_path.read_text(encoding="utf-8", errors="replace")
            import_tokens = [m.group(1) for m in IMPORT_LINE_RE.finditer(text)]

            if not include_all and not import_tokens:
                continue  # examples/*: only import-connected modules earn a node

            node_id = f"{id_prefix}.{rel[: -len('.flow')].replace('/', '.')}"
            label = Path(rel).stem
            ensure_node(node_id, label, group, proof_doc_path(group, rel))

            home_dotted_dir = node_id.rsplit(".", 1)[0]
            for token in import_tokens:
                resolved = resolve_target(token, home_dotted_dir)
                if not resolved:
                    continue
                target_id, target_label, target_group, target_path = resolved
                ensure_node(target_id, target_label, target_group, target_path)
                key = (node_id, target_id)
                if node_id != target_id and key not in edge_seen:
                    edge_seen.add(key)
                    edges.append({"from": node_id, "to": target_id})

    return {
        "nodes": sorted(nodes.values(), key=lambda n: (n["group"], n["id"])),
        "edges": sorted(edges, key=lambda e: (e["from"], e["to"])),
    }


def write_proof_graph() -> dict:
    graph = build_proof_graph()
    (OUT / "proof-graph.json").write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    return graph


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
    """Generate releases.md from docs/project/CHANGELOG.md (copied into the wiki as-is)."""
    lines = [
        "# Release History",
        "",
        "> **Source of truth:** [`project/CHANGELOG.md`](project/CHANGELOG.md) — copied from "
        "`docs/project/CHANGELOG.md` on every wiki build. This page is generated by "
        "`scripts/build_wiki.py`; do not edit it by hand.",
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
            "## Release workflow",
            "",
            "1. Edit `docs/project/CHANGELOG.md` (add a `## [X.Y.Z] - YYYY-MM-DD` section).",
            "2. Run `python3 scripts/build_wiki.py` — copies the changelog and regenerates "
            "`versions.json` + this index.",
            "3. Deploy with `python3 scripts/deploy_wiki.py` when ready to publish.",
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
    track_order = {
        "beginner": 0,
        "control": 1,
        "functions": 2,
        "structs": 3,
        "arrays": 4,
        "strings": 5,
        "pointers": 6,
        "memory": 7,
        "errors": 8,
        "intermediate": 9,
        "concurrency": 10,
        "algorithms": 11,
        "systems": 12,
        "effects-basics": 13,
        "autodiff-basics": 14,
        "audio-basics": 15,
        "advanced": 16,
        "dynamics": 17,
        "projects": 18,
    }

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

    def lesson_key(lesson: dict) -> tuple:
        m = re.search(r"-(\d+)$", lesson["id"])
        n = int(m.group(1)) if m else 0
        return (track_order.get(lesson["track"], 50), n)

    lessons.sort(key=lesson_key)
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
                    {"label": "Benchmarks", "path": "project/benchmark-results.md"},
                    {"label": "Interactive Tutorials", "path": "tutorials/index.html", "external": True},
                    {"label": "Playground", "path": "playground/index.html", "external": True},
                ],
            },
            {
                "id": "lang-ref",
                "tab": "lang",
                "title": "Language Reference",
                "items": [
                    {"label": "Spec Index", "path": "language/spec-index.md"},
                    {"label": "Language Spec", "path": "LANGUAGE_SPEC.md"},
                    {"label": "Grammar", "path": "language/grammar.md"},
                    {"label": "Formal EBNF", "path": "grammar.ebnf"},
                    {"label": "Overview", "path": "language/overview.md"},
                    {"label": "Syntax", "path": "language/syntax.md"},
                    {"label": "Types", "path": "language/types.md"},
                    {"label": "Variables", "path": "language/variables.md"},
                    {"label": "Functions", "path": "language/functions.md"},
                    {"label": "Modules", "path": "language/modules.md"},
                    {"label": "Effects Showcase", "path": "effects-showcase.md"},
                    {"label": "Async via Effects", "path": "language/async-effects.md"},
                    {"label": "Graphics", "path": "language/graphics.md"},
                    {"label": "WebAssembly", "path": "language/wasm.md"},
                    {"label": "Design Notes", "path": "language/language_design.md"},
                ],
            },
            {
                "id": "stdlib",
                "tab": "stdlib",
                "title": "Standard Library",
                "items": [
                    {"label": "API Reference", "path": "library/stdlib-reference.md"},
                    {"label": "API (generated)", "path": "library/stdlib-api.md"},
                    {"label": "Core", "path": "library/core.md"},
                    {"label": "Autodiff", "path": "library/autodiff.md"},
                    {"label": "Autodiff Guide", "path": "library/autodiff-guide.md"},
                    {"label": "Audio DSP", "path": "library/audio.md"},
                    {"label": "RT Safety", "path": "library/rt-safety.md"},
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
                    {"label": "Parser Status", "path": "third-party/flow-verify-parser-status.md"},
                    {"label": "Proof Catalog", "path": "third-party/flow-verify-catalog.md"},
                    {"label": "Proof Dependency Graph", "path": "third-party/proof-graph.md"},
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
                    {"label": "Control Flow", "path": "tutorials/control.md"},
                    {"label": "Functions", "path": "tutorials/functions.md"},
                    {"label": "Structs", "path": "tutorials/structs.md"},
                    {"label": "Arrays", "path": "tutorials/arrays.md"},
                    {"label": "Strings", "path": "tutorials/strings.md"},
                    {"label": "Pointers", "path": "tutorials/pointers.md"},
                    {"label": "Manual Memory", "path": "tutorials/memory.md"},
                    {"label": "Errors", "path": "tutorials/errors.md"},
                    {"label": "Intermediate", "path": "tutorials/intermediate.md"},
                    {"label": "Algorithms", "path": "tutorials/algorithms.md"},
                    {"label": "Systems", "path": "tutorials/systems.md"},
                    {"label": "Effects Basics", "path": "tutorials/effects-basics.md"},
                    {"label": "Autodiff Basics", "path": "tutorials/autodiff-basics.md"},
                    {"label": "Audio Basics", "path": "tutorials/audio-basics.md"},
                    {"label": "Advanced", "path": "tutorials/advanced.md"},
                    {"label": "Dynamics", "path": "tutorials/dynamics.md"},
                    {"label": "Mini Projects", "path": "tutorials/projects.md"},
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
                    {"label": "Self-Hosting", "path": "project/self-hosting.md"},
                ],
            },
            {
                "id": "project",
                "tab": "project",
                "title": "Project",
                "items": [
                    {"label": "Contributing", "path": "project/CONTRIBUTING.md"},
                    {"label": "Changelog", "path": "project/CHANGELOG.md"},
                    {"label": "Benchmarks", "path": "project/benchmark-results.md"},
                    {"label": "Structure", "path": "project/PROJECT_STRUCTURE.md"},
                    {"label": "Package Registry", "path": "project/package-registry.md"},
                    {"label": "Self-Hosting Plan", "path": "project/self-hosting.md"},
                    {"label": "Release Process", "path": "project/RELEASING.md"},
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
    """Build search-index.json (always) — also the source for optional Pagefind indexing."""
    entries: list[dict] = []
    # Larger snippets improve local fallback scoring and Pagefind excerpts.
    body_limit = 6000
    proof_body_limit = 1500

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
        body = re.sub(r"\s+", " ", body)[:body_limit]
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

    # Ensure tutorial HTML shell is searchable by title even without markdown twin.
    tutorials_index = OUT / "tutorials" / "index.html"
    if tutorials_index.exists() and not any(e["path"] == "tutorials/index.html" for e in entries):
        entries.append(
            {
                "path": "tutorials/index.html",
                "title": "Interactive Tutorials",
                "text": "Interactive browser tutorials concurrency memory arrays strings structs "
                "pointers functions control errors algorithms audio autodiff effects systems projects",
                "category": "tutorial",
            }
        )

    for row in lib_rows + ex_rows:
        p = OUT / row["wiki_path"]
        if p.exists():
            text = p.read_text(encoding="utf-8", errors="replace")
            entries.append(
                {
                    "path": row["wiki_path"],
                    "title": row["title"],
                    "text": (row["summary"] + " " + text[:proof_body_limit]).strip(),
                    "category": "proof",
                }
            )

    (OUT / "search-index.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")


def run_pagefind() -> None:
    """Run Pagefind indexer when node/npx are available; skip otherwise."""
    import os
    import subprocess
    import sys

    if os.environ.get("FLOW_WIKI_SKIP_PAGEFIND"):
        print("Pagefind skipped: FLOW_WIKI_SKIP_PAGEFIND set")
        return
    script = ROOT / "scripts" / "build_pagefind.sh"
    if not script.exists():
        print("Pagefind skipped: scripts/build_pagefind.sh missing")
        return
    env = os.environ.copy()
    env["FLOW_WIKI_OUT"] = str(OUT)
    try:
        # npx fetches the indexer on first use and can stall indefinitely on a
        # slow or offline network; the local search index is a fine fallback.
        result = subprocess.run(["bash", str(script)], cwd=ROOT, env=env, timeout=180)
    except subprocess.TimeoutExpired:
        print("Pagefind timed out after 180s (search falls back to search-index.json)", file=sys.stderr)
        return
    if result.returncode != 0:
        print("Pagefind step exited non-zero (search falls back to search-index.json)", file=sys.stderr)


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
        "- [Spec Index](language/spec-index.md)",
        "- [Language Spec](LANGUAGE_SPEC.md)",
        "- [Grammar](language/grammar.md)",
        "- [Types](language/types.md)",
        "- [Functions](language/functions.md)",
        "- [Modules](language/modules.md)",
        "",
        "## Standard Library",
        "- [API Reference](library/stdlib-reference.md)",
        "- [Audio DSP](library/audio.md)",
        "- [RT Safety](library/rt-safety.md)",
        "- [Memory](library/memory.md)",
        "",
        "## Tutorials",
        "- [Beginner](tutorials/beginner.md)",
        "- [Intermediate](tutorials/intermediate.md)",
        "- [Advanced](tutorials/advanced.md)",
        "",
        "## Third-Party",
        "- [flow-verify](third-party/flow-verify.md): Formal math library (optional)",
        "- [Parser Status](third-party/flow-verify-parser-status.md): verify corpus vs. shipped parser",
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
        "flow-lang.js",
        "flow-editor.js",
        "tutorial-runner.js",
        "tutorial-runner.css",
        "proof-graph.html",
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


def generate_stdlib_api() -> None:
    """Refresh docs/library/stdlib-api.md from lib/stdlib sources."""
    script = ROOT / "scripts" / "gen_stdlib_docs.py"
    if script.exists():
        import subprocess
        import sys

        subprocess.run([sys.executable, str(script)], check=False)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    generate_stdlib_api()
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
    graph = write_proof_graph()
    run_pagefind()

    total = len(lib_rows) + len(ex_rows)
    pf = OUT / "pagefind" / "pagefind.js"
    pf_note = " · Pagefind index" if pf.exists() else " · Pagefind skipped (local search-index.json)"
    print(f"Wiki built → {OUT}")
    print(f"  {total} proofs · {len(euclid_nav)} Euclid books · nav + search index generated{pf_note}")
    print(f"  proof-graph.json: {len(graph['nodes'])} nodes · {len(graph['edges'])} edges")


if __name__ == "__main__":
    main()