#!/usr/bin/env python3
"""CLI driver for the FLOW compiler fuzz harness.

Examples:
    python3 tests/fuzz/run_fuzz.py                          # all targets, 30s each
    python3 tests/fuzz/run_fuzz.py --target grammar --seconds 300
    python3 tests/fuzz/run_fuzz.py --seed 7 --save          # persist repros

Budget can also come from FLOW_FUZZ_SECONDS (per target).
Exit code 1 if any new crash class was found.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness import CRASH_DIR, TARGETS, FuzzStats, save_findings  # noqa: E402


def known_crash_classes() -> set:
    import json

    manifest = CRASH_DIR / "known_crashes.json"
    if not manifest.exists():
        return set()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    # "fixed" entries stay in the manifest as regression fixtures, but no
    # longer suppress findings: a NEW crash of the same class must fail.
    return {
        (entry["stage"], entry["exception"])
        for entry in data.values()
        if entry.get("status", "open") == "open"
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="FLOW compiler fuzzer")
    ap.add_argument(
        "--target",
        choices=[*TARGETS, "all"],
        default="all",
        help="fuzz target (default: all, run sequentially)",
    )
    ap.add_argument(
        "--seconds",
        type=float,
        default=float(os.environ.get("FLOW_FUZZ_SECONDS", "30")),
        help="wall-clock budget per target (default 30, or $FLOW_FUZZ_SECONDS)",
    )
    ap.add_argument("--seed", type=int, default=1234, help="RNG seed")
    ap.add_argument(
        "--save",
        action="store_true",
        help="save minimized repros into tests/fuzz/crashes/",
    )
    args = ap.parse_args()

    targets = list(TARGETS) if args.target == "all" else [args.target]
    known = known_crash_classes()
    combined = FuzzStats()
    new_classes = 0
    for i, name in enumerate(targets):
        stats = TARGETS[name](args.seconds, args.seed + i)
        print(
            f"[{name}] {stats.iterations} inputs in {args.seconds:.0f}s: "
            f"{stats.ok} ok, {stats.clean_errors} clean errors, "
            f"{len(stats.findings)} crash class(es)"
        )
        for finding in stats.findings.values():
            is_known = (finding.stage, finding.exc_type) in known
            tag = "KNOWN" if is_known else "NEW  "
            print(
                f"  [{tag}] {finding.exc_type} at {finding.location} "
                f"(stage {finding.stage}): {finding.message[:100]}"
            )
            repro = (finding.minimized or finding.input_text)[:200]
            print(f"    repro ({len(finding.minimized or finding.input_text)}b): "
                  f"{repro!r}")
            if not is_known and finding.key not in combined.findings:
                new_classes += 1
            combined.findings.setdefault(finding.key, finding)
        combined.iterations += stats.iterations
    if combined.findings and args.save:
        for path in save_findings(combined):
            print(f"saved {path}")
    print(
        f"total: {combined.iterations} inputs, "
        f"{len(combined.findings)} distinct crash class(es) "
        f"({new_classes} new)"
    )
    # only NEW crash classes fail the run; known ones are tracked backlog items
    return 1 if new_classes else 0


if __name__ == "__main__":
    raise SystemExit(main())
