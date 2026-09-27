"""A returned `array<T, N>` must outlive the call that produced it (#573).

`-> array<T, N>` used to lower to `T*` over automatic storage, so the caller
read a frame that was already gone and got garbage with no diagnostic. clang
had been saying so on every build: "address of stack memory associated with
compound literal ... returned".

The value checks moved to tests/lang/ (test_array_return_values.flow,
test_array_repeat.flow, test_stdlib_scales.flow). What stays here is the
clang diagnostic on the Python host's generated C.
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


def test_no_stack_address_is_returned():
    """clang's own diagnostic is the ground truth for this defect.

    The returned values themselves are checked in
    tests/lang/test_array_return_values.flow, test_array_repeat.flow and
    test_stdlib_scales.flow.
    """
    for source in (SOURCE, NESTED):
        _, warnings = _build_and_run(source)
        assert "return-stack-address" not in warnings, warnings
