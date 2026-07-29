#!/usr/bin/env python3
"""Verify that every .flow file under examples/ (and apps/, benchmarks/) compiles.

For each file this runs the same pipeline as `./flow test --tier2`:
  1. transpile: python3 -m flow.transpiler <file> --c --lenient -o <tmp>.c
  2. cgen check: clang -fsyntax-only -Wno-everything <tmp>.c

and regenerates the status table in examples/STATUS.md.

Usage (from repo root):
  python3 scripts/verify_examples.py                 # sweep + rewrite examples/STATUS.md
  python3 scripts/verify_examples.py --roots examples
  python3 scripts/verify_examples.py --json out.json --no-write

Helm task: flow-examples-status
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROOTS = ["examples", "apps", "benchmarks"]
DEFAULT_TIMEOUT = 30  # seconds per stage per file
STATUS_MD = REPO_ROOT / "examples" / "STATUS.md"


def discover(roots: list[str]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        base = REPO_ROOT / root
        if not base.is_dir():
            continue
        files.extend(p for p in base.rglob("*.flow") if "third_party" not in p.parts)
    return sorted(set(files))


def shorten(text: str, limit: int = 110) -> str:
    text = " ".join(text.split())
    text = text.replace("|", "\\|")
    if len(text) > limit:
        text = text[: limit - 3] + "..."
    return text


def categorize_transpile_failure(output: str) -> tuple[str, str]:
    """Return (category, short_reason) for a failed transpile."""
    lines = [ln.strip() for ln in output.splitlines() if ln.strip()]
    # Python traceback => internal compiler error
    if any(ln.startswith("Traceback (most recent call last)") for ln in lines):
        exc = lines[-1] if lines else "unknown exception"
        return "internal error", shorten(exc)
    # Look for an explicit error line (last one wins: usually the most specific)
    err_line = ""
    for ln in lines:
        low = ln.lower()
        if "error" in low or "unexpected" in low or "unknown" in low:
            err_line = ln
    if not err_line:
        err_line = lines[-1] if lines else "no output"
    low = err_line.lower()
    # Note: check parser patterns before "type" — "Expected TokenType.X" messages
    # come from the parser, not the type checker.
    if ("parse" in low or "unexpected" in low or "syntax" in low
            or "tokentype" in low or "expected token" in low):
        return "parser", shorten(err_line)
    if "type" in low:
        return "typecheck", shorten(err_line)
    if "module" in low or "import" in low:
        return "module resolution", shorten(err_line)
    return "transpile error", shorten(err_line)


def check_one(flow_file: Path, timeout: int, run_clang: bool, tmp_dir: str) -> dict:
    rel = flow_file.relative_to(REPO_ROOT).as_posix()
    c_file = Path(tmp_dir) / (rel.replace("/", "-") + ".c")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src") + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )
    result = {"file": rel, "status": "pass", "category": "", "reason": ""}

    # Stage 1: transpile Flow -> C
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(flow_file),
             "--c", "--lenient", "-o", str(c_file)],
            capture_output=True, text=True, timeout=timeout,
            env=env, cwd=REPO_ROOT,
        )
    except subprocess.TimeoutExpired:
        result.update(status="fail", category="timeout",
                      reason=f"transpile exceeded {timeout}s")
        return result
    if proc.returncode != 0 or not c_file.exists():
        cat, reason = categorize_transpile_failure(proc.stderr + "\n" + proc.stdout)
        result.update(status="fail", category=cat, reason=reason)
        return result

    # Stage 2: clang syntax check of generated C (same as ./flow test tier2)
    if run_clang:
        try:
            proc = subprocess.run(
                ["clang", "-fsyntax-only", "-Wno-everything", str(c_file)],
                capture_output=True, text=True, timeout=timeout, cwd=REPO_ROOT,
            )
        except subprocess.TimeoutExpired:
            result.update(status="fail", category="timeout",
                          reason=f"clang exceeded {timeout}s")
            return result
        if proc.returncode != 0:
            first_err = ""
            for ln in proc.stderr.splitlines():
                if "error:" in ln:
                    # Strip the temp-file path prefix: keep "line:col: error: ..."
                    first_err = re.sub(r"^.*\.flow\.c:", "generated C ",
                                       ln.strip())
                    break
            result.update(status="fail", category="cgen (invalid C)",
                          reason=shorten(first_err or proc.stderr.strip()))
            return result

    return result


def compiler_version() -> str:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT,
        ).stdout.strip()
    except OSError:
        commit = "unknown"
    version = "unknown"
    pyproject = REPO_ROOT / "pyproject.toml"
    if pyproject.is_file():
        m = re.search(r'^version\s*=\s*"([^"]+)"', pyproject.read_text(), re.M)
        if m:
            version = m.group(1)
    return f"flow {version} @ {commit}"


def write_status_md(results: list[dict], roots: list[str], timeout: int) -> None:
    total = len(results)
    passed = [r for r in results if r["status"] == "pass"]
    failed = [r for r in results if r["status"] == "fail"]

    by_cat: dict[str, int] = {}
    for r in failed:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1

    by_dir: dict[str, list[int]] = {}
    for r in results:
        parts = r["file"].split("/")
        key = "/".join(parts[:2]) if len(parts) > 2 else parts[0]
        entry = by_dir.setdefault(key, [0, 0])
        entry[0 if r["status"] == "pass" else 1] += 1

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []
    lines.append("# Flow Examples Compile Status")
    lines.append("")
    lines.append(f"> Generated by `scripts/verify_examples.py` on {now} "
                 f"with {compiler_version()}.")
    lines.append("> Regenerate with: `python3 scripts/verify_examples.py`")
    lines.append("")
    lines.append("Each file is compile-checked (not executed) with the same pipeline as "
                 "`./flow test --tier2`: Flow -> C via `flow.transpiler --c --lenient`, "
                 "then `clang -fsyntax-only` on the generated C. "
                 f"Per-stage timeout: {timeout}s. Roots swept: "
                 + ", ".join(f"`{r}/`" for r in roots) + ".")
    lines.append("")
    verify_failed = sum(1 for r in failed if r["file"].startswith("examples/verify/"))
    if verify_failed:
        lines.append(
            f"> **Note:** {verify_failed} of the failures below are under "
            "`examples/verify/`, the `flow-verify` proof corpus. That corpus "
            "is written *ahead of* the verification-keyword parser/checker "
            "(see [verification.md](../docs/language/verification.md)) and "
            "intentionally explores notation (set operators, Euclidean "
            "ratios, ghost contracts) that isn't implemented yet — these are "
            "not core-Flow regressions. See "
            "[flow-verify-parser-status.md](../docs/third-party/flow-verify-parser-status.md) "
            "for a categorized breakdown, or regenerate it with "
            "`python3 scripts/triage_verify_failures.py`."
        )
        lines.append("")
    lines.append("## Totals")
    lines.append("")
    lines.append(f"- **{total}** files checked, **{len(passed)}** pass "
                 f"({100 * len(passed) / total:.1f}%), **{len(failed)}** fail")
    for cat in sorted(by_cat, key=by_cat.get, reverse=True):
        lines.append(f"  - {cat}: {by_cat[cat]}")
    lines.append("")
    lines.append("## By directory")
    lines.append("")
    lines.append("| Directory | Pass | Fail |")
    lines.append("|---|---:|---:|")
    for key in sorted(by_dir):
        p, f = by_dir[key]
        lines.append(f"| `{key}/` | {p} | {f} |")
    lines.append("")
    if failed:
        lines.append("## Failures")
        lines.append("")
        lines.append("| File | Category | Reason |")
        lines.append("|---|---|---|")
        for r in failed:
            lines.append(f"| `{r['file']}` | {r['category']} | {r['reason']} |")
        lines.append("")
    lines.append("## All files")
    lines.append("")
    lines.append("<details>")
    lines.append(f"<summary>Full per-file table ({total} files)</summary>")
    lines.append("")
    lines.append("| File | Status | Failure reason |")
    lines.append("|---|---|---|")
    for r in results:
        mark = "pass" if r["status"] == "pass" else "FAIL"
        reason = f"{r['category']}: {r['reason']}" if r["status"] == "fail" else ""
        lines.append(f"| `{r['file']}` | {mark} | {reason} |")
    lines.append("")
    lines.append("</details>")
    lines.append("")
    STATUS_MD.write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--roots", nargs="+", default=DEFAULT_ROOTS)
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--no-clang", action="store_true",
                    help="skip the clang -fsyntax-only stage (tier1 only)")
    ap.add_argument("--json", metavar="PATH", help="also dump raw results as JSON")
    ap.add_argument("--no-write", action="store_true",
                    help="do not rewrite examples/STATUS.md")
    args = ap.parse_args()

    files = discover(args.roots)
    if not files:
        print("No .flow files found", file=sys.stderr)
        return 1
    print(f"Checking {len(files)} .flow files with {args.jobs} workers...")

    tmp_dir = tempfile.mkdtemp(prefix="flow-verify-")
    results: list[dict] = []
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as ex:
            futures = {ex.submit(check_one, f, args.timeout, not args.no_clang,
                                 tmp_dir): f for f in files}
            done = 0
            for fut in concurrent.futures.as_completed(futures):
                results.append(fut.result())
                done += 1
                if done % 100 == 0:
                    print(f"  {done}/{len(files)}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    results.sort(key=lambda r: r["file"])
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = len(results) - passed
    print(f"\n{passed} pass / {failed} fail out of {len(results)}")

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2))
        print(f"JSON written to {args.json}")
    if not args.no_write:
        write_status_md(results, args.roots, args.timeout)
        print(f"Status table written to {STATUS_MD.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
