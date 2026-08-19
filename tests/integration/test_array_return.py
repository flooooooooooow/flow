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


NESTED = """
function consume(rows: array<array<i32, 3>, 4>) -> i32 {
    return rows[0][0] + rows[3][2]
}

function build(root: i32) -> array<array<i32, 3>, 4> {
    return [[root, root + 1, root + 2], [root + 3, root + 4, root + 5],
            [root + 6, root + 7, root + 8], [root + 9, root + 10, root + 11]]
}

function row_of(base: i32) -> array<i32, 3> {
    return [base, base + 1, base + 2]
}

function from_rows(root: i32) -> array<array<i32, 3>, 4> {
    let a: array<i32, 3> = row_of(root)
    let b: array<i32, 3> = row_of(root + 10)
    return [a, b, a, b]
}

function main() -> i32 {
    let rows: array<array<i32, 3>, 4> = build(10)
    printf("built %d %d %d\\n", rows[0][0], rows[1][1], consume(rows))
    let joined: array<array<i32, 3>, 4> = from_rows(1)
    printf("joined %d %d %d\\n", joined[0][0], joined[1][0], joined[3][2])
    return 0
}
"""


def test_nested_arrays_are_rows_not_pointers():
    """`array<array<T, N>, M>` used to be an array of pointers (#575)."""
    stdout, warnings = _build_and_run(NESTED)
    lines = dict(line.split(" ", 1) for line in stdout.strip().splitlines())
    # rows[0][0]=10, rows[1][1]=14, consume = rows[0][0] + rows[3][2] = 10 + 21
    assert lines["built"] == "10 14 31"
    # a = [1,2,3], b = [11,12,13]; joined = [a, b, a, b]
    assert lines["joined"] == "1 11 13"
    assert "return-stack-address" not in warnings, warnings


def test_a_stdlib_progression_returns_real_chords():
    stdout, warnings = _build_and_run("""
import "stdlib/audio/scales.flow"

function main() -> i32 {
    let p: array<array<i32, 3>, 4> = progression_pop(note_C(4))
    printf("pop %d %d %d\\n", p[0][0], p[0][1], p[0][2])
    return 0
}
""")
    # C major triad on note_C(4) = 48
    assert "pop 48 52 55" in stdout
    assert "return-stack-address" not in warnings, warnings


def test_a_sized_array_named_after_a_c_keyword_compiles():
    """Use sites sanitized the name; the declaration did not."""
    stdout, _ = _build_and_run("""
function main() -> i32 {
    let inline: array<array<i32, 2>, 3> = [[1, 2], [3, 4], [5, 6]]
    printf("kw %d %d %d\\n", inline[0][0], inline[1][1], inline[2][0])
    return 0
}
""")
    assert "kw 1 4 5" in stdout
