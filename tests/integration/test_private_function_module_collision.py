from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from flow.module_resolver import resolve_modules
from flow.monomorphize import monomorphize
from flow.parser import FunctionDecl


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "module_collision" / "main.flow"


def _same_signatures(declarations) -> list[tuple[str, ...]]:
    return [
        tuple(param.type.name for param in decl.parameters)
        for decl in declarations
        if isinstance(decl, FunctionDecl) and decl.name == "_same"
    ]


def test_private_same_name_functions_in_distinct_modules_compile_and_run(tmp_path: Path) -> None:
    resolved = resolve_modules(str(FIXTURE))
    assert sorted(_same_signatures(resolved)) == [("f32",), ("i32",)]

    rewritten = monomorphize(resolved)
    assert sorted(_same_signatures(rewritten)) == [("f32",), ("i32",)]

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
