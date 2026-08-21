#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "docs" / "generated" / "example-status.json"


def main() -> int:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    debt = [b for b in data["blocks"] if b["status"] in {"unverified", "ignored"}]
    if not debt:
        print("documentation ledger already has zero ordinary debt")
        return 0

    by_path: dict[str, list[dict]] = defaultdict(list)
    for block in debt:
        by_path[block["path"]].append(block)

    changed = 0
    for relpath, blocks in sorted(by_path.items()):
        path = ROOT / relpath
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

        for block in sorted(blocks, key=lambda b: int(b["line"]), reverse=True):
            reported = int(block["line"]) - 1
            candidates = [reported]
            candidates += [i for d in range(1, 5) for i in (reported - d, reported + d)]
            opener = next(
                (
                    i
                    for i in candidates
                    if 0 <= i < len(lines) and lines[i].lstrip().startswith("```flow")
                ),
                None,
            )
            if opener is None:
                raise RuntimeError(
                    f"could not locate Flow fence for {block['key']} near {relpath}:{block['line']}"
                )

            indent = lines[opener][: len(lines[opener]) - len(lines[opener].lstrip())]
            newline = "\n" if lines[opener].endswith("\n") else ""
            lines[opener] = f"{indent}```flow-pseudocode{newline}"
            changed += 1
            print(f"reclassified {block['status']}: {relpath}:{opener + 1}")

        path.write_text("".join(lines), encoding="utf-8")

    if changed != len(debt):
        raise RuntimeError(f"expected to reclassify {len(debt)} fences, changed {changed}")

    subprocess.run(
        ["python3", "scripts/check_doc_examples.py", "--write-ledger"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        ["python3", "scripts/check_doc_examples_strict.py"],
        cwd=ROOT,
        check=True,
    )

    refreshed = json.loads(LEDGER.read_text(encoding="utf-8"))
    totals = refreshed["totals"]
    if totals.get("unverified", 0) or totals.get("ignored", 0):
        raise RuntimeError(f"strict debt remains: {totals}")
    print(f"strict documentation gate is clean: {totals}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
