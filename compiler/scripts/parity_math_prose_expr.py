#!/usr/bin/env python3
"""Parity gate: Flow port of math_prose expression rendering vs the Python.

Runs examples/compilers/math_prose_expr_demo.flow (which prints one
`KIND|expr|result` line per case), feeds the same expressions through
src/flow/math_prose.py, and fails on any disagreement.

    python3 compiler/scripts/parity_math_prose_expr.py

Set FLOW_PARITY_KEEP=1 to keep the built binary output for inspection.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEMO = ROOT / "examples" / "compilers" / "math_prose_expr_demo.flow"

sys.path.insert(0, str(ROOT / "src"))

from flow.claim_address import parse_claim_address  # noqa: E402
from flow.math_prose import (  # noqa: E402
    flow_expr_to_latex,
    flow_expr_to_mathematical_english,
    geometry_expr_to_latex,
    invoke_premise_mathematical,
)

# The demo prints INV cases keyed by argument shape rather than by expression,
# because invoke_premise takes a parsed address plus four strings.
_INV_ADDR = parse_claim_address("Nat/+.zero-left")
_INV_PHRASE = "zero is the left identity"
_INV_CASES = {
    "plain": dict(phrase=_INV_PHRASE),
    "args": dict(phrase=_INV_PHRASE, args="n", kind="definition"),
    "ref": dict(phrase=_INV_PHRASE, theorem_ref="Theorem 1"),
    "ref+args": dict(phrase=_INV_PHRASE, args="m and n", theorem_ref="Theorem 1"),
}


def _invoke(key: str) -> str:
    return invoke_premise_mathematical(_INV_ADDR, **_INV_CASES[key])


REFERENCE = {
    "EN": flow_expr_to_mathematical_english,
    "TEX": flow_expr_to_latex,
    "GEO": geometry_expr_to_latex,
    "INV": _invoke,
}

# Chained `or` is the one deliberate difference. Python shields `a or b` behind
# a placeholder, then shields the placeholder again for the second `or`, and
# expands in index order, so the inner placeholder is never substituted and a
# literal `__DISJ0__` reaches the output. The Flow port expands every level.
KNOWN_DIVERGENCE: dict[tuple[str, str], str] = {
    ("EN", "a or b or c"): "python leaks an unexpanded __DISJ0__ placeholder",
}


def run_demo() -> list[str]:
    env = dict(os.environ, FLOW_HOST="python")
    proc = subprocess.Popen(
        [str(ROOT / "flow"), "run", str(DEMO)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    while True:
        try:
            stdout_data, stderr_data = proc.communicate(timeout=30)
            break
        except subprocess.TimeoutExpired:
            print("  ... still running flow demo ...", flush=True)

    if proc.returncode != 0:
        sys.stderr.write(stdout_data)
        sys.stderr.write(stderr_data)
        sys.exit(f"demo failed to build or run (exit {proc.returncode})")

    lines = []
    for line in stdout_data.splitlines():
        if line.count("|") >= 2 and line.split("|", 1)[0] in REFERENCE:
            lines.append(line)
    if not lines:
        sys.stderr.write(stdout_data)
        sys.exit("demo produced no comparable output")
    return lines


def main() -> int:
    rows = run_demo()
    mismatches: list[tuple[str, str, str, str]] = []
    waived = 0

    for line in rows:
        kind, expr, got = line.split("|", 2)
        want = REFERENCE[kind](expr)
        if got != want:
            reason = KNOWN_DIVERGENCE.get((kind, expr))
            if reason is not None:
                waived += 1
                print(f"  waived  {kind} {expr!r}: {reason}")
                print(f"            python : {want!r}")
                print(f"            flow   : {got!r}")
                continue
            mismatches.append((kind, expr, want, got))

    print(
        f"compared {len(rows)} case(s) across {len(REFERENCE)} entry point(s), "
        f"{waived} waived"
    )

    if mismatches:
        print(f"\n{len(mismatches)} mismatch(es):\n")
        for kind, expr, want, got in mismatches:
            print(f"  {kind}  {expr!r}")
            print(f"    python : {want!r}")
            print(f"    flow   : {got!r}")
        return 1

    print("PASS math_prose expression parity (Flow port matches Python)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
