"""A returned `array<T, N>` must outlive the call that produced it (#573).

`-> array<T, N>` used to lower to `T*` over automatic storage, so the caller
read a frame that was already gone and got garbage with no diagnostic. clang
had been saying so on every build: "address of stack memory associated with
compound literal ... returned".

These tests read the values back. The one test that existed before,
tests/arrays/test_array_return.flow, returned an unsized `array<f32>` (heap
allocated, so safe) and only printed "Test complete", which is why the defect
survived.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _build_and_run(source: str) -> tuple[str, str]:
    """Compile and run, returning (stdout, clang stderr)."""
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    with tempfile.TemporaryDirectory() as td:
        src, c, exe = Path(td) / "p.flow", Path(td) / "p.c", Path(td) / "p"
        src.write_text(source)
        transpile = subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(src), "--c", "-o", str(c)],
            cwd=ROOT, env=env, capture_output=True, text=True,
        )
        assert transpile.returncode == 0, transpile.stderr + transpile.stdout
        build = subprocess.run(
            ["clang", "-O1", "-Wreturn-stack-address", "-o", str(exe), str(c), "-lm"],
            capture_output=True, text=True,
        )
        assert build.returncode == 0, build.stderr
        run = subprocess.run([str(exe)], capture_output=True, text=True)
        assert run.returncode == 0, f"exit {run.returncode}: {run.stderr}"
        return run.stdout, build.stderr


SOURCE = """
function from_literal(root: i32) -> array<i32, 3> {
    return [root, root + 4, root + 7]
}

function from_local(root: i32) -> array<i32, 3> {
    let built: array<i32, 3> = [root, root + 4, root + 7]
    return built
}

function total(xs: array<i32, 3>) -> i32 {
    return xs[0] + xs[1] + xs[2]
}

function main() -> i32 {
    let a: array<i32, 3> = from_literal(60)
    printf("literal %d %d %d\\n", a[0], a[1], a[2])
    let b: array<i32, 3> = from_local(60)
    printf("local %d %d %d\\n", b[0], b[1], b[2])
    printf("indexed %d\\n", from_literal(60)[1])
    printf("passed %d\\n", total(from_literal(60)))
    return 0
}
"""


def test_returned_array_values_survive_the_call():
    stdout, _ = _build_and_run(SOURCE)
    lines = dict(line.split(" ", 1) for line in stdout.strip().splitlines())
    assert lines["literal"] == "60 64 67"
    assert lines["local"] == "60 64 67"
    assert lines["indexed"] == "64"
    assert lines["passed"] == "191"


def test_no_stack_address_is_returned():
    """clang's own diagnostic is the ground truth for this defect."""
    _, warnings = _build_and_run(SOURCE)
    assert "return-stack-address" not in warnings, warnings


def test_a_stdlib_scale_returns_its_actual_notes():
    """Every function in audio/scales.flow returns a fixed-size array."""
    stdout, warnings = _build_and_run("""
import "stdlib/audio/scales.flow"

function main() -> i32 {
    let s: array<i32, 7> = scale_major(48)
    printf("major %d %d %d %d %d %d %d\\n",
           s[0], s[1], s[2], s[3], s[4], s[5], s[6])
    let c: array<i32, 3> = chord_major(48)
    printf("triad %d %d %d\\n", c[0], c[1], c[2])
    return 0
}
""")
    assert "major 48 50 52 53 55 57 59" in stdout
    assert "triad 48 52 55" in stdout
