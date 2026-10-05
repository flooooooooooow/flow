import subprocess
from pathlib import Path

import pytest

from flow.mlir_spirv import MLIRSPIRVCompiler


def test_spirv_to_msl_uses_spirv_cross(tmp_path: Path, monkeypatch):
    spirv_cross = tmp_path / "spirv-cross"
    spirv_cross.write_text("")
    source = tmp_path / "kernel.spv"
    source.write_bytes(b"\x03\x02\x23\x07")
    output = tmp_path / "kernel.metal"
    calls = []

    def fake_run(cmd, capture_output=False, text=False, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout="#include <metal_stdlib>\nkernel void main0() {}\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    compiler = MLIRSPIRVCompiler(
        mlir_opt="mlir-opt",
        mlir_translate="mlir-translate",
        spirv_cross=str(spirv_cross),
    )
    compiler.compile_spirv_to_msl(
        str(source),
        str(output),
        extra_args=["--msl-version", "23000"],
    )

    assert calls == [
        [
            str(spirv_cross),
            str(source),
            "--msl",
            "--msl-version",
            "23000",
        ]
    ]
    assert "metal_stdlib" in output.read_text()


def test_spirv_to_msl_rejects_empty_output(tmp_path: Path, monkeypatch):
    spirv_cross = tmp_path / "spirv-cross"
    spirv_cross.write_text("")
    source = tmp_path / "kernel.spv"
    source.write_bytes(b"spv")

    def fake_run(cmd, capture_output=False, text=False, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    compiler = MLIRSPIRVCompiler(
        mlir_opt="mlir-opt",
        mlir_translate="mlir-translate",
        spirv_cross=str(spirv_cross),
    )

    with pytest.raises(RuntimeError, match="empty MSL output"):
        compiler.compile_spirv_to_msl(str(source), str(tmp_path / "kernel.metal"))


def test_mlir_to_msl_routes_through_spirv(tmp_path: Path, monkeypatch):
    compiler = MLIRSPIRVCompiler(
        mlir_opt="mlir-opt",
        mlir_translate="mlir-translate",
        spirv_cross="spirv-cross",
    )
    seen = {}

    def fake_spirv(mlir_code, output_path, extra_opt_args=None):
        seen["mlir"] = mlir_code
        seen["opt"] = extra_opt_args
        Path(output_path).write_bytes(b"spv")

    def fake_msl(spirv_path, output_path, extra_args=None):
        seen["spirv"] = Path(spirv_path).read_bytes()
        seen["cross"] = extra_args
        Path(output_path).write_text("kernel void main0() {}\n")

    monkeypatch.setattr(compiler, "compile_mlir_to_spirv", fake_spirv)
    monkeypatch.setattr(compiler, "compile_spirv_to_msl", fake_msl)

    output = tmp_path / "kernel.metal"
    compiler.compile_mlir_to_msl(
        "module {}",
        str(output),
        extra_opt_args=["--canonicalize"],
        spirv_cross_args=["--msl-version", "23000"],
    )

    assert seen == {
        "mlir": "module {}",
        "opt": ["--canonicalize"],
        "spirv": b"spv",
        "cross": ["--msl-version", "23000"],
    }
    assert output.exists()


def test_msl_to_metallib_uses_xcrun(tmp_path: Path, monkeypatch):
    xcrun = tmp_path / "xcrun"
    xcrun.write_text("")
    source = tmp_path / "kernel.metal"
    source.write_text("kernel void main0() {}\n")
    output = tmp_path / "kernel.metallib"
    calls = []

    def fake_run(cmd, capture_output=False, text=False, **kwargs):
        calls.append(cmd)
        if "metallib" in cmd:
            Path(cmd[-1]).write_bytes(b"metallib")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    # Pin every tool. Left unset, the constructor searches for spirv-cross,
    # and on a machine with brew installed that search shells out through the
    # patched subprocess.run and lands in calls[0].
    compiler = MLIRSPIRVCompiler(
        mlir_opt="mlir-opt",
        mlir_translate="mlir-translate",
        spirv_cross="spirv-cross",
        xcrun=str(xcrun),
    )
    compiler.compile_msl_to_metallib(str(source), str(output), sdk="macosx")

    assert calls[0][0:4] == [str(xcrun), "-sdk", "macosx", "metal"]
    assert calls[1][0:4] == [str(xcrun), "-sdk", "macosx", "metallib"]
    assert output.read_bytes() == b"metallib"
