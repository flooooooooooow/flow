"""`defer` runs after the return value is read, and on every return (#594).

Two defects, both found by running the documentation examples rather than
only compiling them. `docs/book/10-memory-and-lifetimes.md` exited 216 where
it should have exited 0.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _build_and_run(source: str) -> tuple[str, int, str]:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    with tempfile.TemporaryDirectory() as td:
        src, c, exe = Path(td) / "p.flow", Path(td) / "p.c", Path(td) / "p"
        src.write_text(source)
        transpile = subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(src), "--c", "-o", str(c)],
            cwd=ROOT, env=env, capture_output=True, text=True,
        )
        assert transpile.returncode == 0, transpile.stderr + transpile.stdout
        generated = c.read_text()
        build = subprocess.run(
            ["clang", "-O0", "-o", str(exe), str(c), "-lm"], capture_output=True, text=True
        )
        assert build.returncode == 0, build.stderr
        run = subprocess.run([str(exe)], capture_output=True, text=True)
        return run.stdout, run.returncode, generated


HEAP = """
extern {
    function calloc(count: i64, size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}
"""


def test_the_return_value_is_read_before_the_defer_runs():
    """`free(data); return data[3] - 40;` read freed memory, and said 216."""
    _, code, generated = _build_and_run(HEAP + """
function main() -> i32 {
    let data: ptr<i32> = calloc(4, 4)
    if data == null { return 1 }
    defer free(data)

    for i in 0 to 4 {
        data[i] = (i + 1) * 10
    }
    return data[3] - 40
}
""")
    assert code == 0, f"exit {code}: the return read freed memory"
    body = generated[generated.index("int32_t main("):]
    assert body.index("free(data)") > body.index("data[3] - 40"), body


def test_a_return_inside_a_nested_block_still_runs_the_defer():
    """Only the enclosing block's defers were consulted, so this leaked."""
    out, code, generated = _build_and_run("""
extern { function printf(fmt: string, val: i32) -> i32 }

function f(n: i32) -> i32 {
    defer printf("cleanup\\n", 0)
    if n > 0 {
        printf("positive\\n", 0)
        return 1
    }
    return 0
}

function main() -> i32 {
    return f(1) - 1
}
""")
    assert code == 0
    assert out.splitlines() == ["positive", "cleanup"], out


def test_defers_run_innermost_first_across_nested_blocks():
    out, code, _ = _build_and_run("""
extern { function printf(fmt: string, val: i32) -> i32 }

function f() -> i32 {
    defer printf("outer\\n", 0)
    if true {
        defer printf("inner\\n", 0)
        return 0
    }
    return 1
}

function main() -> i32 {
    return f()
}
""")
    assert code == 0
    assert out.splitlines() == ["inner", "outer"], out


def test_falling_off_the_end_still_runs_defers_once():
    out, code, _ = _build_and_run("""
extern { function printf(fmt: string, val: i32) -> i32 }

function main() -> i32 {
    defer printf("a\\n", 0)
    defer printf("b\\n", 0)
    printf("body\\n", 0)
    return 0
}
""")
    assert code == 0
    assert out.splitlines() == ["body", "b", "a"], out
