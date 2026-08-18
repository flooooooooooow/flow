"""Counted-loop rotation (#473) must not change what a program computes.

Each case is compiled twice through the C backend: once from the parsed AST and
once from the AST after `canonicalize_counted_loops`. Both binaries run and must
agree. The MLIR generator applies the same rewrite, so this pins the semantics
of the transform itself rather than the text of any one backend.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

import pytest

from pathlib import Path

from flow.c_generator import flow_to_c
from flow.mlir_canonicalize import canonicalize_counted_loops
from flow.mlir_generator import MLIRGenerator
from flow.parser import parse_flow_code


needs_clang = pytest.mark.skipif(
    shutil.which("clang") is None, reason="clang not available"
)


def _run(c_code: str) -> int:
    with tempfile.TemporaryDirectory() as td:
        c_path = os.path.join(td, "prog.c")
        bin_path = os.path.join(td, "prog")
        with open(c_path, "w") as handle:
            handle.write(c_code)
        build = subprocess.run(
            ["clang", "-O0", "-o", bin_path, c_path, "-lm"],
            capture_output=True,
            text=True,
        )
        assert build.returncode == 0, f"{build.stderr}\n---\n{c_code}"
        return subprocess.run([bin_path], capture_output=True).returncode


def _rotated_c(source: str) -> str:
    decls = parse_flow_code(source)
    for decl in decls:
        body = getattr(decl, "body", None)
        if body is not None and hasattr(body, "statements"):
            decl.body = canonicalize_counted_loops(body)
    return flow_to_c(decls)


COUNTDOWN = """
function main() -> i32 {
    let mut count: i32 = 5
    let mut acc: i32 = 0
    while true {
        acc = acc + 1
        if count == 0 {
            break
        }
        count = count - 1
    }
    return acc
}
"""

ZERO_TRIP = """
function main() -> i32 {
    let mut count: i32 = 0
    let mut acc: i32 = 0
    while true {
        acc = acc + 7
        if count == 0 {
            break
        }
        count = count - 1
    }
    return acc
}
"""

BREAK_FIRST = """
function main() -> i32 {
    let mut count: i32 = 9
    let mut acc: i32 = 0
    while true {
        if count == 0 {
            break
        }
        acc = acc + 2
        count = count - 1
    }
    return acc
}
"""

SUFFIX_AFTER_DECREMENT = """
function main() -> i32 {
    let mut count: i32 = 4
    let mut acc: i32 = 0
    while true {
        acc = acc + 1
        if count == 0 {
            break
        }
        count = count - 1
        acc = acc + 10
    }
    return acc
}
"""

NESTED_IF_IN_PREFIX = """
function main() -> i32 {
    let mut count: i32 = 6
    let mut acc: i32 = 0
    while true {
        if count > 3 {
            acc = acc + 1
        } else {
            acc = acc + 100
        }
        if count == 0 {
            break
        }
        count = count - 1
    }
    return acc
}
"""

STEP_TWO = """
function main() -> i32 {
    let mut count: i32 = 8
    let mut acc: i32 = 0
    while true {
        acc = acc + 3
        if count == 0 {
            break
        }
        count = count - 2
    }
    return acc
}
"""


CASES = {
    "countdown": COUNTDOWN,
    "zero_trip": ZERO_TRIP,
    "break_first": BREAK_FIRST,
    "suffix_after_decrement": SUFFIX_AFTER_DECREMENT,
    "nested_if_in_prefix": NESTED_IF_IN_PREFIX,
    "step_two": STEP_TWO,
}


@needs_clang
@pytest.mark.parametrize("name", sorted(CASES))
def test_rotation_preserves_the_result(name: str) -> None:
    source = CASES[name]
    original = _run(flow_to_c(parse_flow_code(source)))
    rotated = _run(_rotated_c(source))
    assert original == rotated, f"{name}: {original} != {rotated}"


@needs_clang
def test_expected_iteration_counts() -> None:
    # Guards against both forms being wrong in the same way.
    assert _run(flow_to_c(parse_flow_code(COUNTDOWN))) == 6
    assert _run(flow_to_c(parse_flow_code(ZERO_TRIP))) == 7
    assert _run(flow_to_c(parse_flow_code(BREAK_FIRST))) == 18


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "counted_loop_rotation.flow"


@needs_clang
def test_doom_shaped_fixture_survives_rotation() -> None:
    source = FIXTURE.read_text()
    assert _run(flow_to_c(parse_flow_code(source))) == _run(_rotated_c(source))


def test_doom_shaped_fixture_lowers_to_a_latch_compare() -> None:
    mlir = MLIRGenerator().generate_module(parse_flow_code(FIXTURE.read_text()))
    hot = mlir.split("func.func @draw_column")[1].split("\n  func.func")[0]
    # One test, at the latch, driving the loop.
    assert hot.count("cf.cond_br") == 1, hot
    assert "arith.cmpi ne" in hot, hot
    # #474: the accessor call inside the hot loop is gone.
    assert "func.call @dc_iscale_value" not in hot, hot
    assert hot.count("llvm.mlir.addressof @dc_iscale") == 2, hot
