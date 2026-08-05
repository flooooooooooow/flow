#!/usr/bin/env python3
"""Verify site/flow-compile.js against the native Flow compiler.

Every runnable snippet in docs/tutorials/*.md is extracted exactly the way
scripts/build_wiki.py's build_tutorial_exercises() extracts it, then run twice:

  native   flow.transpiler -> C -> clang -> execute, capture stdout
  browser  node shim around site/flow-compile.js, capture stdout

The two outputs are diffed. Each snippet lands in one bucket:

  PASS         both ran and stdout matched byte for byte
  UNSUPPORTED  the browser interpreter declined the snippet by name
  REJECTED     the native compiler rejects the snippet and so does the
               interpreter (the tutorial source itself is broken)
  NATIVE-FAIL  native cannot build it but the interpreter produced output,
               so there is nothing to check the output against
  FAIL         a real mismatch: different stdout, or the interpreter errored
               on a snippet the native compiler runs

FAIL must always be zero.

    python3 scripts/verify_browser_interp.py
    python3 scripts/verify_browser_interp.py --filter beginner
    python3 scripts/verify_browser_interp.py --verbose
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ENGINE = ROOT / "site" / "flow-compile.js"

BLOCK_RE = re.compile(r"```(?:flow(?:\s+(?:run|interactive))?)\n(.*?)```", re.DOTALL)

NODE_SHIM = r"""
'use strict';
const fs = require('fs');
require(process.argv[2]);
const files = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const out = {};
for (const [id, path] of Object.entries(files)) {
  const code = fs.readFileSync(path, 'utf8');
  let res;
  const started = Date.now();
  try {
    res = FlowCompile.run(code);
  } catch (err) {
    res = { ok: false, error: 'engine threw: ' + (err && err.stack || err), output: '' };
  }
  out[id] = {
    ok: !!res.ok,
    unsupported: !!res.unsupported,
    construct: res.construct || null,
    error: res.error || null,
    output: res.output || '',
    exitCode: res.exitCode === undefined ? null : res.exitCode,
    steps: res.steps || 0,
    ms: Date.now() - started,
    astLen: (res.ast || '').length,
  };
}
process.stdout.write(JSON.stringify(out));
"""


def extract_snippets() -> list[dict]:
    """Same extraction rule as build_wiki.build_tutorial_exercises()."""
    lessons: list[dict] = []
    for md_path in sorted((DOCS / "tutorials").glob("*.md")):
        if md_path.name == "README.md":
            continue
        text = md_path.read_text(encoding="utf-8", errors="replace")
        track = md_path.stem
        exercise = 0
        for block in BLOCK_RE.finditer(text):
            code = block.group(1).strip()
            if "function main" not in code:
                continue
            exercise += 1
            before = text[: block.start()]
            sub_m = list(re.finditer(r"^### (.+)$", before, re.MULTILINE))
            lessons.append(
                {
                    "id": f"{track}-{exercise}",
                    "track": track,
                    "title": sub_m[-1].group(1) if sub_m else "Exercise",
                    "code": code,
                }
            )
    return lessons


def run_native(snippets: list[dict], work: Path, timeout: int) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    results: dict[str, dict] = {}
    for sn in snippets:
        sid = sn["id"]
        src = work / f"{sid}.flow"
        src.write_text(sn["code"] + "\n", encoding="utf-8")
        cfile = work / f"{sid}.c"
        binf = work / f"{sid}.bin"
        rec: dict = {"id": sid}
        proc = subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(src), "--c", "-o", str(cfile)],
            capture_output=True, text=True, cwd=str(ROOT), env=env, timeout=timeout,
        )
        if proc.returncode != 0:
            rec["stage"] = "transpile"
            rec["error"] = (proc.stdout + proc.stderr).strip()[-600:]
            results[sid] = rec
            continue
        proc = subprocess.run(
            ["clang", "-w", str(cfile), "-o", str(binf), "-lm"],
            capture_output=True, text=True, timeout=timeout,
        )
        if proc.returncode != 0:
            rec["stage"] = "clang"
            rec["error"] = (proc.stdout + proc.stderr).strip()[-600:]
            results[sid] = rec
            continue
        try:
            proc = subprocess.run([str(binf)], capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            rec["stage"] = "timeout"
            results[sid] = rec
            continue
        rec["stage"] = "run"
        rec["stdout"] = proc.stdout
        rec["exit"] = proc.returncode
        results[sid] = rec
    return results


def run_browser(snippets: list[dict], work: Path, timeout: int) -> dict:
    shim = work / "_shim.js"
    shim.write_text(NODE_SHIM, encoding="utf-8")
    index = {sn["id"]: str(work / f"{sn['id']}.flow") for sn in snippets}
    index_path = work / "_index.json"
    index_path.write_text(json.dumps(index), encoding="utf-8")
    proc = subprocess.run(
        ["node", str(shim), str(ENGINE), str(index_path)],
        capture_output=True, text=True, timeout=timeout * max(len(snippets), 1),
    )
    if proc.returncode != 0:
        raise SystemExit(f"node shim failed:\n{proc.stdout}\n{proc.stderr}")
    return json.loads(proc.stdout)


def classify(native: dict, browser: dict) -> tuple[str, str]:
    nat = native or {}
    br = browser or {}
    native_ran = nat.get("stage") == "run"

    if br.get("unsupported"):
        return "UNSUPPORTED", br.get("construct") or (br.get("error") or "")[:70]

    if not native_ran:
        reason = f"native {nat.get('stage', 'missing')}"
        if br.get("ok"):
            return "NATIVE-FAIL", reason + "; interpreter produced output"
        return "REJECTED", reason + "; interpreter also rejects it"

    if not br.get("ok"):
        return "FAIL", "interpreter error: " + (br.get("error") or "unknown")

    if br.get("output", "") != nat.get("stdout", ""):
        return "FAIL", "stdout mismatch"

    if br.get("exitCode") is not None and nat.get("exit") is not None:
        if int(br["exitCode"]) != int(nat["exit"]):
            return "FAIL", f"exit code {br['exitCode']} vs native {nat['exit']}"

    return "PASS", ""


def diff_text(expected: str, got: str, limit: int = 24) -> str:
    exp = expected.split("\n")
    act = got.split("\n")
    out = []
    for i in range(max(len(exp), len(act))):
        e = exp[i] if i < len(exp) else "<missing>"
        a = act[i] if i < len(act) else "<missing>"
        if e != a:
            out.append(f"      line {i + 1}: native {e!r}")
            out.append(f"              browser {a!r}")
        if len(out) >= limit:
            out.append("      ...")
            break
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--filter", default="", help="only snippets whose id contains this")
    ap.add_argument("--verbose", action="store_true", help="show diffs and messages")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--keep", action="store_true", help="keep the scratch directory")
    ap.add_argument("--json", default="", help="write the full report to this path")
    args = ap.parse_args()

    if shutil.which("node") is None:
        print("node is required to run the browser interpreter", file=sys.stderr)
        return 2
    if shutil.which("clang") is None:
        print("clang is required to build the native reference", file=sys.stderr)
        return 2

    snippets = extract_snippets()
    if args.filter:
        snippets = [s for s in snippets if args.filter in s["id"]]
    if not snippets:
        print("no snippets matched")
        return 1

    work = Path(tempfile.mkdtemp(prefix="flow-interp-verify-"))
    try:
        print(f"Running {len(snippets)} tutorial snippets natively ...")
        native = run_native(snippets, work, args.timeout)
        print("Running the same snippets through site/flow-compile.js under node ...")
        browser = run_browser(snippets, work, args.timeout)

        rows = []
        for sn in snippets:
            verdict, note = classify(native.get(sn["id"]), browser.get(sn["id"]))
            rows.append({**sn, "verdict": verdict, "note": note})

        by_track: "OrderedDict[str, Counter]" = OrderedDict()
        for row in rows:
            by_track.setdefault(row["track"], Counter())[row["verdict"]] += 1

        buckets = ["PASS", "UNSUPPORTED", "REJECTED", "NATIVE-FAIL", "FAIL"]
        width = max(len(t) for t in by_track) + 2
        print()
        header = "tutorial".ljust(width) + "".join(b.rjust(13) for b in buckets)
        print(header)
        print("-" * len(header))
        totals: Counter = Counter()
        for track, counts in by_track.items():
            totals.update(counts)
            print(track.ljust(width) + "".join(str(counts.get(b, 0)).rjust(13) for b in buckets))
        print("-" * len(header))
        print("TOTAL".ljust(width) + "".join(str(totals.get(b, 0)).rjust(13) for b in buckets))
        print()

        for row in rows:
            if row["verdict"] in ("PASS",):
                continue
            print(f"  {row['verdict']:<12} {row['id']:<22} {row['note']}")
            if args.verbose and row["verdict"] == "FAIL":
                nat = native.get(row["id"], {})
                br = browser.get(row["id"], {})
                if row["note"] == "stdout mismatch":
                    print(diff_text(nat.get("stdout", ""), br.get("output", "")))
                else:
                    print(f"      {br.get('error')}")

        if args.json:
            Path(args.json).write_text(
                json.dumps({"rows": rows, "native": native, "browser": browser}, indent=1),
                encoding="utf-8")

        fails = totals.get("FAIL", 0)
        print()
        if fails:
            print(f"FAILED: {fails} snippet(s) disagree with the native compiler.")
            return 1
        print("OK: no snippet disagrees with the native compiler.")
        return 0
    finally:
        if args.keep:
            print(f"scratch kept at {work}")
        else:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
