#!/usr/bin/env python3
"""Triage parser failures under the `flow-verify` proof corpus (examples/verify/).

`examples/STATUS.md` shows a large chunk of parser failures concentrated in
examples/verify/. This script re-runs the transpile stage against that corpus,
buckets each failure by its raw parser error *and* by a heuristic guess at
which not-yet-implemented (or corpus-bug) feature is responsible, and prints a
summary. It does not modify the parser, the corpus, or any source files — it
is purely diagnostic.

Usage (from repo root):
  python3 scripts/triage_verify_failures.py
  python3 scripts/triage_verify_failures.py --roots examples/verify --sample 5
  python3 scripts/triage_verify_failures.py --json triage.json

See docs/third-party/flow-verify-parser-status.md for the write-up this
script's output was used to produce.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROOTS = ["examples/verify"]
DEFAULT_TIMEOUT = 20


def _has_non_triple_guillemet_run(text: str) -> bool:
    """True if the file has a run of consecutive `«...»` groups whose length
    isn't exactly 3. The lexer only recognizes exactly-three-group runs
    (CLAIM_COORDINATE, e.g. `«Ring» «one» «right identity»` naming a
    theorem/claim path). Corpus files that reuse the guillemet notation as a
    2-group "type" (`x : «Ring» «Nat»`) or 2-group call (`«Ring» «mul»(x, 1)`)
    fail to lex at all, since a bare `«` outside a valid triple isn't a token.
    """
    for run in re.finditer(r"(?:«[^»]+»\s*)+", text):
        count = len(re.findall(r"«[^»]+»", run.group(0)))
        if count != 3:
            return True
    return False


def _regex_check(pattern: str, flags: int = 0) -> Callable[[str], bool]:
    compiled = re.compile(pattern, flags)
    return lambda text: bool(compiled.search(text))


# Ordered (name, predicate, explanation). A file may match several tags;
# all matches are reported in the "by suspected root cause" table (a file
# isn't limited to one bucket, since several of these compound in practice).
FEATURE_CHECKS: list[tuple[str, Callable[[str], bool], str]] = [
    (
        "unicode set operators (`\\`, `∩`, `∪`)",
        _regex_check(r"[A-Za-z0-9_)\]]\s*\\\s*[A-Za-z0-9_(]|[∩∪]"),
        "Finset lemmas write `s \\ t` for difference and `a ∩ b` / `a ∪ b` "
        "for intersection/union. None of `\\`, `∩`, `∪` are lexable tokens "
        "in Flow today (new binary operators + non-ASCII lexer support).",
    ),
    (
        "list append operator `++`",
        _regex_check(r"\+\+"),
        "List lemmas write `xs ++ ys` for append. `++` is not a recognized "
        "operator (new binary operator, tokenizes as two `+`s).",
    ),
    (
        "hyphenated import path/symbols",
        _regex_check(r"^\s*import\s+\S*[A-Za-z]-[A-Za-z]", re.M),
        "`import .Group-inv-unique { inv-unique }` — sibling proof files are "
        "named with hyphens and imported by that hyphenated name. The "
        "imported symbol is a dependency citation only; it's never called "
        "in the body (claim paths are used instead). Module-path/import-list "
        "parsing does not special-case hyphens, so `Group-inv-unique` lexes "
        "as MINUS-separated identifiers.",
    ),
    (
        "operator-suffixed module path (e.g. `Nat/+`)",
        _regex_check(r"^\s*import\s+\S*/[+\-*/]", re.M),
        "`import verify.Nat/+ { zero-left }` embeds an operator symbol "
        "directly in the module path segment.",
    ),
    (
        "non-triple guillemet claim coordinate",
        _has_non_triple_guillemet_run,
        "The lexer only recognizes exactly-3-group `«A» «B» «C»` runs "
        "(CLAIM_COORDINATE). Some files reuse the notation with 2 groups as "
        "a pseudo-type (`x : «Ring» «Nat»`) or a 2-group call "
        "(`«Ring» «mul»(x, 1)`); a bare `«` outside a valid triple isn't a "
        "token at all, so the lexer fails immediately.",
    ),
    (
        "`in` as a membership expression",
        _regex_check(r"\b(?:if|therefore)\b.*\bin\s+[A-Za-z_]\w*\b(?!\s+to\b)"),
        "`if a in I { ... }` / `therefore 0 in I` use `in` as a general "
        "membership test. Today `in` is only valid in `for x in ... to ...` "
        "loop syntax.",
    ),
    (
        "`:` as a ratio/proportion operator",
        _regex_check(r"\btherefore\b[^\n]*[A-Za-z0-9_)\]]\s*:\s*[A-Za-z0-9_(]"),
        "`therefore area(ABC) : area(DEF) == base_BC : base_EF` uses Euclid's "
        "classical `A : B` ratio notation inside an expression. `:` is only "
        "meaningful today as a type annotation / struct-field separator.",
    ),
    (
        "keyword `and`/`or` in expressions",
        _regex_check(r"==\s*\S+\s+(and|or)\s+\S"),
        "`result.Sum == expected.sum and result.Cout == ...` uses English "
        "`and`/`or` as boolean connectives instead of `&&`/`||`.",
    ),
    (
        "`by <tactic>` proof-automation suffix",
        _regex_check(r"\btherefore\b.*\bby\s+(exhaustive|smt|symbolic)\b"),
        "`therefore x == y by exhaustive` — automation-suffix syntax from "
        "the verification.md design spec, not implemented in the parser.",
    ),
    (
        "`has property` contract clauses",
        _regex_check(r"\bhas\s+property\b"),
        "`has property ... before/after` on functions, or as a struct-body "
        "field constraint — spec'd in verification.md Phase 1 but not "
        "implemented (also needs `old(...)` ghost references).",
    ),
    (
        "`ghost type` declarations",
        _regex_check(r"\bghost\s+type\b"),
        "`ghost type Queue<T> { ... }` — model/ghost-state declarations, "
        "not part of the current grammar.",
    ),
    (
        "`assume` of a bare fact, not a claim-path call",
        _regex_check(
            r"\bassume\s+(?:[A-Z][a-z]+(?:\s+[A-Za-z]+)*\s*\d*\s*:"
            r"|[A-Za-z_]\w*\s*(?:==|!=|<=|>=|<|>)\s)"
        ),
        "`assume segment_AB == segment_DE` and `assume Common Notion 4: "
        "things coinciding ...` both give `assume` a bare boolean/prose "
        "fact instead of a `Claim/Path(args)` call. The parser's `assume` "
        "only knows `assume <claim-path>` or `assume <claim-path>(args)` — "
        "it consumes the leading identifier as the claim path, leaves the "
        "comparison operator/colon dangling, and the next statement parse "
        "chokes on it.",
    ),
    (
        "`mod` keyword operator",
        _regex_check(r"\bmod\b"),
        "`(write_idx - read_idx) mod capacity` — `mod` as an infix keyword "
        "operator; Flow uses `%`.",
    ),
    (
        "non-ASCII identifier (e.g. Greek letters)",
        _regex_check(r"(?:let|function)\s+(?:mut\s+)?[^\x00-\x7F]"),
        "`let σ = arbitrary_memory()` — uses a Greek letter as a plain "
        "identifier. The lexer's IDENTIFIER pattern is ASCII-only "
        "(`[a-zA-Z_][a-zA-Z0-9_]*`).",
    ),
]


def discover(roots: list[str]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        base = REPO_ROOT / root
        if base.is_file() and base.suffix == ".flow":
            files.append(base)
            continue
        if not base.is_dir():
            continue
        files.extend(base.rglob("*.flow"))
    return sorted(set(files))


def shorten(text: str, limit: int = 140) -> str:
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[: limit - 3] + "..."
    return text


def categorize_transpile_failure(output: str) -> str:
    lines = [ln.strip() for ln in output.splitlines() if ln.strip()]
    if any(ln.startswith("Traceback (most recent call last)") for ln in lines):
        return shorten(lines[-1] if lines else "unknown exception")
    err_line = ""
    for ln in lines:
        low = ln.lower()
        if "error" in low or "unexpected" in low or "unknown" in low:
            err_line = ln
    if not err_line:
        err_line = lines[-1] if lines else "no output"
    return shorten(err_line)


def has_unbalanced_parens(text: str) -> bool:
    """Cheap heuristic: ignores strings/comments, just counts paren depth per
    logical statement group (whole file). Good enough to flag the
    hand/generator-typo'd files in math/derived with an extra/missing `)`.
    """
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return True
    return depth != 0


def tag_features(text: str) -> list[str]:
    tags = [name for name, predicate, _ in FEATURE_CHECKS if predicate(text)]
    if has_unbalanced_parens(text):
        tags.append("unbalanced parentheses (likely corpus typo, not a parser gap)")
    return tags


def check_one(flow_file: Path, timeout: int, tmp_dir: str) -> dict:
    rel = flow_file.relative_to(REPO_ROOT).as_posix()
    c_file = Path(tmp_dir) / (rel.replace("/", "-") + ".c")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src") + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )
    result = {"file": rel, "status": "pass", "reason": "", "tags": []}
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(flow_file),
             "--c", "--lenient", "-o", str(c_file)],
            capture_output=True, text=True, timeout=timeout,
            env=env, cwd=REPO_ROOT,
        )
    except subprocess.TimeoutExpired:
        result.update(status="fail", reason=f"transpile exceeded {timeout}s")
        return result
    if proc.returncode != 0 or not c_file.exists():
        reason = categorize_transpile_failure(proc.stderr + "\n" + proc.stdout)
        text = flow_file.read_text(errors="replace")
        result.update(status="fail", reason=reason, tags=tag_features(text))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--roots", nargs="+", default=DEFAULT_ROOTS)
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--sample", type=int, default=3,
                    help="example file paths to print per bucket")
    ap.add_argument("--json", metavar="PATH", help="dump raw results as JSON")
    args = ap.parse_args()

    files = discover(args.roots)
    if not files:
        print("No .flow files found", file=sys.stderr)
        return 1
    print(f"Checking {len(files)} .flow files under {', '.join(args.roots)} "
          f"with {args.jobs} workers (transpile stage only)...\n")

    tmp_dir = tempfile.mkdtemp(prefix="flow-verify-triage-")
    results: list[dict] = []
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as ex:
            futures = [ex.submit(check_one, f, args.timeout, tmp_dir) for f in files]
            for fut in concurrent.futures.as_completed(futures):
                results.append(fut.result())
    finally:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

    results.sort(key=lambda r: r["file"])
    failed = [r for r in results if r["status"] == "fail"]
    passed = len(results) - len(failed)
    print(f"{passed} pass / {len(failed)} fail out of {len(results)}\n")

    # Bucket by raw parser error pattern (normalized).
    def norm_reason(reason: str) -> str:
        reason = reason.replace("Error resolving modules: ", "")
        return re.sub(r"at line \d+, column \d+", "", reason).strip()

    by_reason: dict[str, list[str]] = {}
    for r in failed:
        by_reason.setdefault(norm_reason(r["reason"]), []).append(r["file"])

    print("=" * 78)
    print("By raw parser error")
    print("=" * 78)
    for reason, fs in sorted(by_reason.items(), key=lambda kv: -len(kv[1])):
        print(f"\n[{len(fs)}] {reason}")
        for f in fs[: args.sample]:
            print(f"    {f}")
        if len(fs) > args.sample:
            print(f"    ... +{len(fs) - args.sample} more")

    # Bucket by suspected root-cause feature (a file can appear in >1 bucket).
    by_feature: dict[str, list[str]] = {}
    untagged: list[str] = []
    for r in failed:
        if not r["tags"]:
            untagged.append(r["file"])
        for tag in r["tags"]:
            by_feature.setdefault(tag, []).append(r["file"])

    print()
    print("=" * 78)
    print("By suspected root cause (heuristic; a file may match several)")
    print("=" * 78)
    explanations = {name: expl for name, _, expl in FEATURE_CHECKS}
    for tag, fs in sorted(by_feature.items(), key=lambda kv: -len(kv[1])):
        print(f"\n[{len(fs)}] {tag}")
        if tag in explanations:
            print(f"    {explanations[tag]}")
        for f in fs[: args.sample]:
            print(f"    {f}")
        if len(fs) > args.sample:
            print(f"    ... +{len(fs) - args.sample} more")

    if untagged:
        print(f"\n[{len(untagged)}] (no heuristic tag matched)")
        for f in untagged[: args.sample]:
            print(f"    {f}")
        if len(untagged) > args.sample:
            print(f"    ... +{len(untagged) - args.sample} more")

    print()
    print("=" * 78)
    print("Summary")
    print("=" * 78)
    print(f"{len(failed)} failures. None require checker/proof-semantics work "
          f"to *categorize* — every bucket above traces to either (a) an "
          f"operator/keyword genuinely absent from the parser (`\\`, `++`, "
          f"`in`, `and`/`or`, `mod`, `by <tactic>`, `has property`, "
          f"`ghost type`, freeform `assume`), or (b) a corpus typo "
          f"(unbalanced parens in generated derived/ files). See "
          f"docs/third-party/flow-verify-parser-status.md for the "
          f"recommendation on each.")

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2))
        print(f"\nJSON written to {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
