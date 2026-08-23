#!/usr/bin/env python3
"""Check that release/version surfaces are represented in the canonical changelog."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "docs" / "project" / "CHANGELOG.md"
VERSION = ROOT / "src" / "flow" / "version.py"


def current_version() -> str:
    text = VERSION.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    if not match:
        raise SystemExit("could not read __version__ from src/flow/version.py")
    return match.group(1)


def changelog_versions() -> list[str]:
    text = CHANGELOG.read_text(encoding="utf-8")
    return re.findall(r"^## \[([^]]+)\](?:\s+-\s+.*)?$", text, flags=re.MULTILINE)


def main() -> int:
    version = current_version()
    versions = changelog_versions()
    if version not in versions:
        raise SystemExit(f"current version {version} has no section in {CHANGELOG.relative_to(ROOT)}")
    if len(versions) != len(set(versions)):
        raise SystemExit("duplicate version headings in canonical changelog")
    print(f"changelog: {len(versions)} version sections; current {version} present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
