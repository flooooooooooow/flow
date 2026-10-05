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
from collections import Counter

import check_doc_examples as checker
from docs_blocks import collect

# Strong signals are syntax-shaped rather than keyword-shaped. In particular,
# compiler output such as `array<u8, 1024>` or `flow ~21,000 us` must not be
# mistaken for source merely because it contains a Flow type or keyword.
_STRONG = re.compile(
    r"(?:"
    r"^\s*(?:export\s+)?function\s+[A-Za-z_]\w*(?:<[^\n>]+>)?\s*\([^\n]*\)\s*->|"
    r"^\s*(?:struct|enum|trait|impl|effect|capability)\s+[A-Za-z_]\w*[^\n]*\{|"
    r"^\s*flow\s+[A-Za-z_]\w*[^\n]*\{|"
    r"^\s*(?:state|input|output|param)\s+[A-Za-z_]\w*\s*(?::|=)|"
    r"^\s*let(?:\s+mut)?\s+[A-Za-z_]\w*\s*(?::|=)|"
    r"^\s*(?:const|type|unit)\s+[A-Za-z_]\w*\s*(?::|=)|"
    r"^\s*distinct\s+type\s+|"
    r"^\s*extern\s*\{|"
    r"^\s*import\s+[\"']|"
    r"^\s*module\s+[A-Za-z_]\w*\s*\{|"
    r"^\s*handle\s+[A-Za-z_]\w*\s+with\s+[A-Za-z_]\w*\s*\{|"
    r"^\s*(?:theorem|assume|therefore)\b|"
    r"^\s*(?:solver|always|guarantee|deploy)\s*\{|"
    r"^\s*every\s+[^\n]+\{|"
    r"^\s*when\s+[^\n]+\{|"
    r"^\s*dsys\s+[A-Za-z_]\w*\s*\{|"
    r"^\s*horizon\s+[A-Za-z_]\w*\s+(?:finite|infinite)\b|"
    r"^\s*sense\s+on\s+[A-Za-z_]\w*\s*\{|"
    r"^\s*ga\s+evolve\s+on\s+|"
    r"^\s*closed\s+[A-Za-z_]\w*\s+with\s+|"
    r"^\s*analyze\s+[A-Za-z_]\w*\s+|"
    r"^\s*represent\s+(?:linear|koopman)\b|"
    r"^\s*field\s+[A-Za-z_]\w*\s*:|"
    r"^\s*shader\s+fill\b|"
    r"^\s*@[A-Za-z_]\w*|"
    r"\bevolves\s+as\b|"
    r"\bbecomes\b|"
    r"\|>"
    r")",
    re.MULTILINE,
)

# Control-flow-only fragments are common in the book. Require actual source
# punctuation so English prose and command output do not count.
_CONTROL = re.compile(
    r"^\s*(?:if|elif|while|match|(?:parallel\s+)?for)\b[^\n]*\{",
    re.MULTILINE,
)
_RETURN = re.compile(r"^\s*return(?:\s+[^#\n]+)?\s*(?:#.*)?$", re.MULTILINE)


def looks_like_flow(code: str) -> bool:
    if _STRONG.search(code) or _CONTROL.search(code):
        return True
    if _RETURN.search(code) and re.search(r"\b(?:i32|i64|f32|f64|bool|string|void)\b", code):
        return True
    return False


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
