#!/usr/bin/env python3
"""Check that the current release is represented in Flow's canonical changelog."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "docs" / "project" / "CHANGELOG.md"
VERSION = ROOT / "src" / "flow" / "version.py"

# The pre-formal-release changelog contains two historical 0.2.0 sections.
# Preserve that provenance; do not allow new duplicate version headings.
LEGACY_DUPLICATES = {"0.2.0"}


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

    duplicates = {name for name, count in Counter(versions).items() if count > 1}
    unexpected = duplicates - LEGACY_DUPLICATES
    if unexpected:
        raise SystemExit("duplicate version headings in canonical changelog: " + ", ".join(sorted(unexpected)))

    print(f"changelog: {len(versions)} historical sections; current {version} present")
    if duplicates:
        print("changelog: preserving documented legacy duplicate(s): " + ", ".join(sorted(duplicates)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
