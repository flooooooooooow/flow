#!/usr/bin/env python3
"""Compile Flow GPU kernels through SPIR-V to MSL or a native Metal library."""

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _flow_to_spirv(source: Path, output: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC) + (
        ":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )
    cmd = [
        sys.executable,
        "-m",
        "flow.transpiler",
        str(source),
        "--mlir",
        "--mlir-gpu",
        "--emit-spirv",
        "--spirv-out",
        str(output),
    ]
    res = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    if res.returncode != 0:
        raise RuntimeError(
            f"Flow -> SPIR-V compilation failed (exit {res.returncode}):\n"
            f"{res.stderr or res.stdout}"
        )


def main() -> int:
    from flow.mlir_spirv import MLIRSPIRVCompiler

    parser = argparse.ArgumentParser(
        description="Flow GPU -> SPIR-V -> Metal compiler driver"
    )
    parser.add_argument("input", help="Flow source or an existing .spv binary")
    parser.add_argument("-o", "--output", help="Output .metal or .metallib path")
    parser.add_argument(
        "--msl-only",
        action="store_true",
        help="Stop after SPIRV-Cross and emit Metal Shading Language",
    )
    parser.add_argument(
        "--sdk",
        default="macosx",
        help="Xcode SDK passed to xcrun for .metallib compilation (default: macosx)",
    )
    parser.add_argument(
        "--spirv-cross-arg",
        action="append",
        default=[],
        help="Additional argument forwarded to spirv-cross; repeat as needed",
    )
    args = parser.parse_args()

    source = Path(args.input)
    if not source.exists():
        parser.error(f"input does not exist: {source}")

    suffix = ".metal" if args.msl_only else ".metallib"
    output = (
        Path(args.output)
        if args.output
        else ROOT / "build" / f"{source.stem}{suffix}"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    compiler = MLIRSPIRVCompiler()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            if source.suffix.lower() == ".spv":
                spirv_path = source
            else:
                spirv_path = Path(tmpdir) / f"{source.stem}.spv"
                _flow_to_spirv(source, spirv_path)

            if args.msl_only:
                compiler.compile_spirv_to_msl(
                    str(spirv_path),
                    str(output),
                    extra_args=args.spirv_cross_arg,
                )
            else:
                msl_path = Path(tmpdir) / f"{source.stem}.metal"
                compiler.compile_spirv_to_msl(
                    str(spirv_path),
                    str(msl_path),
                    extra_args=args.spirv_cross_arg,
                )
                compiler.compile_msl_to_metallib(
                    str(msl_path),
                    str(output),
                    sdk=args.sdk,
                )
    except Exception as exc:
        print(f"Metal compilation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Generated Metal artifact: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
