"""flow check: lint .flow files against project conventions (#415).

Reads [conventions].avoid from flow.toml and warns when source
files match avoid patterns.
"""

from __future__ import annotations

import sys
from pathlib import Path

from flow.conventions import check_file, load_conventions


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    conv = load_conventions()
    if not conv.avoid:
        print("No avoid patterns defined in flow.toml.")
        return 0

    if args:
        files = [Path(a) for a in args]
    else:
        files = list(Path.cwd().rglob("*.flow"))
        files = [f for f in files if "build/" not in str(f) and ".freebuff/" not in str(f)]

    if not files:
        print("No .flow files found.")
        return 0

    total_warnings = 0
    for f in files:
        warnings = check_file(f, conv)
        for w in warnings:
            print(w, file=sys.stderr)
            total_warnings += 1

    if total_warnings == 0:
        print(f"Checked {len(files)} files. No convention violations found.")
        return 0
    print(f"\n{total_warnings} warning(s) in {len(files)} files.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
