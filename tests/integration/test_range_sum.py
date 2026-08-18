from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from pathlib import Path

import pytest

from flow.parser import FlowSyntaxError, Literal, ReturnStatement, parse_flow_code


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "range_sum.flow"


def _function_body(source: str, signature_fragment: str) -> str:
    start = source.index(signature_fragment)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace : index + 1]
    raise AssertionError(f"unterminated generated function: {signature_fragment}")


def test_literal_sum_range_folds_during_parsing() -> None:
    declarations = parse_flow_code(
        """
function folded() -> i32 {
    return sum(0..1000 step 3)
}
"""
    )
    return_statement = declarations[0].body.statements[0]
    assert isinstance(return_statement, ReturnStatement)
    assert isinstance(return_statement.value, Literal)
    assert return_statement.value.value == "166833"


def test_sum_range_compiles_to_closed_form_and_preserves_results(tmp_path: Path) -> None:
    generated = tmp_path / "range_sum.c"
    library = tmp_path / "range_sum.so"
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

    c_source = generated.read_text()
    runtime_body = _function_body(c_source, "sum_runtime_i32_i32_i32")
    assert "for (" not in runtime_body
    assert "while (" not in runtime_body

    compile_result = subprocess.run(
        ["clang", "-shared", "-fPIC", "-O2", str(generated), "-lm", "-o", str(library)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert compile_result.returncode == 0, compile_result.stderr + compile_result.stdout

    lib = ctypes.CDLL(str(library))
    expected_zero_arg = {
        "sum_default": 45,
        "sum_step": 18,
        "sum_offset": 21,
        "sum_descending": 22,
        "sum_empty_direction": 0,
    }
    for name, expected in expected_zero_arg.items():
        fn = getattr(lib, name)
        fn.argtypes = []
        fn.restype = ctypes.c_int32
        assert fn() == expected

    runtime = lib.sum_runtime_i32_i32_i32
    runtime.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    runtime.restype = ctypes.c_int32
    assert runtime(0, 1000, 3) == 166833
    assert runtime(5, 10, 2) == 21
    assert runtime(10, 0, -3) == 22
    assert runtime(0, 10, -1) == 0
    assert runtime(10, 0, 1) == 0
    assert runtime(0, 10, 0) == 0


def test_sum_range_rejects_literal_zero_step() -> None:
    with pytest.raises(FlowSyntaxError, match="step must not be zero"):
        parse_flow_code(
            """
function bad() -> i32 {
    return sum(0..10 step 0)
}
"""
        )


def _run(source: str) -> str:
    """Compile and run, returning stdout."""
    import subprocess, sys, tempfile, os
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    env = {**os.environ, "PYTHONPATH": str(root / "src")}
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "p.flow"; c = Path(td) / "p.c"; exe = Path(td) / "p"
        src.write_text(source)
        assert subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(src), "--c", "-o", str(c)],
            cwd=root, env=env, capture_output=True, text=True).returncode == 0
        assert subprocess.run(["clang", "-O0", "-o", str(exe), str(c), "-lm"],
                              capture_output=True, text=True).returncode == 0
        return subprocess.run([str(exe)], capture_output=True, text=True).stdout


def test_runtime_sum_does_not_overflow_where_a_loop_does_not():
    """The closed form must not form twice the answer on the way there.

    n * (2a + (n-1)d) / 2 builds an intermediate of exactly 2*sum, so it wrapped
    once the real answer passed 2^30 even though i32 reaches 2^31-1. This range
    sums to 1500013378, which fits comfortably; the doubled value, 3000026756,
    does not.
    """
    out = _run("""
function loop_sum(limit: i32, stride: i32) -> i32 {
    let mut total: i32 = 0
    let mut n: i32 = 0
    while n < limit {
        total = total + n
        n = n + stride
    }
    return total
}

function closed_sum(limit: i32, stride: i32) -> i32 {
    return sum(0..limit step stride)
}

function main() -> i32 {
    printf("%d %d\\n", closed_sum(54773, 1), loop_sum(54773, 1))
    return 0
}
""")
    closed, looped = out.split()
    assert closed == looped == "1500013378"


def test_each_bound_is_evaluated_exactly_once():
    """A `for` loop over the same range evaluates each bound once.

    While the sum was inlined at the call site the bounds appeared many times
    in the generated expression, so a bound with a side effect ran 4, 3 and 8
    times respectively.
    """
    out = _run("""
let mut start_calls: i32 = 0
let mut end_calls: i32 = 0
let mut step_calls: i32 = 0

function a_start(v: i32) -> i32 { start_calls = start_calls + 1 return v }
function an_end(v: i32) -> i32 { end_calls = end_calls + 1 return v }
function a_step(v: i32) -> i32 { step_calls = step_calls + 1 return v }

function main() -> i32 {
    let total: i32 = sum(a_start(0)..an_end(1000) step a_step(3))
    printf("%d %d %d %d\\n", total, start_calls, end_calls, step_calls)
    return 0
}
""")
    total, starts, ends, steps = out.split()
    assert total == "166833"
    assert (starts, ends, steps) == ("1", "1", "1"), out
