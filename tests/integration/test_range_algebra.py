"""Compiled behaviour of `sum(range | range)` and `sum(range & range)`.

The unit tests check the folded arithmetic against Python's own sets. These
check the generated C: that the helper agrees with a brute-force loop over the
same elements, and that each bound expression is evaluated once.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run(source: str) -> str:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "p.flow"
        c = Path(td) / "p.c"
        exe = Path(td) / "p"
        src.write_text(source)
        transpile = subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(src), "--c", "-o", str(c)],
            cwd=ROOT, env=env, capture_output=True, text=True,
        )
        assert transpile.returncode == 0, transpile.stderr + transpile.stdout
        build = subprocess.run(
            ["clang", "-O1", "-o", str(exe), str(c), "-lm"],
            capture_output=True, text=True,
        )
        assert build.returncode == 0, build.stderr
        return subprocess.run([str(exe)], capture_output=True, text=True).stdout


BRUTE = """
function in_range(x: i32, start: i32, end: i32, stride: i32) -> i32 {
    let mut z: i32 = start
    while (stride > 0 && z < end) || (stride < 0 && z > end) {
        if z == x {
            return 1
        }
        z = z + stride
    }
    return 0
}

function brute_union(sa: i32, ea: i32, pa: i32, sb: i32, eb: i32, pb: i32) -> i32 {
    let mut total: i32 = 0
    let mut x: i32 = sa
    while (pa > 0 && x < ea) || (pa < 0 && x > ea) {
        total = total + x
        x = x + pa
    }
    let mut y: i32 = sb
    while (pb > 0 && y < eb) || (pb < 0 && y > eb) {
        if in_range(y, sa, ea, pa) == 0 {
            total = total + y
        }
        y = y + pb
    }
    return total
}

function brute_isect(sa: i32, ea: i32, pa: i32, sb: i32, eb: i32, pb: i32) -> i32 {
    let mut total: i32 = 0
    let mut y: i32 = sb
    while (pb > 0 && y < eb) || (pb < 0 && y > eb) {
        if in_range(y, sa, ea, pa) == 1 {
            total = total + y
        }
        y = y + pb
    }
    return total
}
"""


def test_compiled_algebra_matches_a_brute_force_loop():
    """Sweep mixed-sign strides and offset starts against the actual element sets."""
    out = _run(BRUTE + """
function main() -> i32 {
    let mut bad: i32 = 0
    let mut i: i32 = 0
    while i < 500 {
        let sa: i32 = (i * 7) % 23 - 11
        let sb: i32 = (i * 13) % 19 - 9
        let pa: i32 = ((i * 5) % 13) - 6
        let pb: i32 = ((i * 3) % 11) - 5
        if pa != 0 && pb != 0 {
            let ea: i32 = sa + (i % 31) - 15
            let eb: i32 = sb + (i % 27) - 13
            if sum(sa..ea step pa | sb..eb step pb) != brute_union(sa, ea, pa, sb, eb, pb) {
                bad = bad + 1
            }
            if sum(sa..ea step pa & sb..eb step pb) != brute_isect(sa, ea, pa, sb, eb, pb) {
                bad = bad + 1
            }
        }
        i = i + 1
    }
    printf("%d\\n", bad)
    return 0
}
""")
    assert out.strip() == "0"


def test_each_bound_is_evaluated_exactly_once():
    """Six bounds, six calls. Inlining inclusion-exclusion would repeat them."""
    out = _run("""
let mut calls: i32 = 0

function bound(value: i32) -> i32 {
    calls = calls + 1
    return value
}

function main() -> i32 {
    let total: i32 = sum(
        bound(0)..bound(1000) step bound(3) | bound(0)..bound(1000) step bound(5)
    )
    printf("%d %d\\n", total, calls)
    return 0
}
""")
    assert out.split() == ["233168", "6"]


def test_literal_algebra_leaves_no_helper_behind():
    """A fully literal expression folds, so no helper is emitted at all."""
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "p.flow"
        c = Path(td) / "p.c"
        src.write_text(
            "function main() -> i32 {\n"
            "    printf(\"%d\\n\", sum(0..1000 step 3 | 0..1000 step 5))\n"
            "    return 0\n"
            "}\n"
        )
        assert subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(src), "--c", "-o", str(c)],
            cwd=ROOT, env=env, capture_output=True, text=True,
        ).returncode == 0
        generated = c.read_text()
    assert "233168" in generated
    assert "__flow_sum_range_union" not in generated
    assert "__flow_range_modinv" not in generated
