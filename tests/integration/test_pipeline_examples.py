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
]


def _run_transpiler(example: str, out: Path, extra_args):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + (
        ":" + env["PYTHONPATH"] if "PYTHONPATH" in env else ""
    )
    return subprocess.run(
        ["python3", "-m", "flow.transpiler", str(EXAMPLES / example), "-o", str(out)]
        + list(extra_args),
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
    )


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
