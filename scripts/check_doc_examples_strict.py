#!/usr/bin/env python3
"""Require every documentation block labelled `flow` to compile.

The legacy checker intentionally keeps a conservative harness for its ratchet.
This strict entry point adds one more harness rung for documentation fragments:
top-level declarations are lifted ahead of a generated `main`, while executable
statements stay in `main`. This handles examples that deliberately teach a
function/struct and then immediately exercise it in the same fence.
"""

from __future__ import annotations

import check_doc_examples as checker


_BLOCK_DECLS = (
    "function ",
    "export function ",
    "struct ",
    "enum ",
    "trait ",
    "impl ",
    "effect ",
    "capability ",
    "flow ",
    "test ",
    "theorem ",
)
_ONE_LINE_DECLS = (
    "const ",
    "type ",
    "distinct ",
    "unit ",
    "import ",
    "extern ",
    "module ",
)


def _partition(code: str) -> tuple[str, str]:
    """Separate declarations from executable top-level fragments."""
    decls: list[str] = []
    stmts: list[str] = []
    pending_attrs: list[str] = []
    current: list[str] = []
    current_is_decl = False
    brace_depth = 0
    waiting_for_brace = False

    def flush() -> None:
        nonlocal current, current_is_decl, waiting_for_brace
        if not current:
            return
        target = decls if current_is_decl else stmts
        target.extend(current)
        current = []
        current_is_decl = False
        waiting_for_brace = False

    for line in code.splitlines():
        stripped = line.strip()

        if current:
            current.append(line)
            brace_depth += line.count("{") - line.count("}")
            if waiting_for_brace and "{" in line:
                waiting_for_brace = False
            if not waiting_for_brace and brace_depth <= 0:
                flush()
                brace_depth = 0
            continue

        if stripped.startswith("@"):
            pending_attrs.append(line)
            continue

        is_block_decl = stripped.startswith(_BLOCK_DECLS)
        is_one_line_decl = stripped.startswith(_ONE_LINE_DECLS)

        if is_block_decl:
            current_is_decl = True
            current = pending_attrs + [line]
            pending_attrs = []
            brace_depth = line.count("{") - line.count("}")
            waiting_for_brace = "{" not in line
            if not waiting_for_brace and brace_depth <= 0:
                flush()
                brace_depth = 0
            continue

        if is_one_line_decl:
            decls.extend(pending_attrs)
            pending_attrs = []
            decls.append(line)
            continue

        if pending_attrs:
            stmts.extend(pending_attrs)
            pending_attrs = []

        stmts.append(line)

    flush()
    if pending_attrs:
        stmts.extend(pending_attrs)
    return "\n".join(decls), "\n".join(stmts)


_original_harness = checker._harness


def _strict_harness(code: str, mode: str) -> str:
    if mode != "partition-wrap":
        return _original_harness(code, mode)
    decls, stmts = _partition(code)
    if not stmts.strip():
        raise checker._NotApplicable
    body = (
        "function main() -> i32 {\n"
        f"{checker._indent(stmts)}\n"
        "    return 0\n"
        "}\n"
    )
    return (decls + "\n\n" if decls.strip() else "") + body


checker.MODES = (*checker.MODES, "partition-wrap")
checker._harness = _strict_harness


def main() -> int:
    results = checker.run(use_clang=True)
    checker.report(results, verbose=True)
    bad = [result for result in results if result.status != "verified"]
    if not bad:
        print("\nall documented Flow blocks compile")
        return 0

    print(f"\n{len(bad)} documented Flow block(s) are not verified")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
