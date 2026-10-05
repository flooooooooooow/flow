"""End-to-end coverage for the `|>` pipeline example programs.

Runs each pipeline example through the real transpiler CLI on both backends,
so the placeholder / fork / inferred-record desugarings stay wired through the
full pipeline (parse -> type check -> monomorphize -> codegen), not just the
parser-level unit tests.
"""

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
EXAMPLES = ROOT / "examples" / "basics"

PIPELINE_EXAMPLES = [
    "pipeline_placeholder.flow",
    "pipeline_fork.flow",
    "pipeline_fork_inferred.flow",
    "pipeline_choose.flow",
]

# Flow-composition examples live under examples/evolution.
EVOLUTION = ROOT / "examples" / "evolution"
FLOW_EXAMPLES = [
    "parent_input_connect.flow",
    "flow_pipeline_stages.flow",
]


def _transpile(path: Path, out: Path, extra_args):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + (
        ":" + env["PYTHONPATH"] if "PYTHONPATH" in env else ""
    )
    return subprocess.run(
        ["python3", "-m", "flow.transpiler", str(path), "-o", str(out)]
        + list(extra_args),
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
    )


def _run_transpiler(example: str, out: Path, extra_args):
    return _transpile(EXAMPLES / example, out, extra_args)


@pytest.mark.parametrize("example", PIPELINE_EXAMPLES)
def test_pipeline_example_compiles_mlir(example, tmp_path):
    out = tmp_path / (example + ".mlir")
    result = _run_transpiler(example, out, [])
    assert result.returncode == 0, result.stderr
    assert out.exists() and out.stat().st_size > 0


@pytest.mark.parametrize("example", PIPELINE_EXAMPLES)
def test_pipeline_example_compiles_c(example, tmp_path):
    out = tmp_path / (example + ".c")
    result = _run_transpiler(example, out, ["--c"])
    assert result.returncode == 0, result.stderr
    assert out.exists() and out.stat().st_size > 0


def test_inferred_fork_synthesizes_a_struct(tmp_path):
    """The anonymous fork example should emit exactly one synthesized record."""
    result = _run_transpiler("pipeline_fork_inferred.flow", tmp_path / "x.mlir", [])
    assert result.returncode == 0, result.stderr
    # 3 user functions + main + printf extern = 5; 1 synthesized struct.
    assert "1 structs" in result.stderr


_SINGLE_EVAL_SRC = """
struct Pair { a: i32, b: i32 }
function twice(x: i32) -> i32 { return x * 2 }
function square(x: i32) -> i32 { return x * x }
function frames(x: i32) -> i32 { return x + 1 }
function main() -> i32 {
    let p: Pair = frames(7) |> Pair { a = twice, b = square }
    return p.a
}
"""


@pytest.mark.parametrize("example", FLOW_EXAMPLES)
def test_flow_example_compiles_mlir(example, tmp_path):
    result = _transpile(EVOLUTION / example, tmp_path / (example + ".mlir"), [])
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("example", FLOW_EXAMPLES)
def test_flow_example_compiles_c(example, tmp_path):
    result = _transpile(EVOLUTION / example, tmp_path / (example + ".c"), ["--c"])
    assert result.returncode == 0, result.stderr


def test_fork_source_hoisted_once_in_generated_c(tmp_path):
    """A non-trivial fork source is bound to one temp in the emitted C."""
    src = tmp_path / "single_eval.flow"
    src.write_text(_SINGLE_EVAL_SRC)
    out = tmp_path / "single_eval.c"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + (
        ":" + env["PYTHONPATH"] if "PYTHONPATH" in env else ""
    )
    result = subprocess.run(
        ["python3", "-m", "flow.transpiler", str(src), "--c", "-o", str(out)],
        capture_output=True, text=True, cwd=ROOT, env=env,
    )
    assert result.returncode == 0, result.stderr
    c = out.read_text()
    # The source is bound to one temp (`__fork_src_0 = frames...(7)`) and both
    # branches read that temp: one definition + two uses == three occurrences,
    # so the source runs once rather than once per field.
    assert c.count("__fork_src_0") == 3
    assert "= frames" in c  # the temp's initializer is the source call
