from __future__ import annotations

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


def test_sum_range_compiles_to_closed_form(tmp_path: Path) -> None:
    """The values are checked in tests/lang/test_range_sum_step.flow."""
    generated = tmp_path / "range_sum.c"
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


def test_sum_range_rejects_literal_zero_step() -> None:
    with pytest.raises(FlowSyntaxError, match="step must not be zero"):
        parse_flow_code(
            """
function bad() -> i32 {
    return sum(0..10 step 0)
}
"""
        )
