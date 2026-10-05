"""Tensor operator sugar: a * b / + - rewrite to tensor_* helpers."""

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "examples" / "ml" / "autodiff" / "tensor_ops.flow"


def test_tensor_binop_emits_helpers(tmp_path):
    out = tmp_path / "tensor_ops.c"
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "flow.transpiler",
            str(SRC),
            "--c",
            "--lenient",
            "-o",
            str(out),
        ],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    c = out.read_text()
    assert "tensor_add" in c
    assert "tensor_sub" in c
    assert "tensor_mul" in c
    assert "tensor_div" in c
    assert "tensor_scale" in c
    assert "tensor_add_scalar" in c
