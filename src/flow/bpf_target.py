"""Flow eBPF target contract and LLVM object-emission driver.

The target reuses Flow's existing MLIR/LLVM pipeline, then applies BPF-specific
ABI metadata and verifier-oriented restrictions before LLVM's BPF backend emits
an ELF object. Linux loading/attachment and live verifier tests belong in
``flow-kernel``.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


BPFEL_TRIPLE = "bpfel"
BPFEL_DATA_LAYOUT = "e-m:e-p:64:64-i64:64-i128:128-n32:64-S128"
BPF_POINTER_BITS = 64
BPF_MAX_STACK_BYTES = 512


class BPFTargetError(ValueError):
    """Raised when a program cannot be represented by the initial BPF target."""


@dataclass(frozen=True)
class BPFTarget:
    name: str = "bpfel"
    triple: str = BPFEL_TRIPLE
    data_layout: str = BPFEL_DATA_LAYOUT
    pointer_bits: int = BPF_POINTER_BITS
    max_stack_bytes: int = BPF_MAX_STACK_BYTES
    little_endian: bool = True


BPFEL = BPFTarget()

_FORBIDDEN_EXTERNALS = (
    "malloc",
    "calloc",
    "realloc",
    "free",
    "operator new",
    "_Znwm",
    "_Znam",
    "__cxa_throw",
    "__cxa_allocate_exception",
    "_Unwind_",
)

_FORBIDDEN_IR_OPS = (
    " invoke ",
    " landingpad ",
    " resume ",
    " catchswitch ",
    " catchpad ",
    " cleanuppad ",
)


def target_for_name(name: str) -> BPFTarget:
    """Resolve a public Flow BPF target name."""
    normalized = name.strip().lower()
    if normalized in {"bpf", "bpfel", "ebpf"}:
        return BPFEL
    raise BPFTargetError(f"unknown BPF target '{name}' (expected bpfel)")


def with_bpf_target_header(llvm_ir: str, target: BPFTarget = BPFEL) -> str:
    """Apply LLVM's canonical BPF triple and data layout to textual IR."""
    lines = llvm_ir.splitlines()
    filtered = [
        line
        for line in lines
        if not line.startswith("target datalayout =")
        and not line.startswith("target triple =")
    ]
    header = [
        f'target datalayout = "{target.data_layout}"',
        f'target triple = "{target.triple}"',
    ]
    return "\n".join(header + filtered) + "\n"


def validate_bpf_llvm_ir(llvm_ir: str) -> None:
    """Reject known verifier/runtime-invalid constructs before object emission."""
    padded = f" {llvm_ir} "
    for op in _FORBIDDEN_IR_OPS:
        if op in padded:
            raise BPFTargetError(
                f"bpfel does not support exception/unwind IR construct: {op.strip()}"
            )

    for symbol in _FORBIDDEN_EXTERNALS:
        if symbol in llvm_ir:
            raise BPFTargetError(
                f"bpfel cannot depend on userspace runtime symbol '{symbol}'"
            )

    # Variable-sized allocas make stack bounds opaque to the verifier. Constant
    # allocas remain eligible; the backend/verifier enforces the final 512-byte
    # aggregate stack limit.
    for match in re.finditer(r"\balloca\s+[^,\n]+,\s+i\d+\s+([^,\n]+)", llvm_ir):
        count = match.group(1).strip()
        if not re.fullmatch(r"\d+", count):
            raise BPFTargetError(
                "bpfel requires statically bounded stack allocation; "
                f"found dynamic alloca count '{count}'"
            )


def emit_bpf_object(
    llvm_ir: str,
    output: str | Path,
    *,
    clang: str | None = None,
    optimize: str = "2",
) -> Path:
    """Validate LLVM IR and emit a little-endian ELF eBPF object with clang."""
    validate_bpf_llvm_ir(llvm_ir)
    targeted_ir = with_bpf_target_header(llvm_ir)

    compiler = clang or shutil.which("clang")
    if not compiler:
        raise BPFTargetError("clang with the LLVM BPF backend is required")

    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    command = [
        compiler,
        "-target",
        BPFEL.triple,
        f"-O{optimize}",
        "-x",
        "ir",
        "-c",
        "-o",
        str(out),
        "-",
    ]
    result = subprocess.run(
        command,
        input=targeted_ir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise BPFTargetError(f"bpfel object emission failed: {detail}")
    return out


def compile_flow_to_bpf(
    source: str | Path,
    output: str | Path,
    *,
    clang: str | None = None,
    optimize: str = "2",
) -> Path:
    """Compile ``.flow`` source through Flow -> MLIR/LLVM -> ELF eBPF."""
    source_path = Path(source)
    if source_path.suffix != ".flow":
        raise BPFTargetError(f"expected a .flow source file, got '{source_path}'")
    if not source_path.is_file():
        raise BPFTargetError(f"Flow source does not exist: {source_path}")

    with tempfile.TemporaryDirectory(prefix="flow-bpf-") as temp_dir:
        llvm_path = Path(temp_dir) / "program.ll"
        command = [
            sys.executable,
            "-m",
            "flow.transpiler",
            str(source_path),
            "--llvm",
            "--optimize",
            "--opt-level",
            f"O{optimize}",
            "-o",
            str(llvm_path),
        ]
        result = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise BPFTargetError(f"Flow -> LLVM lowering failed for bpfel: {detail}")
        if not llvm_path.is_file():
            raise BPFTargetError("Flow LLVM lowering completed without producing LLVM IR")

        llvm_ir = llvm_path.read_text(encoding="utf-8")
        return emit_bpf_object(llvm_ir, output, clang=clang, optimize=optimize)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile Flow or LLVM IR to ELF eBPF")
    parser.add_argument("input", help="Input .flow or .ll file")
    parser.add_argument("-o", "--output", required=True, help="Output .o path")
    parser.add_argument("--target", default="bpfel", choices=["bpfel"])
    parser.add_argument("-O", dest="optimize", default="2", choices=["0", "1", "2", "3"])
    args = parser.parse_args(argv)

    try:
        target_for_name(args.target)
        input_path = Path(args.input)
        if input_path.suffix == ".flow":
            compile_flow_to_bpf(input_path, args.output, optimize=args.optimize)
        else:
            llvm_ir = input_path.read_text(encoding="utf-8")
            emit_bpf_object(llvm_ir, args.output, optimize=args.optimize)
    except (OSError, BPFTargetError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
