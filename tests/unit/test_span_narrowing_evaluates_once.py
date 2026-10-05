"""A span borrow evaluates its source expression exactly once.

Narrowing `span<mut T>` to `span<T>` reads the source span's pointer and its
length, and the initializer expression was inlined into both, so any side
effect in it happened twice. See issue #623.

The mut-to-mut case is checked alongside the narrowing one: it was always
correct, and it is what shows the fix did not simply move the problem.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(
    not shutil.which("cc"), reason="needs a C compiler"
)

SOURCE = """
extern {
    function malloc(size: i64) -> ptr<void>
    function printf(fmt: string, a: f64) -> i32
}

function make_mut(n: i32, calls: ptr<i32>) -> span<mut f64> {
    calls[0] = calls[0] + 1
    let raw: ptr<f64> = malloc(n as i64 * 8)
    return raw[0..n]
}

function main() -> i32 {
    let c: ptr<i32> = malloc(4)
    c[0] = 0
    let a: span<mut f64> = make_mut(3, c)
    printf("%.0f\\n", c[0] as f64)
    c[0] = 0
    let d: span<f64> = make_mut(3, c)
    printf("%.0f\\n", c[0] as f64)
    c[0] = 0
    let mut e: span<f64> = make_mut(3, c)
    e = make_mut(3, c)
    printf("%.0f\\n", c[0] as f64)
    return 0
}
"""


def test_each_borrow_calls_its_initializer_once(tmp_path):
    src = tmp_path / "d.flow"
    src.write_text(textwrap.dedent(SOURCE))
    run = subprocess.run(
        ["./flow", "run", str(src)],
        cwd=ROOT, capture_output=True, text=True,
        env={**os.environ, "FLOW_HOST": "python"},
    )
    counts = [ln for ln in run.stdout.splitlines() if ln.strip().isdigit()]
    # mut <- mut, then const <- mut (the narrowing), then a reassignment
    # whose two calls are counted together.
    assert counts == ["1", "1", "2"], run.stdout + run.stderr
