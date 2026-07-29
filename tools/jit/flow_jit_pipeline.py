#!/usr/bin/env python3
"""Single-shot FLOW JIT pipeline runner.

Runs:
  FLOW -> MLIR -> (mlir-opt) -> LLVM-dialect MLIR -> (mlir-translate) -> LLVM IR
  -> clang -> dylib/so -> execute main via ctypes

This is intentionally a helper script so you don't have to copy/paste commands.
"""

import argparse
import ctypes
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Dict, List


def _brew_prefix_llvm() -> Optional[str]:
    brew = shutil.which("brew")
    if not brew:
        return None
    res = subprocess.run([brew, "--prefix", "llvm"], capture_output=True, text=True)
    if res.returncode != 0:
        return None
    return res.stdout.strip() or None


def _find_tool(env_key: str, tool: str) -> Optional[str]:
    override = os.environ.get(env_key)
    if override:
        return override

    found = shutil.which(tool)
    if found:
        return found

    prefix = _brew_prefix_llvm()
    if prefix:
        candidate = Path(prefix) / "bin" / tool
        if candidate.exists():
            return str(candidate)

    return None


def _run(cmd: List[str], *, cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser("flow-jit-pipeline")
    ap.add_argument("input", help=".flow file")
    ap.add_argument("--entry", default="main", help="entry function name (default: main)")
    ap.add_argument("--keep", action="store_true", help="keep intermediate files")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--remarks", action="store_true", help="print clang vectorization remarks (loop-vectorize/SLP)")
    ap.add_argument("--emit-llvm", action="store_true", help="print path to emitted LLVM IR (.ll)")
    ap.add_argument("--emit-asm", action="store_true", help="also emit assembly (.s) for inspection")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    src_root = repo_root / "src"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_root) if not env.get("PYTHONPATH") else f"{src_root}:{env['PYTHONPATH']}"

    mlir_opt = _find_tool("MLIR_OPT", "mlir-opt")
    mlir_translate = _find_tool("MLIR_TRANSLATE", "mlir-translate")

    if not mlir_opt:
        print("error: mlir-opt not found (set MLIR_OPT or install llvm via brew)", file=sys.stderr)
        return 2
    if not mlir_translate:
        print("error: mlir-translate not found (set MLIR_TRANSLATE or install llvm via brew)", file=sys.stderr)
        return 2

    tmpdir = Path(tempfile.mkdtemp(prefix="flow_jit_pipeline_"))
    mlir_file = tmpdir / "out.mlir"
    lowered_mlir_file = tmpdir / "out.lowered.mlir"
    ll_file = tmpdir / "out.ll"
    asm_file = tmpdir / "out.s"

    ext = ".dylib" if platform.system() == "Darwin" else ".so"
    lib_file = tmpdir / f"out{ext}"

    # 1) FLOW -> MLIR
    p1 = _run([sys.executable, "-m", "flow.transpiler", args.input, "--mlir", "-o", str(mlir_file)], cwd=str(repo_root), env=env)
    if p1.returncode != 0:
        print(p1.stderr, file=sys.stderr)
        return p1.returncode

    # 2) mlir-opt lowering
    p2 = _run([
        mlir_opt,
        "--canonicalize",
        "--cse",
        "--convert-scf-to-cf",
        "--convert-index-to-llvm",
        "--convert-arith-to-llvm",
        "--convert-cf-to-llvm",
        "--convert-math-to-llvm",
        "--convert-func-to-llvm",
        "--finalize-memref-to-llvm",
        "--convert-vector-to-llvm",
        "--reconcile-unrealized-casts",
        str(mlir_file),
        "-o",
        str(lowered_mlir_file),
    ])
    if p2.returncode != 0:
        print(p2.stderr, file=sys.stderr)
        return p2.returncode

    # 3) mlir-translate
    p3 = _run([mlir_translate, "--mlir-to-llvmir", str(lowered_mlir_file), "-o", str(ll_file)])
    if p3.returncode != 0:
        print(p3.stderr, file=sys.stderr)
        return p3.returncode

    # 4) clang -> shared lib (SIMD-first happens here via -O3 -march=native)
    clang_cmd: List[str] = [
        "clang",
        "-shared",
        "-fPIC",
        "-O3",
        "-march=native",
        "-Wno-override-module",
    ]
    if args.remarks:
        clang_cmd.extend([
            "-Rpass=loop-vectorize",
            "-Rpass=slp-vectorize",
            "-Rpass-missed=loop-vectorize",
            "-Rpass-missed=slp-vectorize",
        ])
    if args.emit_asm:
        clang_cmd.extend(["-S", str(ll_file), "-o", str(asm_file)])
        # Also build the shared library.
        clang_cmd = [
            "clang",
            "-shared",
            "-fPIC",
            "-O3",
            "-march=native",
        ] + ([
            "-Rpass=loop-vectorize",
            "-Rpass=slp-vectorize",
            "-Rpass-missed=loop-vectorize",
            "-Rpass-missed=slp-vectorize",
        ] if args.remarks else []) + [str(ll_file), "-o", str(lib_file)]
        # Separate asm emission so we don't depend on clang supporting -S with -shared together.
        p4a = _run(["clang", "-S", "-O3", "-march=native", str(ll_file), "-o", str(asm_file)])
        if p4a.returncode != 0:
            print(p4a.stderr, file=sys.stderr)
            return p4a.returncode
        p4 = _run(clang_cmd)
    else:
        clang_cmd.extend([str(ll_file), "-o", str(lib_file)])
        p4 = _run(clang_cmd)

    if p4.returncode != 0:
        print(p4.stderr, file=sys.stderr)
        return p4.returncode

    if args.remarks and p4.stderr.strip():
        # clang prints -Rpass remarks to stderr.
        print(p4.stderr)

    if args.verbose:
        print(f"built: {lib_file}")

    if args.emit_llvm:
        print(f"llvm_ir: {ll_file}")
    if args.emit_asm:
        print(f"asm: {asm_file}")

    # 5) execute entry
    lib = ctypes.CDLL(str(lib_file))

    # Mach-O may prefix symbols with _
    entry_names = [args.entry]
    if platform.system() == "Darwin":
        entry_names.insert(0, f"_{args.entry}")

    func = None
    for name in entry_names:
        try:
            func = getattr(lib, name)
            break
        except AttributeError:
            continue

    if func is None:
        print(f"error: entry symbol not found in shared library: tried {entry_names}", file=sys.stderr)
        return 3

    func.restype = ctypes.c_int
    result = func()
    print(result)

    if args.keep:
        print(f"kept intermediates in: {tmpdir}")
    else:
        # Leave cleanup manual for now; tmpdirs are small and useful for debugging.
        pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
