#!/usr/bin/env python3
"""Parity gate: Flow port of the proof-file parsing helpers vs the Python.

Runs examples/compilers/proof_parse_demo.flow (which prints one
`KIND|input|result` line per case), feeds the same inputs through the private
helpers in src/flow/proof_document.py, and fails on any disagreement.

    python3 compiler/scripts/parity_proof_parse.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEMO = ROOT / "examples" / "compilers" / "proof_parse_demo.flow"

sys.path.insert(0, str(ROOT / "src"))

import flow.proof_document as pdoc  # noqa: E402


def meta_key(line: str) -> str:
    meta, _ = pdoc._parse_meta_block([line])
    if not meta:
        return ""
    return next(iter(meta))


def meta_value(line: str) -> str:
    meta, _ = pdoc._parse_meta_block([line])
    if not meta:
        return ""
    return next(iter(meta.values()))


def _one_step(line: str):
    """_parse_steps over a single line, returning its ProofStep or None."""
    steps, _claim = pdoc._parse_steps(line)
    return steps[0] if steps else None


def step_kind(line: str) -> str:
    step = _one_step(line)
    return step.kind if step else ""


def step_text(line: str) -> str:
    step = _one_step(line)
    return step.text if step else ""


def step_detail(line: str) -> str:
    step = _one_step(line)
    return step.detail if step else ""


def claim_from_therefore(line: str) -> str:
    _steps, claim = pdoc._parse_steps(line)
    return claim


def _split_brace(spec: str) -> tuple[str, int]:
    index, text = spec.split("@", 1)
    return text, int(index)


def brace_body(spec: str) -> str:
    text, index = _split_brace(spec)
    body, _end = pdoc._extract_brace_body(text, index)
    return body


def brace_end(spec: str) -> str:
    text, index = _split_brace(spec)
    _body, end = pdoc._extract_brace_body(text, index)
    return str(end)


def _thm(claim_path: str = "", means: str = "", claim_expr: str = "", params: str = ""):
    return pdoc.TheoremDoc(
        claim_path=claim_path,
        params=params,
        meta=pdoc.TheoremMeta(means=means),
        steps=[],
        claim_expr=claim_expr,
    )


def claim_sentence(spec: str) -> str:
    means, claim_expr = spec.split("~", 1)
    return pdoc._natural_claim_sentence(_thm(means=means, claim_expr=claim_expr))


def facet_title(spec: str) -> str:
    claim_path, means = spec.split("~", 1)
    return pdoc._facet_title(claim_path, pdoc.TheoremMeta(means=means))


def natural_let(spec: str) -> str:
    step_text, refs = spec.split("~", 1)
    nums = [int(x) for x in refs.split(",") if x.strip()]
    return pdoc._natural_let(step_text, context_refs=nums)


def _entry(number: int, tier: str, label: str = ""):
    return pdoc.TheoremCatalogEntry(
        number=number, tier=tier, title="", claim_path="", label=label
    )


def theorem_ref_plain(spec: str) -> str:
    tier, number = spec.split("~", 1)
    return pdoc._theorem_ref_plain(_entry(int(number), tier))


def theorem_ref_latex(spec: str) -> str:
    label, tier, number = spec.split("~", 2)
    return pdoc._theorem_ref_latex(_entry(int(number), tier, label))


def math_cell(spec: str) -> str:
    return pdoc._render_math_cell_latex(
        pdoc.TutorialLine(number=1, english="", math_latex=spec or None)
    )


def legend_row(spec: str) -> str:
    number, refs = spec.split("~", 1)
    nums = [int(x) for x in refs.split(",") if x.strip()]
    return f"| {pdoc._circled(int(number))} | {pdoc._fmt_refs(nums)} |"


def figure(spec: str) -> str:
    return "\n".join(pdoc.diagram_markdown_embed(spec))


def preamble(spec: str) -> str:
    stem, prefix = spec.split("~", 1)
    return "\n".join(pdoc._latex_preamble(stem, title_prefix=prefix))


REFERENCE = {
    "METAKEY": meta_key,
    "METAVAL": meta_value,
    "KIND": step_kind,
    "TEXT": step_text,
    "DETAIL": step_detail,
    "CLAIM": claim_from_therefore,
    "TEX": pdoc._latex_escape,
    "TEXP": pdoc._latex_escape_params,
    "BRACE": brace_body,
    "BRACEEND": brace_end,
    "PHRASE": pdoc._claim_path_phrase,
    "CLAIMSENT": claim_sentence,
    "FACET": facet_title,
    "LET": natural_let,
    "REFP": theorem_ref_plain,
    "REFL": theorem_ref_latex,
    "MATHCELL": math_cell,
    "LEGEND": legend_row,
    "FIGURE": figure,
    "PREAMBLE": preamble,
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

    # A result may span lines (the LaTeX preamble does), so a new record starts
    # only at a line whose prefix is a known entry point.
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
        if got != want:
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

    print("PASS proof parse parity (Flow port matches Python)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
