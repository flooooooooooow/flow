#!/usr/bin/env python3
"""Reject duplicate mutable project-state documents at the repository root."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

POINTERS = {
    "Questions.md": "docs/project/Questions.md",
    "ROADMAP-1.0.md": "docs/project/archive/ROADMAP-1.0.md",
    "RELEASE-1.0.md": "docs/project/archive/RELEASE-1.0.md",
}

MAX_POINTER_LINES = 12


def main() -> int:
    errors: list[str] = []

    for pointer_name, canonical_name in POINTERS.items():
        pointer = ROOT / pointer_name
        canonical = ROOT / canonical_name

        if not pointer.is_file():
            errors.append(f"missing compatibility pointer: {pointer_name}")
            continue
        if not canonical.is_file():
            errors.append(f"missing canonical/archive document: {canonical_name}")
            continue

        text = pointer.read_text(encoding="utf-8")
        if canonical_name not in text:
            errors.append(
                f"{pointer_name} must point to {canonical_name}; do not restore a second source of truth"
            )

        line_count = len(text.splitlines())
        if line_count > MAX_POINTER_LINES:
            errors.append(
                f"{pointer_name} has {line_count} lines; compatibility pointers must stay <= {MAX_POINTER_LINES}"
            )

    if errors:
        for error in errors:
            print(f"project-state: {error}", file=sys.stderr)
        return 1

    print("project-state: canonical sources OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
