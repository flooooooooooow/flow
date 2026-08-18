#!/usr/bin/env python3
"""Verify the Flow code examples embedded in the documentation.

Every ```flow block is compiled. A block passes when it verifies as written, or
verifies inside a generated harness, or is tagged `expect-error` and does fail,
or carries `ignore="reason"`. Anything else is unverified.

Two tiers:

* **fast** (default) parses and type-checks in process. All 775 blocks take
  about a tenth of a second, so this is cheap enough to run on every commit.
* **deep** (`--deep`) additionally transpiles to C and runs clang over the
  blocks that carry a `main`, which are the ones that could actually execute.

The harness exists because most documented examples are fragments by design: a
page about struct syntax shows a struct, not a program around it. Rather than
padding every snippet with a ceremonial `main`, the checker tries a short ladder
of wrappers and records which rung each block needed. That record is the point.
A block that only verifies under the loosest wrapper stays visible in the ledger
instead of vanishing into a green count.

Usage:
    python3 scripts/check_doc_examples.py --report
    python3 scripts/check_doc_examples.py --write-ledger
    python3 scripts/check_doc_examples.py --deep
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from docs_blocks import Block, InfoStringError, collect  # noqa: E402

LEDGER = ROOT / "docs" / "generated" / "example-status.json"

# Harness rungs, loosest last. `standalone` means the block is already a
# complete compilation unit.
MODES = ("standalone", "decl-wrap", "stmt-wrap", "flow-body")

MAIN_STUB = "\nfunction main() -> i32 {\n    return 0\n}\n"


def _harness(code: str, mode: str) -> str:
    if mode == "standalone":
        return code
    if mode == "decl-wrap":
        # Declarations with no entry point: give them one.
        return code + MAIN_STUB
    if mode == "stmt-wrap":
        # Bare statements: put them in a body.
        body = "\n".join("    " + line if line.strip() else line
                         for line in code.splitlines())
        return f"function main() -> i32 {{\n{body}\n    return 0\n}}\n"
    if mode == "flow-body":
        # Dynamics fragments: `state x: f64 = 0.0`, `x evolves as -x`, and the
        # rest of the `flow` block vocabulary, which is only legal inside one.
        body = "\n".join("    " + line if line.strip() else line
                         for line in code.splitlines())
        return f"flow Demo {{\n{body}\n}}\n" + MAIN_STUB
    raise ValueError(mode)


@dataclass
class Result:
    block: Block
    status: str  # verified | ignored | expected-error | unverified | bad-info
    mode: Optional[str] = None
    detail: str = ""

    def row(self) -> dict:
        out = {
            "id": self.block.ident,
            "path": self.block.path,
            "line": self.block.line,
            "status": self.status,
        }
        if self.mode:
            out["mode"] = self.mode
        if self.detail:
            out["detail"] = self.detail[:400]
        if self.block.ignored:
            out["reason"] = self.block.ignored
        return out


# Expression forms that do nothing when they stand alone as a statement.
# Their presence after wrapping means the text was never statements: Flow reads
# `state angle` as two bare variables and `angle evolves as velocity` as a
# variable followed by a cast of `evolves` to type `velocity`. Both parse, and
# both mean nothing like what the surrounding prose says. Counting those as
# verified would make the whole check worthless.
_NOOP_STATEMENTS = (
    "Variable",
    "Literal",
    "CastExpression",
    "BinaryOperation",
    "FieldAccess",
    "ArrayAccess",
    "UnaryOperation",
)


def _degenerate(decls) -> str:
    """Report a no-op statement in a synthesized main, if there is one."""
    for decl in decls:
        if getattr(decl, "name", None) != "main":
            continue
        body = getattr(getattr(decl, "body", None), "statements", [])
        for stmt in body:
            kind = type(stmt).__name__
            if kind in _NOOP_STATEMENTS:
                return f"no-op {kind} statement; the text is not statements"
    return ""


def _try_compile(source: str, guard_noop: bool = False) -> tuple[bool, str]:
    """Parse and type-check one unit. Returns (ok, first diagnostic)."""
    from flow.parser import parse_flow_code
    from flow.type_checker import TypeChecker

    # The compiler prints notes to stdout on some paths; keep the report clean.
    sink = io.StringIO()
    try:
        with redirect_stdout(sink), redirect_stderr(sink):
            decls = parse_flow_code(source)
            checker = TypeChecker()
            checker.strict = False
            report = checker.check(decls)
    except Exception as exc:  # parse errors are exceptions, not diagnostics
        return False, f"{type(exc).__name__}: {exc}"
    if report.errors:
        return False, str(report.errors[0])
    if guard_noop:
        problem = _degenerate(decls)
        if problem:
            return False, problem
    return True, ""


def verify(block: Block, allowed_modes: tuple[str, ...] = MODES) -> Result:
    if block.ignored:
        return Result(block, "ignored", detail=block.ignored)

    # An explicit mode pins the block to one rung.
    if "flow-body" in block.flags:
        allowed_modes = ("flow-body",)
    elif "no-harness" in block.flags:
        allowed_modes = ("standalone",)

    first_error = ""
    noop_error = ""
    for mode in allowed_modes:
        # Only the wrapping rungs can manufacture a no-op body. A standalone
        # block that contains one is the page's own business.
        ok, detail = _try_compile(
            _harness(block.code, mode), guard_noop=(mode != "standalone")
        )
        if not ok and detail.startswith("no-op") and not noop_error:
            # The most informative diagnostic available: the block parsed, and
            # what it parsed into was nothing. Prefer it over the syntax error
            # that the stricter rungs produced first.
            noop_error = detail
        if ok:
            if block.expects_error:
                return Result(
                    block,
                    "unverified",
                    mode,
                    f"tagged expect-error but compiles under {mode}",
                )
            return Result(block, "verified", mode)
        if not first_error:
            first_error = detail

    if block.expects_error:
        return Result(block, "expected-error", detail=noop_error or first_error)
    return Result(block, "unverified", detail=noop_error or first_error)


def run(deep: bool = False) -> list[Result]:
    try:
        blocks = collect(lang="flow")
    except InfoStringError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)

    results = [verify(b) for b in blocks]
    if deep:
        _deepen(results)
    return results


def _deepen(results: list[Result]) -> None:
    """Transpile and clang the blocks that carry a `main`.

    Reuses the native runner in verify_browser_interp rather than adding a
    third compile path to the repo.
    """
    import shutil
    import subprocess
    import tempfile

    if not shutil.which("clang"):
        print("note: clang not found, skipping the deep tier", file=sys.stderr)
        return

    targets = [r for r in results if r.status == "verified" and r.block.has_main]
    with tempfile.TemporaryDirectory(prefix="flow_doc_deep_") as td:
        work = Path(td)
        for res in targets:
            src = work / "block.flow"
            out = work / "block.c"
            src.write_text(_harness(res.block.code, res.mode or "standalone"))
            proc = subprocess.run(
                [sys.executable, "-m", "flow.transpiler", str(src), "--c",
                 "-o", str(out)],
                cwd=ROOT,
                env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "src")},
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                res.status = "unverified"
                res.detail = "transpile failed: " + (proc.stderr or proc.stdout)[-300:]
                continue
            cc = subprocess.run(
                ["clang", "-fsyntax-only", "-w", str(out)],
                capture_output=True,
                text=True,
            )
            if cc.returncode != 0:
                res.status = "unverified"
                res.detail = "clang failed: " + cc.stderr[-300:]


def report(results: list[Result], verbose: bool = False) -> None:
    counts = Counter(r.status for r in results)
    modes = Counter(r.mode for r in results if r.status == "verified")
    total = len(results)

    print(f"Flow examples in documentation: {total}\n")
    for status in ("verified", "expected-error", "ignored", "unverified"):
        n = counts.get(status, 0)
        pct = (100 * n / total) if total else 0
        print(f"  {status:16s} {n:4d}  ({pct:4.1f}%)")

    print("\n  verified by harness rung:")
    for mode in MODES:
        if modes.get(mode):
            print(f"    {mode:14s} {modes[mode]:4d}")

    unverified = [r for r in results if r.status == "unverified"]
    if unverified:
        by_file = Counter(r.block.path for r in unverified)
        print("\n  unverified concentrates in:")
        for path, n in by_file.most_common(12):
            print(f"    {n:4d}  {path}")

    if verbose:
        print()
        for res in unverified:
            print(f"  {res.block.ident}: {res.detail.splitlines()[0][:120]}")


def write_ledger(results: list[Result]) -> None:
    payload = {
        "generated": date.today().isoformat(),
        "totals": dict(Counter(r.status for r in results)),
        "blocks": [r.row() for r in sorted(results, key=lambda r: (r.block.path, r.block.line))],
    }
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nledger written to {LEDGER.relative_to(ROOT)}")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", action="store_true", help="print the summary")
    ap.add_argument("--verbose", action="store_true", help="list every failure")
    ap.add_argument("--deep", action="store_true",
                    help="also transpile and clang blocks that have a main")
    ap.add_argument("--write-ledger", action="store_true",
                    help=f"write {LEDGER.relative_to(ROOT)}")
    ap.add_argument("--fail-on-unverified", action="store_true",
                    help="exit non-zero when any block is unverified")
    args = ap.parse_args(argv)

    results = run(deep=args.deep)
    if args.report or not args.write_ledger:
        report(results, verbose=args.verbose)
    if args.write_ledger:
        write_ledger(results)

    if args.fail_on_unverified:
        n = sum(1 for r in results if r.status == "unverified")
        if n:
            print(f"\n{n} unverified example(s)", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
