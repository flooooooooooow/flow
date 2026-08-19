#!/usr/bin/env python3
"""One-time cleanup: stop labelling non-compiling snippets as Flow code."""

from __future__ import annotations

import re
from collections import Counter, defaultdict

import check_doc_examples_strict  # noqa: F401  # install the strict harness rung
from check_doc_examples import ROOT, run

FENCE = re.compile(r"^(?P<indent>\s{0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*?)(?P<eol>\r?\n)?$")


def main() -> int:
    results = run(use_clang=True)
    bad = [result for result in results if result.status != "verified"]
    by_path = defaultdict(list)
    for result in bad:
        by_path[result.block.path].append(result.block)

    changed = 0
    statuses = Counter(result.status for result in bad)
    for rel, blocks in by_path.items():
        path = ROOT / rel
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        for block in sorted(blocks, key=lambda item: item.line, reverse=True):
            index = block.line - 1
            match = FENCE.match(lines[index])
            if not match:
                raise RuntimeError(f"cannot find opening fence for {block.ident}")
            info = match.group("info").strip()
            if not info or info.split()[0].lower() != "flow":
                raise RuntimeError(f"opening fence changed for {block.ident}: {info!r}")
            eol = match.group("eol") or ""
            lines[index] = f"{match.group('indent')}{match.group('fence')}text{eol}"
            changed += 1
        path.write_text("".join(lines), encoding="utf-8")

    print(f"retagged {changed} non-compiling Flow block(s) as text: {dict(statuses)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
