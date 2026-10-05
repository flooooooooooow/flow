"""Integration test for `flow gpu` Metal codegen."""

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLOW = ROOT / "flow"
BUILD_GPU = ROOT / "build" / "gpu"


def _run_flow_gpu(path: Path):
    result = subprocess.run(
        [str(FLOW), "gpu", str(path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"flow gpu failed: {result.stderr}\n{result.stdout}"


def _cleanup(patterns):
    if not BUILD_GPU.exists():
        return
    for p in patterns:
        for f in BUILD_GPU.glob(p):
            try:
                f.unlink()
            except FileNotFoundError:
                pass


def test_flow_gpu_codegen_vector_add():
    _cleanup(["vector_add*.metal", "vector_add*_host.m", "vector_scale*.metal", "vector_scale*_host.m", "vector_saxpy*.metal", "vector_saxpy*_host.m"])
    _run_flow_gpu(ROOT / "examples" / "gpu" / "vector_add_gpu.flow")

    assert (BUILD_GPU / "vector_add.metal").exists()
    assert (BUILD_GPU / "vector_scale.metal").exists()
    assert (BUILD_GPU / "vector_saxpy.metal").exists()


def test_flow_gpu_codegen_vector_add_tutorial():
    _cleanup(["vec_add_gpu*.metal", "vec_add_gpu*_host.m"])
    _run_flow_gpu(ROOT / "examples" / "gpu" / "flow_gpu_vector_add.flow")
    assert (BUILD_GPU / "vec_add_gpu.metal").exists()


def test_flow_gpu_codegen_gradients():
    _cleanup(["gpu_mse_grad*.metal", "gpu_relu_grad*.metal", "gpu_sigmoid_grad*.metal", "gpu_scale_grad*.metal"])
    _run_flow_gpu(ROOT / "lib" / "stdlib" / "gpu_gradients.flow")
    assert (BUILD_GPU / "gpu_mse_grad.metal").exists()
    assert (BUILD_GPU / "gpu_relu_grad.metal").exists()
    assert (BUILD_GPU / "gpu_sigmoid_grad.metal").exists()
