#!/usr/bin/env python3
"""flow know — look up a Claim Path."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from flow.know import format_know, lint_duplicate_claims, lookup_claim


def main() -> int:
    parser = argparse.ArgumentParser(description="Look up a Flow Claim Path")
    parser.add_argument(
        "path",
        nargs="?",
        help="Claim Path, e.g. Nat/+.zero-right or verify.Nat/+.zero-right",
    )
    parser.add_argument(
        "--lint-duplicates",
        action="store_true",
        help="Scan verify trees for duplicate claims (synonym creep)",
    )
    args = parser.parse_args()
    root = str(Path(__file__).resolve().parents[2])

    if args.lint_duplicates:
        errors = lint_duplicate_claims(root)
        if not errors:
            print("No duplicate claims found.")
            return 0
        for err in errors:
            print(err)
        return 1

    if not args.path:
        parser.print_help()
        return 1

    entry = lookup_claim(args.path, root)
    if not entry:
        print(f"Unknown Claim Path: {args.path}", file=sys.stderr)
        print("Try: Nat/+.zero-right, Bool/||.commutes, Eq/=.reflexive", file=sys.stderr)
        return 1

    print(format_know(entry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())