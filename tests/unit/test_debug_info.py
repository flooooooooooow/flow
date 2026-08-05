"""Debugger / #line mapping smoke tests (#127)."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c

ROOT = Path(__file__).resolve().parents[2]
FLOW = ROOT / "flow"

SAMPLE = """
function add(a: i32, b: i32) -> i32 {
    let s: i32 = a + b
    return s
}

function main() -> i32 {
    let x: i32 = add(1, 2)
    return x
}
"""


def test_debug_info_emits_line_directives(tmp_path):
    src = tmp_path / "sample.flow"
    src.write_text(SAMPLE)
    c = flow_to_c(parse_flow_code(SAMPLE), source_file=str(src), debug_info=True)
    assert "#line" in c
    assert str(src) in c or "sample.flow" in c
    # At least one mapping into the body (not only the file header)
    assert c.count("#line") >= 2
    # Distinct Flow lines for let vs return in main
    lines = re.findall(r"#line (\d+)", c)
    assert len(set(lines)) >= 2, lines


def test_flow_debug_no_launch_builds_artifacts():
    result = subprocess.run(
        [str(FLOW), "debug", "examples/basics/hello_world.flow", "--no-launch"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert (ROOT / "build" / "hello_world.debug").exists()
    c_file = ROOT / "build" / "hello_world.debug.c"
    assert c_file.exists()
    text = c_file.read_text()
    assert "#line" in text
