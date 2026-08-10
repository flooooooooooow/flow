"""Lightweight MISRA/CERT scan over generated C (#277).

Not a full static analyzer — flags common deviations so CI / `flow analyze`
can produce evidence rows for the compliance matrices.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Finding:
    rule: str
    status: str  # VIOLATION | NOTE
    detail: str
    line: int = 0


_HEAP_RE = re.compile(r"\b(malloc|calloc|realloc|free)\s*\(")
_STDIO_RE = re.compile(r"\b(printf|fprintf|sprintf|snprintf|scanf|gets)\s*\(")
_ABORT_RE = re.compile(r"\babort\s*\(")


def scan_c_source(text: str, path: str = "<stdin>") -> List[Finding]:
    findings: List[Finding] = []
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        if _HEAP_RE.search(line):
            findings.append(
                Finding("MISRA 21.3", "VIOLATION", f"dynamic allocation: {stripped[:80]}", i)
            )
        if _STDIO_RE.search(line):
            # FLOW_DIAG default expands to fprintf — note, not hard fail.
            findings.append(
                Finding("MISRA 21.6", "NOTE", f"stdio I/O: {stripped[:80]}", i)
            )
        if _ABORT_RE.search(line):
            findings.append(
                Finding("MISRA 22.1", "NOTE", f"abort() fault path: {stripped[:80]}", i)
            )
    return findings


def format_report(findings: List[Finding], standard: str, source: str) -> str:
    lines = [
        f"Flow analyze ({standard})",
        f"Source: {source}",
        "-" * 60,
    ]
    if not findings:
        lines.append("No flagged patterns.")
        return "\n".join(lines) + "\n"
    for f in findings:
        loc = f":{f.line}" if f.line else ""
        lines.append(f"[{f.status}] {f.rule}{loc}  {f.detail}")
    viol = sum(1 for f in findings if f.status == "VIOLATION")
    notes = sum(1 for f in findings if f.status == "NOTE")
    lines.append("-" * 60)
    lines.append(f"Summary: {viol} violation(s), {notes} note(s)")
    lines.append("See docs/certification/ for the full compliance matrix.")
    return "\n".join(lines) + "\n"


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="flow-analyze", description="Scan generated C for MISRA/CERT patterns")
    p.add_argument("input", help="Generated .c file (or - for stdin)")
    p.add_argument(
        "--standard",
        default="misra-c-2024",
        choices=["misra-c-2024", "cert-c"],
        help="Compliance standard label for the report",
    )
    p.add_argument(
        "--fail-on-violation",
        action="store_true",
        help="Exit 1 when any VIOLATION is reported",
    )
    args = p.parse_args(argv)
    if args.input == "-":
        text = sys.stdin.read()
        source = "<stdin>"
    else:
        path = Path(args.input)
        text = path.read_text()
        source = str(path)
    findings = scan_c_source(text, source)
    sys.stdout.write(format_report(findings, args.standard, source))
    if args.fail_on_violation and any(f.status == "VIOLATION" for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
