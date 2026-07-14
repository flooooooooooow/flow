"""Integration test for MLIR GPU -> SPIR-V lowering."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FLOW = ROOT / "flow"
EXAMPLE = ROOT / "examples" / "gpu" / "flow_gpu_vector_add.flow"


def _has_mlir_spirv_tools() -> bool:
    return shutil.which("mlir-opt") is not None and shutil.which("mlir-translate") is not None


@pytest.mark.skipif(
    sys.platform == "darwin",
    reason="SPIR-V lowering validated on Linux CI; Homebrew LLVM is stricter on macOS",
)
def test_mlir_spirv_vector_add():
    if not _has_mlir_spirv_tools():
        pytest.skip("mlir-opt/mlir-translate not available")
    out_spv = ROOT / "build" / "flow_gpu_vector_add.spv"
    if out_spv.exists():
        out_spv.unlink()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + (":" + env["PYTHONPATH"] if "PYTHONPATH" in env else "")
    result = subprocess.run(
        ["python3", "-m", "flow.transpiler", str(EXAMPLE), "--mlir", "--mlir-gpu", "--emit-spirv"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"mlir spirv failed: {result.stderr}\n{result.stdout}"
    assert out_spv.exists(), "SPIR-V output not generated"
