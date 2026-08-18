#!/usr/bin/env python3
"""Keep every version string in the tree in sync with one canonical value.

The canonical version lives in ``src/flow/version.py``. Every other surface
(manifests, docs headers, the CLI banner, the Homebrew formula) mirrors it.
Historically those drifted: 0.11.0 shipped with ``version.py`` still reading
0.3.3 and three hardcoded 0.10.0 strings in the ``flow`` driver.

Usage::

    python3 scripts/sync_version.py              # rewrite mirrors from canonical
    python3 scripts/sync_version.py --check      # exit 1 if any mirror drifted
    python3 scripts/sync_version.py --set 0.12.0 # bump canonical, then rewrite
    python3 scripts/sync_version.py --set v0.12.0 --release-date 2026-09-01

The Homebrew formula is only touched with ``--homebrew``: its ``url`` and
``sha256`` point at a release tarball that does not exist until the tag is
pushed, so bumping it early leaves the formula unusable. The release workflow
passes ``--homebrew --sha256 <digest>`` once the tarball is published.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parent.parent
CANONICAL = REPO / "src" / "flow" / "version.py"
CANONICAL_RE = re.compile(r'^__version__ = "(?P<version>[^"]+)"$', re.MULTILINE)

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.\-]+)?$")


@dataclass(frozen=True)
class Mirror:
    """One file plus the patterns whose version capture must match canonical."""

    path: str
    patterns: tuple[str, ...]
    #: Only applied when --homebrew is passed.
    release_only: bool = False

    def compiled(self) -> list[re.Pattern[str]]:
        return [re.compile(p, re.MULTILINE) for p in self.patterns]


# Every pattern must contain exactly one group named "version". Anything else
# in the pattern is preserved verbatim, so surrounding prose cannot be mangled.
MIRRORS: tuple[Mirror, ...] = (
    Mirror("flow.toml", (r'^version = "(?P<version>[^"]+)"$',)),
    Mirror("pyproject.toml", (r'^version = "(?P<version>[^"]+)"$',)),
    Mirror("CITATION.cff", (r"^version: (?P<version>\S+)$",)),
    Mirror("README.md", (r"^\| Version \| (?P<version>\S+) \|$",)),
    # The wiki front page. It was advertising v0.10 while the canonical version
    # was 0.11.1, because nothing pointed sync_version at it.
    Mirror(
        "docs/wiki-home.md",
        (
            r'^<p class="wiki-hero-eyebrow">v(?P<version>\S+) ·',
            r"^\| Version \| (?P<version>\S+) ·",
        ),
    ),
    Mirror(
        "docs/LANGUAGE_SPEC.md",
        (
            r"^> \*\*Version\*\*: (?P<version>\S+)$",
            r"^\*Version: (?P<version>[^*]+)\*$",
        ),
    ),
    Mirror(
        "flow",
        (
            r'^    echo "Flow Programming Language v(?P<version>[^"]+)"$',
            r'^    echo "  version           Print Flow version \((?P<version>[^)]+)\)"$',
            r'^        echo "Flow (?P<version>[^"]+)"$',
        ),
    ),
    Mirror(
        "packaging/homebrew/Formula/flow.rb",
        (
            # The url carries the version twice, in the tag path and again in
            # the tarball filename. Both need rewriting, so match them apart.
            r'^  url "https://github\.com/flooooooooooow/flow/releases/download/'
            r'v(?P<version>[^/]+)/flow-v[^"]+\.tar\.gz"$',
            r'^  url "https://github\.com/flooooooooooow/flow/releases/download/'
            r'v[^/]+/flow-v(?P<version>[^"]+)\.tar\.gz"$',
            r'^  version "(?P<version>[^"]+)"$',
        ),
        release_only=True,
    ),
)

# Surfaces that carry a release date alongside the version.
DATE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("CITATION.cff", r'^date-released: "(?P<date>[^"]+)"$'),
    ("docs/LANGUAGE_SPEC.md", r"^> \*\*Last Updated\*\*: (?P<date>\S+)$"),
)


def read_canonical() -> str:
    match = CANONICAL_RE.search(CANONICAL.read_text())
    if not match:
        sys.exit(f"error: no __version__ assignment found in {CANONICAL}")
    return match.group("version")


def write_canonical(version: str) -> None:
    text = CANONICAL.read_text()
    updated = CANONICAL_RE.sub(f'__version__ = "{version}"', text, count=1)
    CANONICAL.write_text(updated)


def _substitute(
    text: str,
    pattern: re.Pattern[str],
    group: str,
    value: str,
) -> tuple[str, int]:
    """Replace only the named group, leaving the rest of each match intact."""
    replaced = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal replaced
        current = match.group(group)
        if current == value:
            return match.group(0)
        replaced += 1
        start, end = match.span(group)
        offset = match.start()
        return match.group(0)[: start - offset] + value + match.group(0)[end - offset :]

    return pattern.sub(repl, text), replaced


def apply(
    version: str,
    *,
    check: bool,
    homebrew: bool,
    release_date: str | None,
    sha256: str | None,
    log: Callable[[str], None],
) -> list[str]:
    """Rewrite (or verify) every mirror. Returns the list of drifted files."""
    drifted: list[str] = []

    for mirror in MIRRORS:
        if mirror.release_only and not homebrew:
            continue
        path = REPO / mirror.path
        if not path.exists():
            log(f"warning: {mirror.path} is missing, skipping")
            continue

        original = path.read_text()
        text = original
        total = 0
        for pattern in mirror.compiled():
            if not pattern.search(text):
                log(f"warning: {mirror.path} has no match for {pattern.pattern!r}")
                continue
            text, count = _substitute(text, pattern, "version", version)
            total += count

        if release_date:
            for target, raw in DATE_PATTERNS:
                if target != mirror.path:
                    continue
                text, count = _substitute(
                    text, re.compile(raw, re.MULTILINE), "date", release_date
                )
                total += count

        if sha256 and mirror.path.endswith("flow.rb"):
            text, count = _substitute(
                text,
                re.compile(r'^  sha256 "(?P<version>[0-9a-f]{64})"$', re.MULTILINE),
                "version",
                sha256,
            )
            total += count

        if text == original:
            continue

        drifted.append(mirror.path)
        if check:
            log(f"drift: {mirror.path} ({total} occurrence(s) out of date)")
        else:
            path.write_text(text)
            log(f"updated: {mirror.path} ({total} occurrence(s))")

    return drifted


def fetch_sha256(url: str) -> str:
    with urllib.request.urlopen(url) as response:  # noqa: S310 - fixed GitHub host
        return hashlib.sha256(response.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify only; exit 1 if any mirror is out of date",
    )
    parser.add_argument(
        "--set",
        dest="new_version",
        help="set the canonical version first (leading 'v' is stripped)",
    )
    parser.add_argument(
        "--homebrew",
        action="store_true",
        help="also update the Homebrew formula (release time only)",
    )
    parser.add_argument(
        "--sha256",
        help="tarball digest for the Homebrew formula; implies --homebrew",
    )
    parser.add_argument(
        "--sha256-from-release",
        action="store_true",
        help="download the release tarball and compute its digest",
    )
    parser.add_argument(
        "--release-date",
        help="ISO date for CITATION.cff and the spec header",
    )
    args = parser.parse_args()

    if args.check and args.new_version:
        parser.error("--check and --set are mutually exclusive")

    if args.new_version:
        version = args.new_version.lstrip("v")
        if not SEMVER_RE.match(version):
            parser.error(f"not a semantic version: {version!r}")
        write_canonical(version)
        print(f"canonical: {CANONICAL.relative_to(REPO)} -> {version}")
    else:
        version = read_canonical()
        print(f"canonical: {version}")

    homebrew = args.homebrew or bool(args.sha256) or args.sha256_from_release
    sha256 = args.sha256
    if args.sha256_from_release and not sha256:
        url = (
            "https://github.com/flooooooooooow/flow/releases/download/"
            f"v{version}/flow-v{version}.tar.gz"
        )
        print(f"fetching {url}")
        sha256 = fetch_sha256(url)
        print(f"sha256: {sha256}")

    drifted = apply(
        version,
        check=args.check,
        homebrew=homebrew,
        release_date=args.release_date,
        sha256=sha256,
        log=print,
    )

    if not drifted:
        print("all version references are in sync")
        return 0

    if args.check:
        print()
        print(f"{len(drifted)} file(s) disagree with {version}.")
        print("Fix with: python3 scripts/sync_version.py")
        return 1

    print()
    print(f"synced {len(drifted)} file(s) to {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
