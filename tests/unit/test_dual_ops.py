"""Dual operator sugar: a * b / + - rewrite to Dual overloads."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "examples" / "ml" / "autodiff" / "dual_ops.flow"


def test_dual_binop_emits_overloads(tmp_path):
    out = tmp_path / "dual_ops.c"
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
        env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(ROOT / "src")},
        check=True,
        capture_output=True,
        text=True,
    )
    c = out.read_text()
    assert "mul_Dual_Dual" in c
    assert "add_Dual_f32" in c or "mul_f32_Dual" in c
    assert "neg_Dual" in c
    assert "add_Dual_Dual" in c or "add_Dual_f32" in c
    assert "add(neg_Dual" not in c
