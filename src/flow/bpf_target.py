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


@dataclass(frozen=True)
class BPFProgram:
    """Kernel-facing metadata for one exported Flow eBPF program."""

    entry: str
    section: str
    license: str = "GPL"

    @property
    def export_symbol(self) -> str:
        """The symbol to decorate, as the MLIR path actually names it.

        `flow_export_<name>` is a C-backend alias: c_generator emits it for
        `--export`, and the MLIR path does not. Since this target lowers with
        `--llvm`, the definition in the IR carries the plain Flow name.
        """
        return self.entry

    @property
    def candidate_symbols(self) -> tuple[str, ...]:
        """Names the entry may appear under, most explicit first.

        The C backend emits both the mangled definition and a visible
        `flow_export_<name>` alias, so when both are present the alias is the
        one to decorate. The MLIR path emits only the plain name.
        """
        return (f"flow_export_{self.entry}", self.entry)


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


def _llvm_c_string(value: str) -> tuple[int, str]:
    raw = value.encode("utf-8") + b"\x00"
    escaped = "".join(
        chr(byte) if 32 <= byte <= 126 and byte not in {34, 92} else f"\\{byte:02X}"
        for byte in raw
    )
    return len(raw), escaped


def with_bpf_program_metadata(llvm_ir: str, program: BPFProgram) -> str:
    """Place an exported Flow entry in a BPF section and add license metadata."""
    if not program.entry or not program.section:
        raise BPFTargetError("BPF program entry and section must be non-empty")

    # Settle on one symbol before rewriting anything: if both the alias and the
    # plain definition are present, decorating both is a duplicate-entry error.
    lines = llvm_ir.splitlines()
    symbol = ""
    for candidate in program.candidate_symbols:
        needle = f"@{candidate}("
        if any(line.startswith("define ") and needle in line for line in lines):
            symbol = needle
            break

    decorated: list[str] = []
    found = False
    for line in lines:
        if symbol and line.startswith("define ") and symbol in line:
            if found:
                raise BPFTargetError(f"duplicate exported BPF entry '{program.entry}'")
            if "{" not in line:
                raise BPFTargetError(
                    f"cannot decorate multiline definition for BPF entry '{program.entry}'"
                )
            prefix, brace, suffix = line.partition("{")
            line = f'{prefix.rstrip()} section "{program.section}" {brace}{suffix}'
            found = True
        decorated.append(line)

    if not found:
        raise BPFTargetError(
            f"exported BPF entry '{program.entry}' not found; looked for "
            + " or ".join(f"@{n}" for n in program.candidate_symbols)
        )

    license_len, license_data = _llvm_c_string(program.license)
    decorated.append(
        f'@_flow_bpf_license = dso_local constant [{license_len} x i8] '
        f'c"{license_data}", section "license", align 1'
    )
    return "\n".join(decorated) + "\n"


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
    for match in re.finditer(r"\balloca\s+[^,\n]+,\s+i\d+\s+([^\s,]+)", llvm_ir):
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
    program: BPFProgram | None = None,
    clang: str | None = None,
    optimize: str = "2",
) -> Path:
    """Validate LLVM IR and emit a little-endian ELF eBPF object with clang."""
    validate_bpf_llvm_ir(llvm_ir)
    targeted_ir = with_bpf_target_header(llvm_ir)
    if program is not None:
        targeted_ir = with_bpf_program_metadata(targeted_ir, program)

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
    program: BPFProgram | None = None,
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
        return emit_bpf_object(
            llvm_ir,
            output,
            program=program,
            clang=clang,
            optimize=optimize,
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile Flow or LLVM IR to ELF eBPF")
    parser.add_argument("input", help="Input .flow or .ll file")
    parser.add_argument("-o", "--output", required=True, help="Output .o path")
    parser.add_argument("--target", default="bpfel", choices=["bpfel"])
    parser.add_argument("--entry", help="Exported Flow function to expose as a BPF program")
    parser.add_argument("--section", help="ELF BPF program section, for example socket or xdp")
    parser.add_argument("--license", default="GPL", help="BPF license string")
    parser.add_argument("-O", dest="optimize", default="2", choices=["0", "1", "2", "3"])
    args = parser.parse_args(argv)

    try:
        target_for_name(args.target)
        if bool(args.entry) != bool(args.section):
            raise BPFTargetError("--entry and --section must be supplied together")
        program = (
            BPFProgram(entry=args.entry, section=args.section, license=args.license)
            if args.entry
            else None
        )
        input_path = Path(args.input)
        if input_path.suffix == ".flow":
            compile_flow_to_bpf(
                input_path,
                args.output,
                program=program,
                optimize=args.optimize,
            )
        else:
            llvm_ir = input_path.read_text(encoding="utf-8")
            emit_bpf_object(
                llvm_ir,
                args.output,
                program=program,
                optimize=args.optimize,
            )
    except (OSError, BPFTargetError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
