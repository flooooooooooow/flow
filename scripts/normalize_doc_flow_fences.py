#!/usr/bin/env python3
"""One-time repair of documentation fence intent after the broad text retag.

This script is intentionally conservative. It never blesses an ordinary broken
snippet as pseudocode merely because it fails. It only restores executable
snippets, historical negative tests, and examples whose pre-PR metadata already
said they were ignored/proposed.
"""

from __future__ import annotations

import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

import check_doc_examples as checker
from docs_blocks import ROOT, collect
from check_doc_flow_snippets import looks_like_flow

FENCE = re.compile(r"^(?P<indent>\s{0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*?)(?P<eol>\r?\n)?$")

FUTURE_WORDS = (
    "proposed", "not implemented", "aspirational", "future", "north-star",
    "planned", "design sketch", "not yet", "later card", "vision syntax",
)


def base_ledger() -> dict[str, dict]:
    raw = subprocess.check_output(
        ["git", "show", "origin/main:docs/generated/example-status.json"],
        text=True,
    )
    payload = json.loads(raw)
    return {row["key"]: row for row in payload.get("blocks", [])}


def classify_ignored(reason: str) -> str:
    lower = reason.lower()
    if any(word in lower for word in FUTURE_WORDS):
        return "flow-future"
    return "flow-pseudocode"


def main() -> int:
    ledger = base_ledger()
    hidden = [
        block for block in collect()
        if block.lang in {"", "text"} and looks_like_flow(block.code)
    ]

    by_path: dict[str, list[tuple[object, str]]] = defaultdict(list)
    counts: dict[str, int] = defaultdict(int)

    for block in hidden:
        result = checker.verify(block)
        if result.status == "verified":
            new_info = "flow"
            counts["restored-current"] += 1
        else:
            old = ledger.get(block.key)
            if old and old.get("status") == "expected-error":
                new_info = "flow expect-error"
                counts["restored-negative"] += 1
            elif old and old.get("status") == "ignored":
                new_info = classify_ignored(str(old.get("reason", "")))
                counts[new_info] += 1
            elif (
                block.path in {"VISION.md", "docs/vision.md"}
                or block.path == "ROADMAP.md"
                or (block.section and "future" in block.section.lower())
                or (block.title and "future" in block.title.lower())
            ):
                new_info = "flow-future"
                counts["flow-future"] += 1
            elif "..." in block.code:
                new_info = "flow-pseudocode"
                counts["flow-pseudocode"] += 1
            else:
                continue
        by_path[block.path].append((block, new_info))

    changed = 0
    for rel, items in by_path.items():
        path = ROOT / rel
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        for block, new_info in sorted(items, key=lambda pair: pair[0].line, reverse=True):
            index = block.line - 1
            match = FENCE.match(lines[index])
            if not match:
                raise RuntimeError(f"opening fence missing at {block.ident}")
            current = match.group("info").strip()
            if current not in {"", "text"}:
                raise RuntimeError(f"unexpected fence {current!r} at {block.ident}")
            eol = match.group("eol") or ""
            lines[index] = (
                f"{match.group('indent')}{match.group('fence')}{new_info}{eol}"
            )
            changed += 1
        path.write_text("".join(lines), encoding="utf-8")

    print(f"normalized {changed} Flow-looking fence(s): {dict(counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
