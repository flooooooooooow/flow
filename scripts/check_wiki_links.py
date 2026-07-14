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


def resolve_link(source: Path, href: str) -> Path | None:
    href = href.split("#")[0].strip()
    if not href or href.startswith(("http://", "https://", "mailto:", "#")):
        return None
    if href.endswith(".html"):
        return None

    relative = (WIKI / source.parent / href).resolve()
    if relative.is_relative_to(WIKI) and relative.exists():
        return relative

    absolute = (WIKI / href).resolve()
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