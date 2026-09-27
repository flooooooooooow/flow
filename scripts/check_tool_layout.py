#!/usr/bin/env python3
"""Reject mirrored long-lived tool directories under tools/ and scripts/tools/."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SCRIPT_TOOLS = ROOT / "scripts" / "tools"


def child_dirs(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {p.name for p in root.iterdir() if p.is_dir()}


def main() -> int:
    mirrors = sorted(child_dirs(TOOLS) & child_dirs(SCRIPT_TOOLS))
    if not mirrors:
        print("tool-layout: no mirrored tool directories")
        return 0

    for name in mirrors:
        print(
            f"tool-layout: {name!r} exists under both tools/ and scripts/tools/; "
            "choose one canonical implementation and keep scripts/ as thin automation",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
