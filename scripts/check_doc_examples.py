#!/usr/bin/env python3
"""Verify the Flow code examples embedded in the documentation.

Every ```flow block goes through the same front end a real build uses: the
fill-shader / field / dynamics source expanders, the parser, the strict type
checker, the C generator, and clang. A block passes when it survives that as
written, or survives inside a generated harness, or is tagged `expect-error`
and is genuinely rejected, or carries `ignore="reason"`.

Three things here are load-bearing, and each exists because leaving it out
produced a checker that reported success on documentation that does not work.

**The type checker runs strict.** In lenient mode it does not resolve names, so
undefined identifiers survive all the way to clang. Of the first 120 blocks a
lenient run called verified, 52 failed transpile or clang.

**Blocks go all the way to clang**, for the same reason.

**A block that compiles to nothing does not count.** `theorem nat_zero_add(...)`
and unused generic declarations are erased before codegen, so the C is empty and
clang is trivially happy. A translation unit holding no functions, structs,
enums, effects or capabilities is vacuous, and vacuous is not verified.

The harness exists because most documented examples are fragments by design: a
page about struct syntax shows a struct, not a program wrapped around one. The
checker tries a short ladder of wrappers and records which rung each block
needed, so a block leaning on the loosest wrapper stays visible in the ledger
rather than disappearing into a green count.

Usage:
    python3 scripts/check_doc_examples.py --report
    python3 scripts/check_doc_examples.py --write-ledger
    python3 scripts/check_doc_examples.py --no-clang     # front end only
"""

from __future__ import annotations

import argparse
import io
import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from docs_blocks import Block, InfoStringError, collect  # noqa: E402

LEDGER = ROOT / "docs" / "generated" / "example-status.json"


def _rel(path: Path) -> str:
    """Repo-relative when it can be, absolute otherwise (tests point elsewhere)."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)

# Harness rungs, loosest last. `standalone` means the block is already a
# complete compilation unit.
#
# Two rungs that were designed and then measured out again:
#
# `flow-body` (wrap in `flow Demo { ... }`) rescues zero blocks repo-wide.
# `flow_blocks._validate_flow` rejects a flow that declares no state and
# restricts members to f32/f64, while the documentation writes
# `state angle : Angle`. Its intended cases are either aspirational syntax (an
# `ignore=` case) or already-complete `flow` blocks, where wrapping only
# replaces a useful diagnostic with a worse one.
#
# `decl-wrap` (append a `main`) also rescues zero. A Flow translation unit needs
# no entry point to parse, type-check or generate C, so a block with real
# declarations already passes standalone. All it ever did was supply substance
# to blocks that were otherwise empty, defeating the vacuity check.
MODES = ("standalone", "stmt-wrap", "split-wrap")

# Keywords that open a top-level declaration. Anything at brace depth zero that
# does not start with one of these is a statement.
_DECL_KEYWORDS = (
    "function", "export", "struct", "enum", "trait", "impl", "effect",
    "capability", "const", "type", "distinct", "unit", "import", "extern",
    "module", "flow", "test", "theorem", "let mut", "@",
)


def _split_declarations(code: str) -> tuple[str, str]:
    """Partition a block into leading declarations and trailing statements.

    Documentation very often declares a few things and then shows them being
    used: a `capability` or two followed by a bare `handle ... with ... { }`.
    That shape fits neither rung on its own, because `handle` is not legal at
    top level and `capability` is not legal inside a function.
    """
    lines = code.splitlines()
    depth, boundary = 0, len(lines)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if depth == 0 and stripped and not stripped.startswith("#"):
            if not stripped.startswith(_DECL_KEYWORDS):
                boundary = i
                break
        depth += line.count("{") - line.count("}")
    return "\n".join(lines[:boundary]), "\n".join(lines[boundary:])



def _indent(code: str) -> str:
    return "\n".join(
        "    " + line if line.strip() else line for line in code.splitlines()
    )


def _harness(code: str, mode: str) -> str:
    if mode == "standalone":
        return code
    if mode == "stmt-wrap":
        return f"function main() -> i32 {{\n{_indent(code)}\n    return 0\n}}\n"
    if mode == "split-wrap":
        decls, stmts = _split_declarations(code)
        if not stmts.strip():
            raise _NotApplicable
        body = f"function main() -> i32 {{\n{_indent(stmts)}\n    return 0\n}}\n"
        return (decls + "\n\n" if decls.strip() else "") + body
    raise ValueError(mode)


class _NotApplicable(Exception):
    """This rung has nothing to offer for this block."""


@dataclass
class Result:
    block: Block
    status: str  # verified | ignored | expected-error | unverified
    mode: Optional[str] = None
    detail: str = ""
    stage: str = ""  # parse | types | codegen | clang | vacuous | degenerate
    csource: Optional[str] = None  # held only for the batched clang pass
    modes_tried: list = field(default_factory=list)

    def row(self) -> dict:
        out = {
            "key": self.block.key,
            "path": self.block.path,
            "line": self.block.line,
            "status": self.status,
        }
        if self.mode:
            out["mode"] = self.mode
        if self.stage:
            out["stage"] = self.stage
        if self.detail:
            out["detail"] = self.detail[:300]
        if self.block.ignored:
            out["reason"] = self.block.ignored
        return out


# Expression forms that do nothing when they stand alone as a statement. Their
# presence after wrapping means the text was never statements: Flow reads
# `state angle` as two bare variables and `angle evolves as velocity` as a
# variable followed by a cast of `evolves` to type `velocity`. Both parse, and
# neither means anything like what the surrounding prose says.
_NOOP_STATEMENTS = (
    "Variable",
    "Literal",
    "CastExpression",
    "BinaryOperation",
    "FieldAccess",
    "ArrayAccess",
    "UnaryOperation",
)

_BLOCK_FIELDS = ("body", "then_block", "else_block", "block")


def _walk_statements(node):
    """Yield statements at every depth, so a no-op inside an `if` still counts."""
    for name in _BLOCK_FIELDS:
        inner = getattr(node, name, None)
        for stmt in getattr(inner, "statements", None) or []:
            yield stmt
            yield from _walk_statements(stmt)
    for pair in getattr(node, "elif_blocks", None) or []:
        for stmt in getattr(pair[1], "statements", None) or []:
            yield stmt
            yield from _walk_statements(stmt)


def _degenerate(decls) -> str:
    for decl in decls:
        if getattr(decl, "name", None) != "main":
            continue
        for stmt in _walk_statements(decl):
            kind = type(stmt).__name__
            if kind in _NOOP_STATEMENTS:
                return f"no-op {kind} statement; the text is not statements"
    return ""


def _expand(code: str) -> str:
    """Apply the source expanders that module_resolver applies before parsing.

    Without these, `dsys plant { ... }` and `field T: f64[32] on Line` are
    reported as syntax errors even though both are working Flow that the real
    pipeline compiles.
    """
    from flow.dynamics_dsl import expand_dynamics_dsl, has_dynamics_dsl
    from flow.field_dsl import expand_field_dsl, has_field_dsl

    if has_field_dsl(code):
        code = expand_field_dsl(code)
    if has_dynamics_dsl(code):
        code = expand_dynamics_dsl(code)
    return code


def _compile(source: str, guard_noop: bool, mode: str = "standalone") -> tuple[Optional[str], str, str]:
    """Front end plus codegen. Returns (c_source, stage, detail).

    c_source is None when the block did not get that far.
    """
    from flow.c_generator import flow_to_c
    from flow.module_resolver import resolve_modules
    from flow.monomorphize import monomorphize
    from flow.parser import parse_flow_code
    from flow.shader_dsl import extract_shader_module, has_fill_shader_dsl
    from flow.type_checker import TypeChecker

    sink = io.StringIO()
    try:
        with redirect_stdout(sink), redirect_stderr(sink):
            if has_fill_shader_dsl(source):
                # A fill-shader module is a different language with its own
                # validator and no host translation unit to check.
                mod = extract_shader_module(source)
                if not mod.fills:
                    return None, "parse", "no `shader fill` block in a shader module"
                return "", "shader", ""
            own = parse_flow_code(_expand(source))
    except Exception as exc:
        return None, "parse", f"{type(exc).__name__}: {exc}"

    if guard_noop:
        problem = _degenerate(own)
        if problem:
            return None, "degenerate", problem

    # Imports have to be resolved, or a page that correctly demonstrates a
    # library reads as broken. lib/stdlib/audio/README.md is fourteen complete
    # programs calling functions that all exist; without this they failed as
    # "Undefined function 'bass'".
    #
    # The vacuity and no-op checks stay on the block's own declarations. The
    # resolved unit carries every imported declaration too, and counting those
    # would let `import` alone make an empty block look substantial.
    decls = own
    if any(type(d).__name__ == "ImportDecl" for d in own):
        with tempfile.TemporaryDirectory(prefix="flow_doc_mod_") as td:
            unit = Path(td) / "block.flow"
            unit.write_text(source)
            try:
                with redirect_stdout(sink), redirect_stderr(sink):
                    decls = resolve_modules(str(unit))
            except Exception as exc:
                return None, "imports", f"{type(exc).__name__}: {exc}"

    try:
        with redirect_stdout(sink), redirect_stderr(sink):
            checker = TypeChecker()
            checker.strict = True
            report = checker.check(decls)
    except Exception as exc:
        return None, "types", f"{type(exc).__name__}: {exc}"
    if report.errors:
        return None, "types", str(report.errors[0])

    # The vacuity check has to ignore anything the harness itself added,
    # otherwise the synthesized `main` supplies the substance and every empty
    # block passes. A block that is only comments, or only a `theorem` the
    # compiler erases, must still be reported as vacuous.
    # Vacuous means the block declares nothing, which is only true of a block
    # that is entirely comments. It does not mean "emits no functions": a page
    # about type aliases legitimately shows one type alias, and `const PI`,
    # `type Bytes = array<u8>` and `unit Meter` each generate real C. An
    # earlier whitelist of "substantive" declaration kinds got this wrong and
    # reported 26 correct examples as empty.
    substantive = own
    if mode in ("stmt-wrap", "split-wrap"):
        # Everything except the bare `return 0` the harness appended.
        substantive = [
            d for d in own
            if len(getattr(getattr(d, "body", None), "statements", None) or []) > 1
        ]
    if not substantive:
        return None, "vacuous", "declares nothing; the block is only comments"

    try:
        with redirect_stdout(sink), redirect_stderr(sink):
            return flow_to_c(monomorphize(decls)), "codegen", ""
    except Exception as exc:
        return None, "codegen", f"{type(exc).__name__}: {exc}"


def _preamble_text(block: Block) -> tuple[str, str]:
    """Return (text, error) for a block's preamble. Empty text when it has none."""
    rel = block.preamble
    if not rel:
        return "", ""
    path = ROOT / rel
    if not path.exists():
        return "", f"preamble {rel!r} does not exist"
    return path.read_text().rstrip() + "\n\n", ""


def _from_mismatch(block: Block) -> str:
    """Empty unless the block claims a source file it no longer matches."""
    rel = block.source_file
    if not rel:
        return ""
    path = ROOT / rel
    if not path.exists():
        return f"from={rel!r} does not exist"
    body = block.code.strip()
    if body and body not in path.read_text(errors="replace"):
        return (
            f"block no longer appears in {rel}; the page and the file have "
            f"drifted, so update whichever is wrong"
        )
    return ""


def verify(block: Block) -> Result:
    if block.ignored:
        return Result(block, "ignored", detail=block.ignored)

    drifted = _from_mismatch(block)
    if drifted:
        return Result(block, "unverified", detail=drifted, stage="from")

    preamble, problem = _preamble_text(block)
    if problem:
        return Result(block, "unverified", detail=problem, stage="preamble")

    modes = ("standalone",) if "no-harness" in block.flags else MODES
    first: tuple[str, str] = ("", "")
    best_noop = ""
    reached_meaning = False
    meaning_detail = ""

    for mode in modes:
        try:
            source = preamble + _harness(block.code, mode)
        except _NotApplicable:
            continue
        csource, stage, detail = _compile(
            source,
            guard_noop=(mode != "standalone"),
            mode=mode,
        )
        if stage in ("types", "vacuous", "codegen", "degenerate"):
            reached_meaning = True
        if stage in ("types", "codegen") and not meaning_detail:
            # The rejection the block is there to demonstrate. Without this the
            # ledger records the standalone parse error instead, which is the
            # harness failing to wrap a fragment rather than the compiler
            # rejecting the program.
            meaning_detail = detail
        if stage == "degenerate" and not best_noop:
            best_noop = detail
        if csource is not None:
            if block.expects_error:
                return Result(
                    block, "unverified", mode,
                    f"tagged expect-error but compiles under {mode}", "types",
                    modes_tried=list(modes),
                )
            return Result(block, "verified", mode, "", stage, csource, list(modes))
        if not first[0]:
            first = (stage, detail)

    if block.expects_error:
        # A block only demonstrates a rejection when the compiler got far enough
        # to reject it on meaning. A syntax error the harness itself
        # manufactured proves nothing, so record which of the two happened.
        return Result(
            block,
            "expected-error",
            detail=meaning_detail or best_noop or first[1],
            stage="types" if reached_meaning else "parse",
        )
    return Result(block, "unverified", detail=best_noop or first[1], stage=first[0])


def _batch_clang(results: list[Result], batch: int = 150) -> None:
    """Run clang over every candidate, a few hundred translation units per call.

    One clang process per block costs several times the whole rest of the run.
    Batching keeps the complete check inside a few seconds.
    """
    if not shutil.which("clang"):
        print("note: clang not found, skipping the clang stage", file=sys.stderr)
        return

    pending = [r for r in results if r.status == "verified" and r.csource]
    if not pending:
        return

    with tempfile.TemporaryDirectory(prefix="flow_doc_c_") as td:
        work = Path(td)
        by_name: dict[str, Result] = {}
        for i, res in enumerate(pending):
            path = work / f"b{i:04d}.c"
            path.write_text(res.csource or "")
            by_name[path.name] = res

        names = list(by_name)
        for start in range(0, len(names), batch):
            chunk = names[start : start + batch]
            proc = subprocess.run(
                ["clang", "-fsyntax-only", "-w", "-Wreturn-type"]
                + [str(work / name) for name in chunk],
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                continue
            for line in proc.stderr.splitlines():
                if ": error:" not in line:
                    continue
                res = by_name.get(Path(line.split(":", 1)[0]).name)
                if res is not None and res.status == "verified":
                    res.status = "unverified"
                    res.stage = "clang"
                    res.detail = line.split(": error:", 1)[1].strip()[:200]


def run(use_clang: bool = True) -> list[Result]:
    try:
        blocks = collect(lang="flow")
    except InfoStringError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)

    results = [verify(b) for b in blocks]
    if use_clang:
        _batch_clang(results)
    for res in results:
        res.csource = None  # do not keep every translation unit alive
    return results


def report(results: list[Result], verbose: bool = False) -> None:
    counts = Counter(r.status for r in results)
    total = len(results)

    print(f"Flow examples in documentation: {total}\n")
    for status in ("verified", "expected-error", "ignored", "unverified"):
        n = counts.get(status, 0)
        pct = (100 * n / total) if total else 0
        print(f"  {status:16s} {n:4d}  ({pct:4.1f}%)")

    modes = Counter(r.mode for r in results if r.status == "verified")
    print("\n  verified by harness rung:")
    for mode in MODES:
        if modes.get(mode):
            print(f"    {mode:14s} {modes[mode]:4d}")

    unverified = [r for r in results if r.status == "unverified"]
    if unverified:
        print("\n  unverified stops at:")
        for stage, n in Counter(r.stage for r in unverified).most_common():
            print(f"    {stage or 'unknown':14s} {n:4d}")
        print("\n  unverified concentrates in:")
        for path, n in Counter(r.block.path for r in unverified).most_common(12):
            print(f"    {n:4d}  {path}")

    if verbose:
        print()
        for res in unverified:
            head = (res.detail or "").splitlines()
            print(f"  {res.block.ident} [{res.stage}] {head[0][:110] if head else ''}")


def write_ledger(results: list[Result]) -> None:
    """Write the ratchet ledger.

    Rows are keyed by content hash rather than by line number. Inserting one
    paragraph at the top of VISION.md shifts all 30 of its blocks; a line key
    would rewrite those 30 rows. Across this repository 178 of the last 813
    commits would have renumbered at least one row, up to 223 at once, which
    turns the ledger into a permanent merge conflict and trains reviewers to
    resolve it blindly. A content key changes exactly when the code changes,
    which is also the moment a block genuinely needs re-verifying.
    """
    # Identical text repeated in one page shares a key and one row; the two
    # copies always verify the same way, so a second row would say nothing.
    by_key: dict[str, dict] = {}
    for res in results:
        by_key.setdefault(res.block.key, res.row())
    rows = sorted(by_key.values(), key=lambda r: (r["path"], r["line"]))
    payload = {
        "generated": date.today().isoformat(),
        "totals": dict(Counter(r.status for r in results)),
        "blocks": rows,
    }
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nledger written to {_rel(LEDGER)}")


def check_ledger(results: list[Result]) -> int:
    """Fail on regressions only; report progress without demanding a rewrite.

    The ledger records the examples that do not compile today. A block is
    allowed to be unverified only if the ledger already says so, keyed by the
    hash of its own text. Edit the block and the key changes, so the exemption
    evaporates and the new text has to compile. That is the ratchet: existing
    debt is grandfathered, new and edited content is not.

    Debt that has since been paid off is reported rather than failed. Making an
    unrelated pull request fail because someone else fixed a doc example would
    teach people to regenerate the file without reading it.
    """
    if not LEDGER.exists():
        print(f"no ledger at {_rel(LEDGER)}; run --write-ledger", file=sys.stderr)
        return 1
    ledger = json.loads(LEDGER.read_text())
    known = {
        row["key"]: row["status"]
        for row in ledger["blocks"]
    }

    regressions: list[Result] = []
    resolved: list[Result] = []
    for res in results:
        was = known.get(res.block.key)
        if res.status == "unverified":
            if was != "unverified":
                regressions.append(res)
        elif was == "unverified":
            resolved.append(res)

    debt = sum(1 for r in results if r.status == "unverified")
    print(f"\nexamples: {len(results)}   unverified: {debt}"
          f"   ledger: {sum(1 for v in known.values() if v == 'unverified')}")

    if resolved:
        print(f"\n{len(resolved)} example(s) now compile that the ledger lists as "
              f"failing. Refresh it with:")
        print("    python3 scripts/check_doc_examples.py --write-ledger")

    if not regressions:
        print("\nno new unverified examples")
        return 0

    print(f"\n{len(regressions)} example(s) do not compile and are not in the "
          f"ledger:")
    for res in regressions:
        head = (res.detail or "").splitlines()
        print(f"    {res.block.ident} [{res.stage}] "
              f"{head[0][:100] if head else ''}")
    print()
    print("A new or edited example has to compile. Tag it `expect-error` if it "
          "is meant to fail,")
    print("or ignore=\"reason\" if it cannot be checked.")
    return 1


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--verbose", action="store_true", help="list every failure")
    ap.add_argument("--no-clang", action="store_true",
                    help="stop after codegen; skip the clang stage")
    ap.add_argument("--write-ledger", action="store_true")
    ap.add_argument("--fail-on-unverified", action="store_true")
    ap.add_argument("--check-ledger", action="store_true",
                    help="fail only on examples that regressed against the ledger")
    args = ap.parse_args(argv)

    results = run(use_clang=not args.no_clang)
    if args.check_ledger:
        return check_ledger(results)
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
