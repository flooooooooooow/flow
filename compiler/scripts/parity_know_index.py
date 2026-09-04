#!/usr/bin/env python3
"""Parity gate: Flow port of the `flow know` index and rendering vs the Python.

Runs examples/compilers/know_index_demo.flow (which prints one
`KIND|input|result` line per case), feeds the same inputs through
src/flow/know.py, and fails on any disagreement.

    python3 compiler/scripts/parity_know_index.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEMO = ROOT / "examples" / "compilers" / "know_index_demo.flow"

sys.path.insert(0, str(ROOT / "src"))

import flow.know as know  # noqa: E402
import flow.proof_document as pdoc  # noqa: E402
from flow.claim_address import to_legacy_path, try_parse_claim_address  # noqa: E402

# Keys are compared as sets: Python builds them in a set, so their order is
# not part of the contract.
SET_KINDS = {"KEYS"}


def search_roots(project_root: str) -> str:
    return "\n".join(know._default_search_roots(project_root))


def index_keys(spec: str) -> str:
    module, claim_path = spec.split("~", 1)
    keys = {claim_path, know._qualify(module, claim_path)}
    addr = try_parse_claim_address(claim_path)
    if addr:
        keys.add(addr.guillemets)
        keys.add(addr.slug)
        keys.add(addr.display)
        keys.add(to_legacy_path(addr))
        keys.add(know._qualify(module, addr.guillemets))
        keys.add(know._qualify(module, to_legacy_path(addr)))
    keys.discard("")
    return "\n".join(sorted(keys))


def lookup_matches(spec: str) -> str:
    key, query, claim_path = spec.split("~", 2)
    hit = key.endswith(query) or query.endswith(claim_path)
    return "1" if hit else "0"


def qualify(spec: str) -> str:
    module, claim_path = spec.split("~", 1)
    return know._qualify(module, claim_path)


# The demo's KNOW cases, keyed by the label it prints.
KNOW_CASES = {
    "full": dict(
        qualified_path="verify.nat.Nat/+.zero-left",
        claim_path="Nat/+.zero-left",
        means="Adding zero on the left does not change the number.",
        claim_expr="zero + n == n",
        tier="definition",
        from_source="Peano axioms",
        needs=["Nat/+.succ-right", "Eq/=.refl"],
        used_by=["Nat/+.order-does-not-matter"],
        file_path="lib/verify/nat_plus.flow",
    ),
    "minimal": dict(
        qualified_path="verify.misc.thing",
        claim_path="not-a-claim-address",
        file_path="lib/verify/misc.flow",
    ),
    "geometry": dict(
        qualified_path=(
            "verify.geo.«Geometry» «triangle» "
            "«interior angles sum to two right angles»"
        ),
        claim_path="«Geometry» «triangle» «interior angles sum to two right angles»",
        claim_expr="angle_alpha + angle_beta + angle_gamma == two_right_angles",
        tier="derived",
        file_path="lib/verify/geometry.flow",
    ),
}


def format_know(label: str) -> str:
    case = KNOW_CASES[label]
    meta = pdoc.TheoremMeta(
        means=case.get("means", ""),
        from_source=case.get("from_source", ""),
        tier=case.get("tier", ""),
        needs=list(case.get("needs", [])),
        used_by=list(case.get("used_by", [])),
    )
    thm = pdoc.TheoremDoc(
        claim_path=case["claim_path"],
        params="",
        meta=meta,
        steps=[],
        claim_expr=case.get("claim_expr", ""),
        file_path=case["file_path"],
    )
    entry = know.ClaimEntry(
        theorem=thm,
        module=pdoc.ModuleDoc(),
        qualified_path=case["qualified_path"],
    )
    return know.format_know(entry)


REFERENCE = {
    "ROOTS": search_roots,
    "QUERY": know._normalize_query,
    "PREFIX": know._package_prefix,
    "QUAL": qualify,
    "KEYS": index_keys,
    "MATCH": lookup_matches,
    "KNOW": format_know,
}

KNOWN_DIVERGENCE: dict[tuple[str, str], str] = {}


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

    # Results span lines, so a record continues until the next known prefix.
    rows: list[str] = []
    for line in stdout_data.splitlines():
        if line.strip() == "##END##":
            break
        head = line.split("|", 1)[0]
        if line.count("|") >= 2 and head in REFERENCE:
            rows.append(line)
        elif rows:
            rows[-1] = rows[-1] + "\n" + line
    if not rows:
        sys.stderr.write(stdout_data)
        sys.exit("demo produced no comparable output")
    return rows


def main() -> int:
    rows = run_demo()
    mismatches: list[tuple[str, str, str, str]] = []
    waived = 0

    for line in rows:
        kind, given, got = line.split("|", 2)
        want = REFERENCE[kind](given)
        if kind in SET_KINDS:
            same = set(got.split("\n")) == set(want.split("\n"))
        else:
            same = got == want
        if not same:
            reason = KNOWN_DIVERGENCE.get((kind, given))
            if reason is not None:
                waived += 1
                print(f"  waived  {kind} {given!r}: {reason}")
                continue
            mismatches.append((kind, given, want, got))

    print(
        f"compared {len(rows)} case(s) across {len(REFERENCE)} entry point(s), "
        f"{waived} waived"
    )

    if mismatches:
        print(f"\n{len(mismatches)} mismatch(es):\n")
        for kind, given, want, got in mismatches:
            print(f"  {kind}  {given!r}")
            print(f"    python : {want!r}")
            print(f"    flow   : {got!r}")
        return 1

    print("PASS know index parity (Flow port matches Python)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
