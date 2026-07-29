#!/usr/bin/env python3

import argparse
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
    ap = argparse.ArgumentParser("flow-debug")
    ap.add_argument("input", help=".flow file")
    ap.add_argument("--entry", default="main", help="entry function name (default: main)")
    ap.add_argument("--keep", action="store_true", help="keep intermediates")
    ap.add_argument("--opt", default="0", choices=["0", "1", "2", "3"], help="clang optimization level")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    src_root = repo_root / "src"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_root) if not env.get("PYTHONPATH") else f"{src_root}:{env['PYTHONPATH']}"

    mlir_opt = _find_tool("MLIR_OPT", "mlir-opt")
    mlir_translate = _find_tool("MLIR_TRANSLATE", "mlir-translate")
    clang = shutil.which("clang")
    lldb = shutil.which("lldb")

    if not mlir_opt:
        print("error: mlir-opt not found (set MLIR_OPT or install llvm via brew)", file=sys.stderr)
        return 2
    if not mlir_translate:
        print("error: mlir-translate not found (set MLIR_TRANSLATE or install llvm via brew)", file=sys.stderr)
        return 2
    if not clang:
        print("error: clang not found on PATH", file=sys.stderr)
        return 2
    if not lldb:
        print("error: lldb not found on PATH", file=sys.stderr)
        return 2

    tmpdir = Path(tempfile.mkdtemp(prefix="flow_debug_"))
    mlir_file = tmpdir / "out.mlir"
    lowered_mlir_file = tmpdir / "out.lowered.mlir"
    ll_file = tmpdir / "out.ll"
    shim_c = tmpdir / "shim.c"
    exe_file = tmpdir / "a.out"

    # 1) FLOW -> MLIR
    p1 = _run([sys.executable, "-m", "flow.transpiler", args.input, "--mlir", "-o", str(mlir_file)], cwd=str(repo_root), env=env)
    if p1.returncode != 0:
        print(p1.stderr, file=sys.stderr)
        return p1.returncode

    # 2) Lower MLIR → LLVM IR (keep .ll for debugging)
    lowered_mlir_file = tmpdir / "out.lowered.mlir"
    p2 = _run([
        mlir_opt,
        "--mlir-print-op-on-diagnostic=false",
        "--pass-pipeline=builtin.module(func.func(convert-scf-to-cf),convert-cf-to-llvm,func.func(convert-index-to-llvm,convert-arith-to-llvm,convert-math-to-llvm),convert-func-to-llvm,finalize-memref-to-llvm,convert-vector-to-llvm,reconcile-unrealized-casts)",
        str(mlir_file),
        "-o",
        str(lowered_mlir_file),
    ])
    if p2.returncode != 0:
        print(p2.stderr, file=sys.stderr)
        return p2.returncode

    # 3) LLVM IR
    p3 = _run([mlir_translate, "--mlir-to-llvmir", str(lowered_mlir_file), "-o", str(ll_file)])
    if p3.returncode != 0:
        print(p3.stderr, file=sys.stderr)
        return p3.returncode

    # Always rename FLOW's main to _flow_main to avoid clash with shim main
    # (The FLOW file may define a main even if we're debugging a different entry)
    p3b = _run([
        "sed",
        "-i",
        "",
        "s/@main/@_flow_main/g",
        str(ll_file),
    ])
    if p3b.returncode != 0:
        print(p3b.stderr, file=sys.stderr)
        return p3b.returncode

    entry_sym = args.entry
    if entry_sym == "main":
        # If debugging main, point to renamed symbol
        entry_sym = "_flow_main"

    # 4) Build a debuggable executable with a tiny C shim that calls the chosen entry.
    # This makes LLDB breakpoints hit meaningful code even when the FLOW `main` is trivial.
    # Currently supported: entry has signature `() -> i32`.
    if platform.system() == "Darwin":
        # Mach-O often uses an underscore prefix for C symbols. Our LLVM IR may or may not.
        # The shim tries both by declaring both and calling the non-underscored form.
        pass

    shim_c.write_text(
        """
        #include <stdint.h>

        // FLOW entry (expected signature: i32 ()). If the symbol is underscored on Darwin,
        // lld/clang will still resolve the correct one at link time.
        extern int32_t {entry}(void);

        int main(void) {{
            return (int){entry}();
        }}
        """.format(entry=entry_sym),
        encoding="utf-8",
    )

    p4 = _run([
        clang,
        f"-O{args.opt}",
        "-g",
        "-fno-omit-frame-pointer",
        str(shim_c),
        str(ll_file),
        "-o",
        str(exe_file),
    ])
    if p4.returncode != 0:
        print(p4.stderr, file=sys.stderr)
        return p4.returncode

    print(f"exe: {exe_file}")
    if args.keep:
        print(f"kept intermediates in: {tmpdir}")

    # Launch LLDB with breakpoint pre-set on entry function
    os.execvp("lldb", ["lldb", "-o", f"break set -n {entry_sym}", "-o", "run", str(exe_file)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
