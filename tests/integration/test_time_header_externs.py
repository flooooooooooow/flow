from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "time_header_externs.flow"


def test_time_header_owns_localtime_and_strftime_prototypes(tmp_path: Path) -> None:
    generated = tmp_path / "time_header_externs.c"
    obj = tmp_path / "time_header_externs.o"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")

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

    source = generated.read_text()
    assert "#include <time.h>" in source

    compile_result = subprocess.run(
        ["clang", "-Werror", "-c", str(generated), "-o", str(obj)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert compile_result.returncode == 0, compile_result.stderr + compile_result.stdout
