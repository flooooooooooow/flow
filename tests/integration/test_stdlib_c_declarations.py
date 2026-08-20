"""Importing a stdlib module brings the C declarations its code needs (#590).

A block that passes Flow parsing, type checking and codegen but fails at
clang is a backend gap, not stale Flow syntax. `import "stdlib/math.flow"`
followed by `sin(x)` emitted a call to `sin_f32` that nothing declared.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _build(source: str) -> tuple[str, str]:
    """Transpile and compile. Returns (generated C, clang stderr)."""
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    with tempfile.TemporaryDirectory() as td:
        src, c = Path(td) / "p.flow", Path(td) / "p.c"
        src.write_text(source)
        transpile = subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(src), "--c", "-o", str(c)],
            cwd=ROOT, env=env, capture_output=True, text=True,
        )
        assert transpile.returncode == 0, transpile.stderr + transpile.stdout
        generated = c.read_text()
        build = subprocess.run(
            ["clang", "-fsyntax-only", str(c)], capture_output=True, text=True
        )
        return generated, build.stderr


MATH = """
import "stdlib/math.flow"

function main() -> i32 {
    let x = sin(3.14159 / 2.0)
    printf("sin(pi/2) = %f\\n", x)
    return 0
}
"""


def test_a_math_call_uses_the_libm_name():
    """`sin` is never emitted, so the call has to be `sin`, not `sin_f32`."""
    generated, errors = _build(MATH)
    assert "sin_f32(" not in generated, generated[generated.find("sin_f32") - 80:][:160]
    assert "= sin(" in generated
    assert errors.strip() == "", errors


def test_the_math_example_runs_and_is_correct():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    with tempfile.TemporaryDirectory() as td:
        src, c, exe = Path(td) / "p.flow", Path(td) / "p.c", Path(td) / "p"
        src.write_text(MATH)
        subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(src), "--c", "-o", str(c)],
            cwd=ROOT, env=env, capture_output=True, text=True, check=True,
        )
        assert subprocess.run(
            ["clang", "-w", "-O0", "-o", str(exe), str(c), "-lm"],
            capture_output=True, text=True,
        ).returncode == 0
        out = subprocess.run([str(exe)], capture_output=True, text=True).stdout
    assert "sin(pi/2) = 1.000000" in out, out


def test_a_header_is_included_once():
    """Several externs mapping to one header used to emit it repeatedly."""
    generated, _ = _build("""
extern {
    function usleep(usec: i32) -> i32
    function sleep(seconds: i32) -> i32
    function getcwd(buf: ptr<i8>, size: i32) -> ptr<i8>
}

function main() -> i32 {
    return 0
}
""")
    assert generated.count("#include <unistd.h>") == 1, generated.count("#include <unistd.h>")
