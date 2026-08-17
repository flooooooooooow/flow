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
