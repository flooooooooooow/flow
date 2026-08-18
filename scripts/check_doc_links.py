#!/usr/bin/env python3
"""Check that relative links in tracked markdown resolve to real files.

Complements scripts/check_wiki_links.py, which validates the *built* wiki under
build/wiki. This one validates the repo as it sits on GitHub, where most readers
meet it. The two catch different things: a link can be fine on the deployed site
and dead in the tree, or the reverse.

Some targets are generated into the site at build time by scripts/build_wiki.py
and never exist in the tree. Those are listed in GENERATED and skipped, because
they are correct for the audience that follows them.

Usage::

    python3 scripts/check_doc_links.py            # report and exit 1 on breakage
    python3 scripts/check_doc_links.py --list-ok  # also list what was skipped
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent

# [text](target) with an optional "title" after the target.
LINK = re.compile(r"\[[^\]]*\]\(\s*([^)\s]+?)\s*(?:\"[^\"]*\")?\)")

# Trees that are vendored, generated, or intentionally not link-clean.
SKIP_PREFIXES = (
    "docs/formal/",     # Lean mathlib vendor tree
    "third_party/",
    "node_modules/",
)

# Basenames produced by scripts/build_wiki.py into the published site. They are
# absent from the tree by design, so a link to one is not a defect.
GENERATED = frozenset(
    {
        "index.html",
        "proof-graph.html",
        "manifest.json",
        "flow-verify-catalog.md",
        "language-roadmap.md",
        "benchmark-results.md",
    }
)

# `#` is no longer here: a same-page anchor is not an external link, and
# leaving it in the skip list meant 55 of them were never validated.
EXTERNAL = ("http://", "https://", "mailto:", "<")


def tracked_paths() -> set[str]:
    """Every path git knows about, as posix strings relative to the repo root."""
    out = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=True,
    ).stdout.splitlines()
    return {line.strip() for line in out if line.strip()}


def tracked_markdown() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "*.md"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=True,
    ).stdout.split()
    return [f for f in out if not f.startswith(SKIP_PREFIXES)]


def resolves(source: str, target: str, tracked: set[str]) -> bool:
    """Does `target`, written inside `source`, point at something git tracks?

    Deliberately checked against the index rather than the filesystem. A working
    tree accumulates untracked build output (a stale docs/VISION.md, for one),
    and resolving against it lets a link pass locally and fail in CI's fresh
    checkout. Comparing against tracked paths makes the two agree.
    """
    base = PurePosixPath(source).parent
    try:
        resolved = os.path.normpath(str(base / target))
    except ValueError:
        return False
    if resolved.startswith(".."):     # escapes the repo; not ours to verify
        return True
    resolved = PurePosixPath(resolved).as_posix()
    if resolved in tracked:
        return True
    prefix = resolved.rstrip("/") + "/"      # directory link
    return any(p.startswith(prefix) for p in tracked)


HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
_ANCHOR_CACHE: dict[str, set[str]] = {}


def heading_slug(text: str) -> str:
    """GitHub/GFM heading id.

    Runs of dashes are deliberately not collapsed, because GitHub does not
    collapse them. `10. Domain / DSL Surfaces` loses the slash and keeps the
    spaces either side, giving `10-domain--dsl-surfaces`. site/wiki.js used to
    collapse, which left 11 anchors resolving on GitHub and dead on the
    published wiki.
    """
    text = re.sub(r"`", "", text)
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return text.replace(" ", "-")


def anchors_in(rel: str) -> set[str]:
    """Every heading id a page offers, including explicit HTML ids."""
    if rel in _ANCHOR_CACHE:
        return _ANCHOR_CACHE[rel]
    try:
        text = (ROOT / rel).read_text(errors="ignore")
    except OSError:
        text = ""
    slugs: set[str] = set()
    seen: dict[str, int] = {}
    for _, title in HEADING.findall(text):
        slug = heading_slug(title.strip())
        if not slug:
            continue
        # Repeated headings get -1, -2 ... exactly as GitHub numbers them.
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        slugs.add(slug if n == 0 else f"{slug}-{n}")
    # Hand-written anchors: <a id="x">, <a name="x">, id="x" on any element.
    slugs.update(re.findall(r'(?:id|name)="([^"]+)"', text))
    _ANCHOR_CACHE[rel] = slugs
    return slugs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list-ok",
        action="store_true",
        help="also list links skipped as build-time generated",
    )
    args = parser.parse_args()

    broken: list[tuple[str, str]] = []
    bad_anchors: list[tuple[str, str, str]] = []
    skipped: list[tuple[str, str]] = []
    checked = 0
    anchors_checked = 0
    tracked = tracked_paths()
    sources = tracked_markdown()

    for rel in sources:
        path = ROOT / rel
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for match in LINK.finditer(text):
            target = match.group(1)
            if target.startswith(EXTERNAL):
                continue
            bare, _, fragment = target.partition("#")
            if bare:
                checked += 1
            if not bare:
                # Same-page anchor: check it against this file's own headings.
                if fragment and rel.endswith(".md"):
                    anchors_checked += 1
                    if fragment not in anchors_in(rel):
                        bad_anchors.append((rel, target, rel))
                continue
            if resolves(rel, bare, tracked):
                fragment = target.partition("#")[2]
                if fragment:
                    target_rel = (
                        rel
                        if not bare
                        else os.path.normpath(
                            os.path.join(os.path.dirname(rel), bare)
                        ).replace(os.sep, "/")
                    )
                    if target_rel.endswith(".md"):
                        anchors_checked += 1
                        if fragment not in anchors_in(target_rel):
                            bad_anchors.append((rel, target, target_rel))
                continue
            if os.path.basename(bare) in GENERATED:
                skipped.append((rel, target))
                continue
            broken.append((rel, target))

    print(f"checked {checked} relative links across {len(sources)} files")
    print(f"checked {anchors_checked} link fragment(s) against page headings")
    if skipped:
        print(f"skipped {len(skipped)} link(s) to build-time generated targets")
        if args.list_ok:
            for rel, target in skipped:
                print(f"    {rel}: {target}")

    if not broken and not bad_anchors:
        print("all relative links and fragments resolve")
        return 0

    if broken:
        print()
        print(f"{len(broken)} broken link(s):")
        for rel, target in broken:
            print(f"    {rel}: {target}")
        print()
        print("Fix the path, or add the basename to GENERATED if the site builds it.")

    if bad_anchors:
        print()
        print(f"{len(bad_anchors)} link(s) to a heading that does not exist:")
        for rel, target, target_rel in bad_anchors:
            fragment = target.partition("#")[2]
            near = difflib.get_close_matches(
                fragment, sorted(anchors_in(target_rel)), n=1, cutoff=0.6
            )
            hint = f"   (closest heading: #{near[0]})" if near else ""
            print(f"    {rel}: {target}{hint}")
        print()
        print("Heading ids follow GitHub's rules; runs of dashes are not collapsed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
