#!/usr/bin/env python3
"""WebAssembly target for Flow's MLIR backend.

This module deliberately does not route through the C generator.  A Flow source
file is first lowered by the existing transpiler to wasm32-compatible LLVM IR,
then LLVM/Clang links that IR directly into a WebAssembly module.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable, Optional


def _find_clang() -> str:
    override = os.environ.get("FLOW_WASM_CLANG") or os.environ.get("CLANG")
    if override:
        return override

    llvm_path = os.environ.get("LLVM_PATH")
    if llvm_path:
        candidate = Path(llvm_path) / "clang"
        if candidate.exists():
            return str(candidate)

    found = shutil.which("clang")
    if found:
        return found

    raise RuntimeError(
        "clang not found. Install an LLVM toolchain or set FLOW_WASM_CLANG/LLVM_PATH."
    )


def llvm_to_wasm(
    llvm_ir: str,
    output: str | Path,
    *,
    exports: Optional[Iterable[str]] = None,
    allow_undefined: bool = True,
    export_memory: bool = True,
    optimize: str = "O2",
) -> Path:
    """Compile LLVM IR directly to a freestanding wasm32 module."""
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if optimize not in {"O0", "O1", "O2", "O3", "Os", "Oz"}:
        raise ValueError(f"unsupported optimization level: {optimize}")

    with tempfile.TemporaryDirectory(prefix="flow_wasm_") as temp_dir:
        llvm_path = Path(temp_dir) / "module.ll"
        llvm_path.write_text(llvm_ir)

        command = [
            _find_clang(),
            "--target=wasm32-unknown-unknown",
            "-x",
            "ir",
            f"-{optimize}",
            "-nostdlib",
            str(llvm_path),
            "-Wl,--no-entry",
        ]

        export_names = list(exports or [])
        if export_names:
            command.extend(f"-Wl,--export={name}" for name in export_names)
        else:
            command.append("-Wl,--export-all")

        if allow_undefined:
            command.append("-Wl,--allow-undefined")
        if export_memory:
            command.append("-Wl,--export-memory")

        command.extend(["-o", str(output_path)])
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                "LLVM IR to WebAssembly compilation failed:\n" + result.stderr.strip()
            )

    return output_path


def flow_to_wasm(
    source: str | Path,
    output: str | Path,
    *,
    exports: Optional[Iterable[str]] = None,
    optimize: str = "O2",
) -> Path:
    """Compile Flow source through MLIR/LLVM IR directly to WebAssembly."""
    source_path = Path(source)
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    with tempfile.TemporaryDirectory(prefix="flow_wasm_ir_") as temp_dir:
        llvm_path = Path(temp_dir) / (source_path.stem + ".ll")
        command = [
            sys.executable,
            "-m",
            "flow.transpiler",
            str(source_path),
            "--wasm32",
            "--llvm",
            "-o",
            str(llvm_path),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                "Flow to LLVM IR compilation failed:\n" + result.stderr.strip()
            )
        return llvm_to_wasm(
            llvm_path.read_text(),
            output,
            exports=exports,
            optimize=optimize,
        )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compile Flow source to WebAssembly via MLIR and LLVM IR"
    )
    parser.add_argument("input", help="Input .flow file")
    parser.add_argument("-o", "--output", required=True, help="Output .wasm file")
    parser.add_argument(
        "--export",
        action="append",
        default=[],
        help="Exact LLVM symbol to export; repeat for multiple symbols. Defaults to export-all.",
    )
    parser.add_argument(
        "-O",
        "--opt-level",
        choices=["O0", "O1", "O2", "O3", "Os", "Oz"],
        default="O2",
    )
    args = parser.parse_args(argv)

    flow_to_wasm(
        args.input,
        args.output,
        exports=args.export or None,
        optimize=args.opt_level,
    )
    print(f"Generated WebAssembly: {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
