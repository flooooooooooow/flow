"""Integration test for MLIR GPU -> SPIR-V lowering."""

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLOW = ROOT / "flow"
EXAMPLE = ROOT / "examples" / "gpu" / "flow_gpu_vector_add.flow"


def _has_mlir_spirv_tools() -> bool:
    return shutil.which("mlir-opt") is not None and shutil.which("mlir-translate") is not None


def test_mlir_spirv_vector_add():
    if not _has_mlir_spirv_tools():
        return  # Skip if toolchain not available
    out_spv = ROOT / "build" / "flow_gpu_vector_add.spv"
    if out_spv.exists():
        out_spv.unlink()
    result = subprocess.run(
        [str(FLOW), "mlir", "--mlir-gpu", "--emit-spirv", str(EXAMPLE)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"mlir spirv failed: {result.stderr}\n{result.stdout}"
    assert out_spv.exists(), "SPIR-V output not generated"
