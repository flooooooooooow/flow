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

EXTERNAL = ("http://", "https://", "mailto:", "#", "<")


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list-ok",
        action="store_true",
        help="also list links skipped as build-time generated",
    )
    args = parser.parse_args()

    broken: list[tuple[str, str]] = []
    skipped: list[tuple[str, str]] = []
    checked = 0
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
            checked += 1
            bare = target.split("#")[0]
            if not bare:
                continue
            if resolves(rel, bare, tracked):
                continue
            if os.path.basename(bare) in GENERATED:
                skipped.append((rel, target))
                continue
            broken.append((rel, target))

    print(f"checked {checked} relative links across {len(sources)} files")
    if skipped:
        print(f"skipped {len(skipped)} link(s) to build-time generated targets")
        if args.list_ok:
            for rel, target in skipped:
                print(f"    {rel}: {target}")

    if not broken:
        print("all relative links resolve")
        return 0

    print()
    print(f"{len(broken)} broken link(s):")
    for rel, target in broken:
        print(f"    {rel}: {target}")
    print()
    print("Fix the path, or add the basename to GENERATED if the site builds it.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
