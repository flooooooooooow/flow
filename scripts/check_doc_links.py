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
from pathlib import Path

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


def tracked_markdown() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "*.md"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=True,
    ).stdout.split()
    return [f for f in out if not f.startswith(SKIP_PREFIXES)]


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

    for rel in tracked_markdown():
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
            if (path.parent / bare).resolve().exists():
                continue
            if os.path.basename(bare) in GENERATED:
                skipped.append((rel, target))
                continue
            broken.append((rel, target))

    print(f"checked {checked} relative links across {len(tracked_markdown())} files")
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
