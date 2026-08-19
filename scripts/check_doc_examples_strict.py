#!/usr/bin/env python3
"""Require every documentation block labelled `flow` to compile."""

from check_doc_examples import report, run


def main() -> int:
    results = run(use_clang=True)
    report(results, verbose=True)
    bad = [result for result in results if result.status != "verified"]
    if not bad:
        print("\nall documented Flow blocks compile")
        return 0

    print(f"\n{len(bad)} documented Flow block(s) are not verified")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
