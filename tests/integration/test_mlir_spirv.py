"""Integration tests for MLIR GPU -> SPIR-V emit (parallel to Metal/WGSL).

Dispatch via Vulkan/MoltenVK is deferred; this suite asserts emit-only.
Linux CI is the primary environment; Darwin is skipped (Homebrew LLVM pass
differences). Metal remains the primary macOS GPU path (`./flow gpu`).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = [
    ROOT / "examples" / "gpu" / "flow_gpu_vector_add.flow",
    ROOT / "examples" / "gpu" / "flow_gpu_matrix_add.flow",
]


def _has_mlir_spirv_tools() -> bool:
    if shutil.which("mlir-opt") and shutil.which("mlir-translate"):
        return True
    # Homebrew LLVM (common on Darwin CI images that still skip this suite)
    brew = shutil.which("brew")
    if not brew:
        return False
    try:
        res = subprocess.run(
            [brew, "--prefix", "llvm"], capture_output=True, text=True
        )
        if res.returncode != 0:
            return False
        bindir = Path(res.stdout.strip()) / "bin"
        return (bindir / "mlir-opt").exists() and (bindir / "mlir-translate").exists()
    except Exception:
        return False


@pytest.mark.skipif(
    sys.platform == "darwin",
    reason="SPIR-V lowering validated on Linux CI; Homebrew LLVM is stricter on macOS",
)
@pytest.mark.parametrize("example", EXAMPLES, ids=[p.stem for p in EXAMPLES])
def test_mlir_spirv_emit(example: Path):
    if not example.exists():
        pytest.skip(f"missing fixture {example}")
    if not _has_mlir_spirv_tools():
        pytest.skip("mlir-opt/mlir-translate not available")

    out_spv = ROOT / "build" / f"{example.stem}.spv"
    if out_spv.exists():
        out_spv.unlink()

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + (
        ":" + env["PYTHONPATH"] if "PYTHONPATH" in env else ""
    )
    result = subprocess.run(
        [
            "python3",
            "-m",
            "flow.transpiler",
            str(example),
            "--mlir",
            "--mlir-gpu",
            "--emit-spirv",
            "--spirv-out",
            str(out_spv),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, (
        f"mlir spirv failed for {example.name}:\n{result.stderr}\n{result.stdout}"
    )
    assert out_spv.exists() and out_spv.stat().st_size > 0, (
        f"SPIR-V output missing or empty: {out_spv}"
    )


def test_mlir_gpu_unknown_var_fails_loud():
    """Soft '// Unknown' comments are forbidden — kernels must fail loudly."""
    from flow.mlir_gpu_codegen import MLIRGpuGenerator
    from flow.parser import Variable

    gen = MLIRGpuGenerator()
    with pytest.raises(NotImplementedError, match="unknown variable"):
        gen.generate_expression(Variable("no_such_gpu_var"))
