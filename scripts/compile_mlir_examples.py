#!/usr/bin/env python3
"""Compile all examples through MLIR, optionally emit SPIR-V for @gpu kernels."""

import argparse
import os
import subprocess
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def has_mlir_spirv_tools() -> bool:
    return shutil.which("mlir-opt") is not None and shutil.which("mlir-translate") is not None


def is_gpu_example(path: Path) -> bool:
    try:
        text = path.read_text()
        return "@gpu" in text
    except Exception:
        return False


def collect_examples() -> list[Path]:
    return [p for p in EXAMPLES.rglob("*.flow") if p.is_file()]


def run_mlir(path: Path, emit_gpu: bool, emit_spirv: bool) -> tuple[int, str]:
    args = ["python3", "-m", "flow.transpiler", str(path), "--mlir"]
    if emit_gpu:
        args.append("--mlir-gpu")
    if emit_spirv:
        args.append("--emit-spirv")
    env = os.environ.copy()
    env["PYTHONPATH"] = f\"{ROOT / 'src'}\" + (\":\" + env.get(\"PYTHONPATH\") if env.get(\"PYTHONPATH\") else \"\")\n+    res = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, env=env)
    return res.returncode, res.stderr + res.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fail-fast", action="store_true")
    ap.add_argument("--emit-spirv", action="store_true")
    args = ap.parse_args()

    examples = collect_examples()
    spirv_ok = args.emit_spirv and has_mlir_spirv_tools()

    failed = 0
    for ex in examples:
        emit_gpu = is_gpu_example(ex)
        emit_spv = spirv_ok and emit_gpu
        code, out = run_mlir(ex, emit_gpu=emit_gpu, emit_spirv=emit_spv)
        if code != 0:
            failed += 1
            print(f"FAIL: {ex}")
            print(out)
            if args.fail_fast:
                return 1
        else:
            print(f"OK:   {ex}")

    if failed:
        print(f"{failed} example(s) failed MLIR compilation")
        return 1
    print("All examples compiled through MLIR")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
