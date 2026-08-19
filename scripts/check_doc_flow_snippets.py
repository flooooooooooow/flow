#!/usr/bin/env python3
"""Reject Flow-looking documentation snippets hidden in generic code fences.

A documentation example must not become invisible to the compiler merely by
changing `````flow`` to `````text``. Current Flow belongs in a ``flow`` fence
and is compiled by check_doc_examples.py. Intentionally non-current language
sketches must be explicit ``flow-pseudocode`` or ``flow-future`` fences so a
reader cannot mistake them for shipped syntax.
"""

from __future__ import annotations

import re
import sys
from collections import Counter

import check_doc_examples as checker
from docs_blocks import collect

# High-signal Flow surface forms. These deliberately target syntax rather than
# ordinary programming words so shell transcripts, JSON, C, Python, output, and
# prose examples do not get swept into the Flow compiler.
_FLOW_LINE = re.compile(
    r"^\s*(?:"
    r"(?:export\s+)?function\s+|"
    r"struct\s+|enum\s+|trait\s+|impl\s+|effect\s+|capability\s+|"
    r"flow\s+|state\s+|input\s+|output\s+|param\s+|"
    r"let(?:\s+mut)?\s+|const\s+|distinct\s+type\s+|type\s+|unit\s+|"
    r"extern\s*\{|import\s+|module\s+|"
    r"if\s+|elif\s+|while\s+|(?:parallel\s+)?for\s+|match\s+|"
    r"handle\s+|return\s+|defer\s+|expect\s+|"
    r"theorem\s+|assume\s+|therefore\s+|"
    r"solver\s*\{|every\s+|when\s+|always\s*\{|"
    r"dsys\s+|horizon\s+|sense\s+|ga\s+evolve\s+|closed\s+|analyze\s+|"
    r"represent\s+|control\s+|guarantee\s*\{|deploy\s*\{|"
    r"field\s+|boundary\s+|shader\s+fill\s+|"
    r"@[A-Za-z_]"
    r")",
    re.MULTILINE,
)

_FLOW_INFIX = re.compile(r"\b(?:evolves\s+as|becomes)\b|\|>")

# These tags are intentionally explicit. They are not executable current Flow,
# and the name says that directly to readers and tooling.
EXPLICIT_NONCURRENT = {"flow-pseudocode", "flow-future"}


def looks_like_flow(code: str) -> bool:
    return bool(_FLOW_LINE.search(code) or _FLOW_INFIX.search(code))


def main() -> int:
    suspicious = [
        block
        for block in collect()
        if block.lang in {"", "text"} and looks_like_flow(block.code)
    ]

    if not suspicious:
        print("no Flow-looking snippets are hidden in text or untyped fences")
        return 0

    results = [checker.verify(block) for block in suspicious]
    checker._batch_clang(results)
    counts = Counter(result.status for result in results)

    print(
        f"Flow-looking snippets hidden from the canonical checker: {len(results)} "
        f"({dict(counts)})\n"
    )
    print(
        "Current Flow must use a `flow` fence and compile. Future or schematic "
        "syntax must use `flow-future` or `flow-pseudocode` explicitly.\n"
    )

    for result in results:
        block = result.block
        if result.status == "verified":
            detail = "compiles; relabel this fence as `flow`"
        else:
            head = (result.detail or "").splitlines()
            reason = head[0] if head else result.stage or result.status
            detail = f"does not compile: {reason}"
        print(f"  {block.ident}: {detail}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
