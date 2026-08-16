#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


def _run(cmd: list[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main() -> int:
    ap = argparse.ArgumentParser(description="Optional SIMD check (toolchain-dependent).")
    ap.add_argument("flow_file", nargs="?", default="tests/test_simd_saxpy.flow")
    ap.add_argument("--arch", choices=["auto", "arm64", "x86_64"], default="auto")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    flow_file = (repo_root / args.flow_file).resolve()
    if not flow_file.exists():
        print(f"error: file not found: {flow_file}", file=sys.stderr)
        return 2

    pipeline = repo_root / "tools" / "jit" / "flow_jit_pipeline.py"
    if not pipeline.exists():
        print("error: tools/jit/flow_jit_pipeline.py not found", file=sys.stderr)
        return 2

    # Require toolchain (mlir-opt/mlir-translate/clang) indirectly via pipeline script.
    env = os.environ.copy()
    if "PYTHONPATH" not in env:
        env["PYTHONPATH"] = str(repo_root / "src")

    # Run pipeline to emit asm and keep intermediates.
    proc = subprocess.run(
        [sys.executable, str(pipeline), str(flow_file), "--emit-asm", "--keep"],
        cwd=str(repo_root),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out = proc.stdout + "\n" + proc.stderr
    if proc.returncode != 0:
        print(out)
        return proc.returncode

    m = re.search(r"asm:\s*(.+)$", proc.stdout, flags=re.MULTILINE)
    if not m:
        print(out)
        print("error: could not locate emitted asm path in output", file=sys.stderr)
        return 2

    asm_path = Path(m.group(1).strip())
    if not asm_path.exists():
        print(out)
        print(f"error: emitted asm not found: {asm_path}", file=sys.stderr)
        return 2

    asm = asm_path.read_text(encoding="utf-8", errors="ignore")

    arch = args.arch
    if arch == "auto":
        arch = "arm64" if sys.platform == "darwin" and os.uname().machine == "arm64" else "x86_64"

    if arch == "arm64":
        # NEON patterns: vector regs with lane suffixes and 128-bit loads/stores.
        # (Use single backslashes; these are regex patterns, not literals.)
        patterns = [
            r"\.4s\b",
            r"\bldr\s+q",
            r"\bstr\s+q",
            r"\bfmul\.4s\b",
            r"\bfadd\.4s\b",
            r"\bfmla\b",
            r"\bld1\b",
            r"\bst1\b",
        ]
    else:
        # x86 patterns: ymm/zmm usage or packed float ops.
        patterns = [
            r"\bymm\d+",
            r"\bzmm\d+",
            r"\bv(add|mul|fmadd)ps\b",
            r"\b(vpadd|vpmul)\w+\b",
        ]

    if any(re.search(p, asm) for p in patterns):
        print(f"SIMD detected in asm: {asm_path}")
        return 0

    print(f"No SIMD patterns detected in asm: {asm_path}")
    # Help debug false negatives by printing likely-interesting lines.
    interesting = []
    pattern = re.compile(r"\.4s\b|\bldr\s+q|\bstr\s+q|\bld1\b|\bst1\b|\bymm\d+|\bzmm\d+|\bv(add|mul|fmadd)ps\b")
    for line in asm.splitlines():
        if pattern.search(line):
            interesting.append(line)
            if len(interesting) >= 30:
                break
    if interesting:
        print("--- asm snippet (potential SIMD lines) ---")
        for l in interesting:
            print(l)
        print("--- end snippet ---")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
