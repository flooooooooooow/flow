"""`x as T` inside a string concatenation keeps its cast type (#577).

`_infer_expr_type` had no CastExpression branch, so a cast fell through to
the default and `_is_string_expr` said no. `"a" + (buf as string)` then went
through `_gen_stringify_expr`, which printed the buffer *pointer* with "%d"
into a 64-byte stack buffer:

    snprintf(_flow_strval[64], 64, "%d", ((char*)(ov)))

The result was 10 digits of pointer where 5000 characters should have been.
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
        src, c, exe = Path(td) / "p.flow", Path(td) / "p.c", Path(td) / "p"
        src.write_text(source)
        transpile = subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(src), "--c", "-o", str(c)],
            cwd=ROOT, env=env, capture_output=True, text=True,
        )
        assert transpile.returncode == 0, transpile.stderr + transpile.stdout
        build = subprocess.run(
            ["clang", "-O1", "-o", str(exe), str(c), "-lm"], capture_output=True, text=True
        )
        assert build.returncode == 0, build.stderr
        run = subprocess.run([str(exe)], capture_output=True, text=True)
        assert run.returncode == 0, run.stderr
        return run.stdout


def test_array_cast_to_string_is_not_printed_as_a_pointer():
    """The issue's own repro: 5000 'p' plus 29 characters of surrounding SQL."""
    out = _run("""
extern {
    function printf(fmt: string, val: i64) -> i32
    function strlen(s: string) -> i64
}

function main() -> i32 {
    let mut ov: array<u8, 6000> = []
    let mut oi: i32 = 0
    while oi < 5000 {
        ov[oi] = 112
        oi = oi + 1
    }
    ov[5000] = 0
    let sql: string = "INSERT INTO t VALUES (1, '" + (ov as string) + "');"
    printf("len=%lld\\n", strlen(sql))
    return 0
}
""")
    assert "len=5029" in out, out


def test_the_cast_content_survives_not_just_the_length():
    out = _run("""
function main() -> i32 {
    let mut buf: array<u8, 8> = []
    buf[0] = 104
    buf[1] = 105
    buf[2] = 0
    println("cast=" + (buf as string) + "!")
    return 0
}
""")
    assert "cast=hi!" in out, out


def test_numeric_casts_still_format_as_numbers():
    """A cast to a number must keep going through the stringify path."""
    out = _run("""
function main() -> i32 {
    let x: f64 = 3.75
    let n: i32 = 42
    println("int=" + (n as i64))
    println("trunc=" + (x as i32))
    return 0
}
""")
    assert "int=42" in out, out
    assert "trunc=3" in out, out


def test_the_documented_workaround_still_works():
    """Binding the cast to a variable first was the workaround in #577."""
    out = _run("""
extern { function strlen(s: string) -> i64 }

function main() -> i32 {
    let mut ov: array<u8, 64> = []
    ov[0] = 97
    ov[1] = 0
    let ovs: string = ov as string
    println("via var=" + ovs + "!")
    return 0
}
""")
    assert "via var=a!" in out, out


def test_concatenating_a_wide_numeric_type_is_still_a_string():
    """The wider bug behind #577: the concat inferred a *numeric* result.

    `_infer_expr_type` had no string case for `+`, so an i64 or f64 operand
    was claimed by the numeric promotion rules and the whole concatenation
    was formatted as that number. `"i64=" + v` printed the concatenated
    pointer with "%lld"; `"f64=" + f` printed 0.000000. It appeared to work
    only for operand types the rules did not recognise, which fell through to
    `left or right` and happened to land on the string.
    """
    out = _run("""
function main() -> i32 {
    let v: i64 = 42
    let f: f64 = 1.5
    let u: u32 = 7
    println("i64=" + v)
    println("f64=" + f)
    println("u32=" + u)
    return 0
}
""")
    assert "i64=42" in out, out
    assert "f64=1.5" in out, out
    assert "u32=7" in out, out


def test_arithmetic_without_a_string_still_promotes():
    out = _run("""
function main() -> i32 {
    let a: i32 = 3
    let b: i64 = 4
    let c: f64 = 0.5
    println((a + b) * 2)
    println(c + 1.0)
    return 0
}
""")
    assert "14" in out, out
    assert "1.5" in out, out
