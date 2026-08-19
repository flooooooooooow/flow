#!/usr/bin/env python3
"""Require every documentation block labelled `flow` to compile."""

from __future__ import annotations

import check_doc_examples as checker


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
