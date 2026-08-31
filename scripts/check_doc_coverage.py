#!/usr/bin/env python3
"""Does the documentation cover every part of the language?

The feature list is read out of the compiler, never hand-maintained, so it
cannot quietly fall behind the implementation:

    keywords        src/flow/parser.py, Lexer.keyword_map
    attributes      src/flow/attributes.py, KNOWN_ATTRIBUTES
    CLI commands    the `flow` driver's dispatch table
    stdlib modules  lib/stdlib/**/*.flow
    backends        src/flow/*_generator.py and friends

`docs/coverage.json` maps each feature to the page that documents it. A mapping
is only accepted when the named page exists and actually mentions the feature,
so an entry cannot be a promise nobody kept. Features that genuinely have no
home carry a written reason instead.

Usage:
    python3 scripts/check_doc_coverage.py            # report and gate
    python3 scripts/check_doc_coverage.py --propose  # suggest homes for gaps
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MAP = DOCS / "coverage.json"

# Keywords whose whole job is to be part of another construct, or which read as
# ordinary English often enough that a bare word search proves nothing.
UNINTERESTING_KEYWORDS = {
    "true", "false", "null", "self", "in", "to", "as", "with", "and", "or",
    "not", "default", "void", "step",
}


def _keywords() -> set[str]:
    src = (ROOT / "src" / "flow" / "parser.py").read_text()
    block = re.search(r"self\.keyword_map\s*=\s*\{(.*?)\n\s*\}", src, re.S)
    if not block:
        raise SystemExit("could not find Lexer.keyword_map in parser.py")
    found = set(re.findall(r"['\"]([a-z_]+)['\"]\s*:", block.group(1)))
    return found - UNINTERESTING_KEYWORDS


def _attributes() -> set[str]:
    sys.path.insert(0, str(ROOT / "src"))
    from flow.attributes import KNOWN_ATTRIBUTES

    return set(KNOWN_ATTRIBUTES)


def _cli_commands() -> set[str]:
    """Subcommands the driver dispatches on.

    Read from the `case` arms rather than the help text, so a command that
    exists but was never added to `show_help` still counts.
    """
    driver = (ROOT / "flow-driver").read_text()
    start = driver.index('case "${1:-help}" in')
    # Stop at the matching esac, i.e. the first one at column 0.
    end = driver.index("\nesac", start)
    body = driver[start:end]
    commands: set[str] = set()
    for arm in re.findall(r'^\s{4}((?:"[^"]+"\|?)+)\)\s*$', body, re.M):
        for name in re.findall(r'"([^"]+)"', arm):
            if name.startswith("-") or "*" in name:
                continue
            commands.add(name)
    return commands


def _stdlib_modules() -> set[str]:
    out = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "lib/stdlib/*.flow", "lib/stdlib/**/*.flow"],
        text=True,
    )
    return {
        Path(line).stem
        for line in out.splitlines()
        if line and "test" not in Path(line).parts
    }


# Suffixes a backend module can carry. `_target` is here because a BPF target
# on an unmerged branch would otherwise have landed as a whole new compilation
# target that the coverage gate could not see.
_BACKEND_SUFFIXES = ("_generator", "_codegen", "_compiler", "_target", "_backend")


def _backends() -> set[str]:
    names = set()
    for path in (ROOT / "src" / "flow").glob("*.py"):
        if path.stem.endswith(_BACKEND_SUFFIXES):
            names.add(path.stem)
    return names


CATEGORIES = {
    "keyword": _keywords,
    "attribute": _attributes,
    "cli": _cli_commands,
    "stdlib": _stdlib_modules,
    "backend": _backends,
}


def inventory() -> dict[str, set[str]]:
    return {name: fn() for name, fn in CATEGORIES.items()}


def _doc_text(rel: str) -> str:
    path = DOCS / rel
    try:
        return path.read_text(errors="ignore")
    except OSError:
        return ""


def mentions(rel: str, category: str, feature: str) -> bool:
    """Does the page actually talk about this feature?

    Deliberately literal. A mapping that points at a page which never names the
    thing is worse than an admitted gap, because it reads as covered.
    """
    text = _doc_text(rel)
    if not text:
        return False
    if category == "attribute":
        return f"@{feature}" in text
    if category == "cli":
        return bool(re.search(rf"(?:flow|\$)\s+{re.escape(feature)}\b", text))
    if category == "stdlib":
        return feature in text
    return bool(re.search(rf"\b{re.escape(feature)}\b", text))


def all_doc_pages() -> list[str]:
    return sorted(
        p.relative_to(DOCS).as_posix()
        for p in DOCS.rglob("*.md")
        if "formal" not in p.parts and not any(x.startswith(".") for x in p.parts)
    )


def propose(category: str, feature: str, pages: Iterable[str]) -> list[str]:
    """Pages that mention a feature, best first."""
    hits = []
    for rel in pages:
        if not mentions(rel, category, feature):
            continue
        text = _doc_text(rel)
        if category == "attribute":
            score = text.count(f"@{feature}")
        else:
            score = len(re.findall(rf"\b{re.escape(feature)}\b", text))
        # A dedicated reference page beats a passing mention in a changelog.
        bonus = 3 if rel.startswith(("language/", "library/")) else 0
        hits.append((score + bonus, rel))
    hits.sort(reverse=True)
    return [rel for _, rel in hits[:3]]


def load_map() -> dict:
    if not MAP.exists():
        return {"covered": {}, "exempt": {}}
    return json.loads(MAP.read_text(encoding="utf-8"))


def check() -> tuple[list[str], dict]:
    mapping = load_map()
    covered = mapping.get("covered", {})
    exempt = mapping.get("exempt", {})
    problems: list[str] = []
    stats: dict[str, Counter] = {}

    inv = inventory()
    known = {f"{cat}:{name}" for cat, names in inv.items() for name in names}

    for category, names in sorted(inv.items()):
        counter = Counter()
        for name in sorted(names):
            key = f"{category}:{name}"
            if key in exempt:
                if not str(exempt[key]).strip():
                    problems.append(f"{key} is exempt with no written reason")
                counter["exempt"] += 1
                continue
            page = covered.get(key)
            if not page:
                counter["uncovered"] += 1
                problems.append(f"{key} has no documented home")
                continue
            if not (DOCS / page).exists():
                problems.append(f"{key} maps to {page!r}, which does not exist")
                counter["broken"] += 1
                continue
            if not mentions(page, category, name):
                problems.append(f"{key} maps to {page!r}, which never mentions it")
                counter["broken"] += 1
                continue
            counter["covered"] += 1
        stats[category] = counter

    for key in sorted(set(covered) | set(exempt)):
        if key not in known:
            problems.append(f"{key} is mapped but no longer exists in the compiler")

    return problems, stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--propose", action="store_true",
                    help="suggest a home for every uncovered feature")
    ap.add_argument("--write-proposal", action="store_true",
                    help="write docs/coverage.json from the proposal")
    args = ap.parse_args()

    inv = inventory()
    print("Feature inventory, read from the compiler:")
    for category, names in sorted(inv.items()):
        print(f"  {category:10s} {len(names):4d}")

    if args.propose or args.write_proposal:
        pages = all_doc_pages()
        covered: dict[str, str] = {}
        gaps: list[str] = []
        for category, names in sorted(inv.items()):
            for name in sorted(names):
                best = propose(category, name, pages)
                if best:
                    covered[f"{category}:{name}"] = best[0]
                else:
                    gaps.append(f"{category}:{name}")
        print(f"\nproposed homes : {len(covered)}")
        print(f"no page mentions them at all : {len(gaps)}")
        for key in gaps:
            print(f"    {key}")
        if args.write_proposal:
            existing = load_map()
            existing["covered"] = covered
            existing.setdefault("exempt", {})
            MAP.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n")
            print(f"\nwrote {MAP.relative_to(ROOT)}")
        return 0

    problems, stats = check()
    print("\nCoverage:")
    for category, counter in sorted(stats.items()):
        total = sum(counter.values())
        print(
            f"  {category:10s} {counter['covered']:4d}/{total:<4d} covered"
            f"   exempt {counter['exempt']:3d}   problems {counter['broken']:3d}"
            f"   uncovered {counter['uncovered']:3d}"
        )

    if problems:
        print(f"\n{len(problems)} problem(s):")
        for line in problems[:60]:
            print(f"  {line}")
        if len(problems) > 60:
            print(f"  ... and {len(problems) - 60} more")
        return 1
    print("\nevery feature has a documented home")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
