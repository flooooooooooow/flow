from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "module_collision" / "main.flow"


def test_private_same_name_functions_in_distinct_modules_compile_and_run(tmp_path: Path) -> None:
    output = tmp_path / "module_collision"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")

    generated = tmp_path / "module_collision.c"
    transpile = subprocess.run(
        [
            sys.executable,
            "-m",
            "flow.transpiler",
            str(FIXTURE),
            "--c",
            "-o",
            str(generated),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert transpile.returncode == 0, transpile.stderr + transpile.stdout

    c_source = generated.read_text()
    assert "_same_i32" in c_source
    assert "_same_f32" in c_source

    compile_result = subprocess.run(
        ["clang", str(generated), "-lm", "-o", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert compile_result.returncode == 0, compile_result.stderr + compile_result.stdout

    run_result = subprocess.run(
        [str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert run_result.returncode == 42, run_result.stderr + run_result.stdout
