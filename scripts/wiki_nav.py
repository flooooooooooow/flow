#!/usr/bin/env python3
"""The wiki sidebar, loaded from one manifest and validated.

`docs/nav.json` is the single source of truth. Before this existed the same
information was hand-maintained in five places inside `scripts/build_wiki.py`
and `mkdocs.yml`:

    write_nav()          the sidebar itself
    page_category()      the Pagefind category filter
    write_llms_txt()     a third hand-written index
    build_tutorial_exercises()   track ordering for the lessons app
    mkdocs.yml nav:      a separate navigation over the same files

They had already drifted. `mkdocs.yml` listed pages the sidebar omitted and
omitted the entire Book. The sidebar carried an entry for
`project/PROJECT_STRUCTURE.md`, a file that only exists under `archive/`, and
nothing ever checked, so it shipped as a dead link.

Two things are validated on every build, and both are failures rather than
warnings:

* every nav path resolves to a real page
* every page under `docs/` is either in the nav or listed in `unlisted` with a
  written reason

The second is the one that matters for the wiki's purpose. 50 of 172 pages were
in no sidebar and 23 had no inbound link from anywhere, which for a reference
manual means the information exists and cannot be found.

JSON rather than YAML because the wiki CI job runs bare `python3` with no
`setup-python` step and no `pip install`, so anything this module touches has to
be in the standard library.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MANIFEST = DOCS / "nav.json"

# Trees that are not documentation pages: vendored, generated, or presentation.
SKIP_DIRS = {
    "formal",  # vendored Lean/mathlib
    "playground",  # a web app, copied verbatim
    "assets",
    "stylesheets",
    "generated",
    "demos",  # gallery media, indexed by its own overview pages
}


# Pages that exist only in build/wiki, written by build_wiki.py from sources
# outside docs/. check_doc_links.py keeps an equivalent list for the same reason.
BUILD_GENERATED = {
    "releases.md",
    "project/language-roadmap.md",  # from ROADMAP.md
    "project/benchmark-results.md",  # from benchmarks/suite/RESULTS.md
    "third-party/flow-verify-catalog.md",
    "project/example-status.md",  # from docs/generated/example-status.json
}


class NavError(Exception):
    """The manifest disagrees with what is on disk."""


def load(manifest: Path = MANIFEST) -> dict:
    return json.loads(manifest.read_text(encoding="utf-8"))


def iter_items(nav: dict) -> Iterator[tuple[dict, dict]]:
    """Yield (section, item) for every static entry."""
    for section in nav["sections"]:
        for item in section.get("items", []):
            yield section, item


def nav_paths(nav: dict) -> set[str]:
    """Every docs-relative path the sidebar points at, external links aside."""
    return {
        item["path"]
        for _, item in iter_items(nav)
        if item.get("path") and not item.get("external")
    }


def doc_pages(docs: Path = DOCS) -> set[str]:
    """Every markdown page under docs/ that a reader could be sent to."""
    pages = set()
    for path in docs.rglob("*.md"):
        rel = path.relative_to(docs)
        if rel.parts[0] in SKIP_DIRS:
            continue
        if any(part.startswith(".") for part in rel.parts):
            continue
        pages.add(rel.as_posix())
    return pages


def validate(nav: dict, docs: Path = DOCS) -> list[str]:
    """Return every problem with the manifest. Empty means it is consistent."""
    problems: list[str] = []

    tab_ids = {tab["id"] for tab in nav["tabs"]}
    seen_sections: set[str] = set()
    for section in nav["sections"]:
        if section["tab"] not in tab_ids:
            problems.append(
                f"section {section['id']!r} names tab {section['tab']!r}, which does not exist"
            )
        if section["id"] in seen_sections:
            problems.append(f"duplicate section id {section['id']!r}")
        seen_sections.add(section["id"])
        if "items" not in section and "generated" not in section:
            problems.append(
                f"section {section['id']!r} has neither items nor a generated source"
            )

    # Dead entries: the defect that shipped PROJECT_STRUCTURE.md to readers.
    for section, item in iter_items(nav):
        path = item.get("path")
        if not path or item.get("external"):
            continue
        if path in BUILD_GENERATED:
            continue
        # build_wiki also publishes the markdown under examples/, so a nav
        # entry may name a page that lives outside docs/ but is copied to the
        # same place in the built site.
        if not (docs / path).exists() and not (docs.parent / path).exists():
            problems.append(
                f"section {section['id']!r} points at {path!r}, which does not exist"
            )

    listed = nav_paths(nav)
    unlisted = nav.get("unlisted", {})
    for path, reason in unlisted.items():
        if not (docs / path).exists():
            problems.append(f"unlisted entry {path!r} does not exist")
        elif not str(reason).strip():
            problems.append(f"unlisted entry {path!r} needs a written reason")
        elif path in listed:
            problems.append(f"{path!r} is both in the nav and marked unlisted")

    orphans = doc_pages(docs) - listed - set(unlisted)
    for path in sorted(orphans):
        problems.append(
            f"{path!r} is in no nav section and has no unlisted reason"
        )

    if nav["default"] not in listed:
        problems.append(f"default page {nav['default']!r} is not in the nav")

    return problems


# --------------------------------------------------------------------------
# Derived views: one manifest, several consumers
# --------------------------------------------------------------------------

def sections_for_build(nav: dict, generated: dict[str, list]) -> list[dict]:
    """The sidebar, with the proof-corpus sections filled in.

    `generated` maps a section's "generated" key to the items computed from the
    proof corpus at build time.
    """
    out: list[dict] = []
    for section in nav["sections"]:
        entry = {k: v for k, v in section.items() if k != "generated"}
        if "generated" in section:
            entry["items"] = generated.get(section["generated"], [])
        out.append(entry)
    return out


def category_for(path: str, nav: dict) -> str:
    """Pagefind category, derived from the tab a page sits under.

    Previously a separate prefix-matching function, so a page could be filed
    under Language in the sidebar and reported as a guide in search.
    """
    tab_category = {
        "tutorials": "tutorial",
        "book": "guide",
        "lang": "reference",
        "stdlib": "reference",
        "tooling": "tooling",
        "thirdparty": "proof",
        "project": "guide",
        "gallery": "guide",
        "start": "guide",
    }
    for section, item in iter_items(nav):
        if item.get("path") == path:
            return tab_category.get(section["tab"], "guide")
    return "guide"


def main() -> int:
    nav = load()
    problems = validate(nav)
    listed = nav_paths(nav)
    unlisted = nav.get("unlisted", {})
    pages = doc_pages()

    print(f"nav sections   : {len(nav['sections'])}")
    print(f"nav entries    : {len(listed)}")
    print(f"docs pages     : {len(pages)}")
    print(f"unlisted       : {len(unlisted)}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for line in problems[:60]:
            print(f"  {line}")
        if len(problems) > 60:
            print(f"  ... and {len(problems) - 60} more")
        return 1
    print("\nnav is consistent with docs/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
