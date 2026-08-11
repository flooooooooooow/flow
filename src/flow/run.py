"""Shell-independent Flow program runner (#400).

Transpiles a .flow file to C, compiles it with clang, and runs the resulting
binary. This is equivalent to `flow run` but works without bash, so it runs
under any shell or directly via `python3 -m flow.run`.

Usage:
    python3 -m flow.run prog.flow [--backend=c|mlir] [--json] [--keep]

--json wraps the program stdout in a JSON envelope with exit code and timing,
suitable for docs builds and CI fixtures.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="flow.run",
        description="Transpile, compile, and run a Flow program (shell-independent).",
    )
    parser.add_argument("input", help="Input .flow file")
    parser.add_argument(
        "--backend",
        choices=["c", "mlir"],
        default="c",
        help="Compilation backend (default: c)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON envelope with stdout, exit code, and timing",
    )
    parser.add_argument(
        "--keep",
        help="Keep the generated C/binary at this path instead of a temp dir",
    )
    parser.add_argument(
        "--lenient",
        action="store_true",
        help="Lenient type checking (warnings only)",
    )
    parser.add_argument(
        "--extra-cflags",
        default="",
        help="Extra clang flags (space-separated)",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        return 1

    basename = input_path.stem

    # Output directory
    if args.keep:
        out_dir = Path(args.keep)
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = Path(tempfile.mkdtemp(prefix="flow_run_"))

    c_path = out_dir / f"{basename}.c"
    exe_path = out_dir / basename

    # Step 1: Transpile
    t0 = time.monotonic()
    transpile_cmd = [
        sys.executable, "-m", "flow.transpiler",
        str(input_path), "--c", "-o", str(c_path),
    ]
    if args.lenient:
        transpile_cmd.append("--lenient")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(transpile_cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        msg = result.stderr.strip() or result.stdout.strip()
        if args.json:
            _emit_json("", 1, t0, error=f"transpile failed: {msg}")
        else:
            print(f"Transpile failed:\n{msg}", file=sys.stderr)
        return 1
    t1 = time.monotonic()

    # Step 2: Compile
    clang = shutil.which("clang") or shutil.which("cc")
    if not clang:
        if args.json:
            _emit_json("", 1, t0, error="clang not found")
        else:
            print("Error: clang not found", file=sys.stderr)
        return 1

    cflags = ["-std=c11", "-O2", "-Wno-everything", "-lm"]
    if args.extra_cflags:
        cflags.extend(args.extra_cflags.split())
    compile_cmd = [clang] + cflags + [str(c_path), "-o", str(exe_path)]
    result = subprocess.run(compile_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        msg = result.stderr.strip()
        if args.json:
            _emit_json("", 1, t0, error=f"compile failed: {msg}")
        else:
            print(f"Compile failed:\n{msg}", file=sys.stderr)
        return 1
    t2 = time.monotonic()

    # Step 3: Run
    result = subprocess.run([str(exe_path)], capture_output=True, text=True)
    t3 = time.monotonic()

    if args.json:
        _emit_json(
            result.stdout,
            result.returncode,
            t0,
            transpile_s=t1 - t0,
            compile_s=t2 - t1,
            run_s=t3 - t2,
            stderr=result.stderr,
        )
    else:
        sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)

    # Cleanup
    if not args.keep:
        shutil.rmtree(out_dir, ignore_errors=True)

    return result.returncode


def _emit_json(
    stdout: str,
    exit_code: int,
    t0: float,
    *,
    transpile_s: float = 0,
    compile_s: float = 0,
    run_s: float = 0,
    stderr: str = "",
    error: str = "",
) -> None:
    envelope = {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "timing": {
            "transpile_s": round(transpile_s, 4),
            "compile_s": round(compile_s, 4),
            "run_s": round(run_s, 4),
            "total_s": round(time.monotonic() - t0, 4),
        },
    }
    if error:
        envelope["error"] = error
    print(json.dumps(envelope, indent=2))


if __name__ == "__main__":
    sys.exit(main())
