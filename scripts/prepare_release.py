#!/usr/bin/env python3
"""Prepare a Flow release branch from one small release-notes file."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
HEADING_RE = re.compile(r"^#\s+(.+?)\s*$")
CURRENT_RELEASE_RE = re.compile(r"\*\*Flow \d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?\*\*.*?\n\n", re.S)


def read_notes(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8").strip()
    lines = text.splitlines()
    if not lines:
        raise SystemExit(f"release notes are empty: {path}")
    match = HEADING_RE.fullmatch(lines[0])
    if not match:
        raise SystemExit(f"release notes must start with one '# headline': {path}")
    headline = match.group(1).strip()
    body = "\n".join(lines[1:]).strip()
    if not body:
        raise SystemExit(f"release notes have no body: {path}")
    return headline, body


def sync_version(root: Path, version: str, release_date: str) -> None:
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "sync_version.py"),
            "--set",
            version,
            "--release-date",
            release_date,
        ],
        cwd=root,
        check=True,
    )


def update_detailed_changelog(
    root: Path,
    version: str,
    release_date: str,
    body: str,
) -> None:
    path = root / "docs" / "project" / "CHANGELOG.md"
    text = path.read_text(encoding="utf-8")
    heading = f"## [{version}] - {release_date}"
    if heading in text:
        return
    marker = "## Unreleased\n"
    if marker not in text:
        raise SystemExit(f"{path.relative_to(root)} has no Unreleased section")
    entry = f"{heading}\n\n{body.rstrip()}\n"
    path.write_text(text.replace(marker, marker + "\n" + entry + "\n", 1), encoding="utf-8")


def update_root_changelog(root: Path, version: str, release_date: str, headline: str) -> None:
    path = root / "CHANGELOG.md"
    text = path.read_text(encoding="utf-8")
    current = (
        f"**Flow {version}** is the current release on the explicit 1.x compatibility contract in "
        "[`STABILITY.md`](STABILITY.md). "
        f"{headline.rstrip('.')} .\n\n"
    ).replace(" .", ".")

    updated, count = CURRENT_RELEASE_RE.subn(current, text, count=1)
    if count != 1 and f"**Flow {version}**" not in text:
        raise SystemExit(f"could not replace current-release paragraph in {path.relative_to(root)}")
    text = updated

    if f"| {version} |" not in text:
        rows = list(re.finditer(r"^\| (\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?) \|", text, re.M))
        if not rows:
            raise SystemExit(f"could not find release-history rows in {path.relative_to(root)}")
        row = f"| {version} | {release_date} | {headline.rstrip('.')} |\n"
        insert_at = rows[0].start()
        text = text[:insert_at] + row + text[insert_at:]

    path.write_text(text, encoding="utf-8")


def verify(root: Path, version: str) -> None:
    subprocess.run(
        [sys.executable, str(root / "scripts" / "sync_version.py"), "--check"],
        cwd=root,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(root / "scripts" / "check_changelog.py")],
        cwd=root,
        check=True,
    )
    version_text = (root / "src" / "flow" / "version.py").read_text(encoding="utf-8")
    if f'__version__ = "{version}"' not in version_text:
        raise SystemExit("canonical version did not update")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--release-date", required=True)
    parser.add_argument("--notes", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    version = args.version.lstrip("v")
    if not VERSION_RE.fullmatch(version):
        parser.error(f"not a semantic version: {args.version!r}")

    root = args.root.resolve()
    notes = args.notes if args.notes.is_absolute() else root / args.notes
    headline, body = read_notes(notes)

    sync_version(root, version, args.release_date)
    update_detailed_changelog(root, version, args.release_date, body)
    update_root_changelog(root, version, args.release_date, headline)
    verify(root, version)
    print(f"prepared Flow {version} ({args.release_date})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
