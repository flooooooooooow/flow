"""Debugger / #line mapping smoke tests (#127)."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c
from flow.monomorphize import monomorphize

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


def test_statement_lines_map_inside_body(tmp_path):
    """Statement-level #line: a breakpoint on any body line lands exactly there."""
    src = tmp_path / "stmt.flow"
    sample = (
        "function step(n: i32) -> i32 {\n"  # 1
        "    let mut acc: i32 = 0\n"  # 2
        "    acc = acc + 1\n"  # 3
        "    if acc > 5 {\n"  # 4
        "        acc = 0\n"  # 5
        "    } else {\n"
        "        acc = acc + 2\n"  # 7
        "    }\n"
        "    let mut i: i32 = 0\n"  # 9
        "    while i < 3 {\n"  # 10
        "        acc = acc + i\n"  # 11
        "        i = i + 1\n"  # 12
        "    }\n"
        "    return acc\n"  # 14
        "}\n"
    )
    src.write_text(sample)
    c = flow_to_c(parse_flow_code(sample), source_file=str(src), debug_info=True)

    # Every statement line in the body appears as a #line directive.
    dirs = [int(m) for m in re.findall(r"#line (\d+)", c)]
    for expect in (1, 2, 3, 4, 5, 7, 9, 10, 11, 12, 14):
        assert expect in dirs, f"missing #line for .flow line {expect}: {dirs}"

    # Each directive sits directly above the C it maps to — proving the
    # mapping is statement-level, not just function-entry-level.
    lines = c.split("\n")
    pairs = {}
    for i, line in enumerate(lines):
        m = re.match(r"\s*#line (\d+)", line)
        if not m:
            continue
        nxt = next(
            (lines[j].strip() for j in range(i + 1, len(lines)) if lines[j].strip()),
            "",
        )
        pairs.setdefault(int(m.group(1)), nxt)
    assert pairs[2].startswith("int32_t acc"), pairs.get(2)
    assert pairs[3].startswith("acc = (acc + 1)"), pairs.get(3)
    assert pairs[4].startswith("if (acc > 5)"), pairs.get(4)
    assert pairs[5].startswith("acc = 0"), pairs.get(5)
    assert pairs[7].startswith("acc = (acc + 2)"), pairs.get(7)
    assert pairs[11].startswith("acc = (acc + i)"), pairs.get(11)
    assert pairs[14].startswith("return acc"), pairs.get(14)


def test_monomorphized_body_keeps_statement_lines(tmp_path):
    """Generic instantiations keep statement-level #line after monomorphize."""
    src = tmp_path / "generic.flow"
    sample = (
        "function twice<T>(x: T) -> T {\n"  # 1
        "    let y: T = x\n"  # 2
        "    return y\n"  # 3
        "}\n"
        "function main() -> i32 {\n"  # 5
        "    let a: i32 = twice(21)\n"  # 6
        "    return a\n"  # 7
        "}\n"
    )
    src.write_text(sample)
    decls = monomorphize(parse_flow_code(sample))
    c = flow_to_c(decls, source_file=str(src), debug_info=True)
    dirs = [int(m) for m in re.findall(r"#line (\d+)", c)]
    # The instantiated `twice_i32` body keeps its exact statement lines.
    assert 2 in dirs, dirs
    assert 3 in dirs, dirs
    assert 6 in dirs, dirs
    assert 7 in dirs, dirs


def test_monomorphized_expect_keeps_line(tmp_path):
    """Rebuilt `expect` statements keep #line via the 1-based line fallback."""
    src = tmp_path / "generic_expect.flow"
    sample = (
        "function clamp<T>(x: T) -> T {\n"  # 1
        "    expect x != 0\n"  # 2
        "    return x\n"  # 3
        "}\n"
        "function main() -> i32 {\n"  # 5
        "    return clamp(1)\n"  # 6
        "}\n"
    )
    src.write_text(sample)
    decls = monomorphize(parse_flow_code(sample))
    c = flow_to_c(decls, source_file=str(src), debug_info=True)
    dirs = [int(m) for m in re.findall(r"#line (\d+)", c)]
    # The monomorphized clamp_i32 body keeps both its statement lines.
    assert 2 in dirs, dirs
    assert 3 in dirs, dirs


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
