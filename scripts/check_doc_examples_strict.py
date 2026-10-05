#!/usr/bin/env python3
"""Require every documentation block labelled `flow` to be compiler-checked."""

from __future__ import annotations

import check_doc_examples as checker


def main() -> int:
    results = checker.run(use_clang=True)
    checker.report(results, verbose=True)
    # `expect-error` blocks are verified negative tests: they pass only when
    # the compiler reaches the intended rejection. `ignore=` remains a strict
    # failure here because it is deliberately not compiler-checked.
    bad = [
        result
        for result in results
        if result.status not in {"verified", "expected-error"}
    ]
    if not bad:
        print("\nall documented Flow blocks are compiler-checked")
        return 0

    print(f"\n{len(bad)} documented Flow block(s) are not compiler-checked")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
