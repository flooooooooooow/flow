#!/usr/bin/env python3
"""Validate internal wiki links after build."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "build" / "wiki"

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

SKIP_FILES = {
    "README.md",
    "mkdocs.yml",
}

# Repo paths that are intentionally linked from docs but not mirrored into the wiki.
REPO_LINK_PREFIXES = (
    "examples/",
    "benchmarks/",
    "compiler/",
    "runtime/",
    "lib/",
    "src/",
    "tests/",
    "plugins/",
    "scripts/",
    "registry/",
)


def resolve_link(source: Path, href: str) -> Path | None:
    """Return a path that must exist, or None if the link should be skipped."""
    href = href.split("#")[0].strip()
    if not href or href.startswith(("http://", "https://", "mailto:", "#")):
        return None
    if href.endswith(".html"):
        return None

    relative = (WIKI / source.parent / href).resolve()
    if relative.is_relative_to(WIKI) and relative.exists():
        return relative

    # Repo-root docs/ links still appear in some project pages before rewrite.
    if href.startswith("docs/"):
        stripped = (WIKI / href[len("docs/") :]).resolve()
        if stripped.is_relative_to(WIKI):
            return stripped

    absolute = (WIKI / href).resolve()
    if absolute.is_relative_to(WIKI) and absolute.exists():
        return absolute

    # Allow repo-root links that point at real tracked files outside the wiki tree.
    if href.startswith(REPO_LINK_PREFIXES) or href in {"VISION.md", "ROADMAP.md"}:
        repo_target = (ROOT / href).resolve()
        if repo_target.is_relative_to(ROOT) and repo_target.exists():
            return repo_target

    # A page copied out of the repo (examples/**/README.md) links to its
    # siblings by bare name. wiki.js sends every non-.md file under a source
    # directory to GitHub rather than serving it, so the file has to exist in
    # the repo, not in the built site.
    if source.as_posix().startswith(REPO_LINK_PREFIXES):
        sibling = (ROOT / source.parent / href).resolve()
        if (
            sibling.is_relative_to(ROOT)
            and sibling.exists()
            and sibling.suffix != ".md"
        ):
            return sibling

    if absolute.is_relative_to(WIKI):
        return absolute
    return None


def main() -> int:
    if not WIKI.exists():
        print("Run scripts/build_wiki.py first", file=sys.stderr)
        return 1

    errors: list[str] = []
    for md in WIKI.rglob("*.md"):
        rel = md.relative_to(WIKI)
        if rel.as_posix() in SKIP_FILES:
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        for href in LINK_RE.findall(text):
            target = resolve_link(rel, href)
            if target is None or target.exists():
                continue
            errors.append(f"{rel}: broken link → {href}")

    if errors:
        print(f"Found {len(errors)} broken link(s):", file=sys.stderr)
        for err in errors[:40]:
            print(f"  {err}", file=sys.stderr)
        if len(errors) > 40:
            print(f"  … and {len(errors) - 40} more", file=sys.stderr)
        return 1

    print("Wiki links OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
