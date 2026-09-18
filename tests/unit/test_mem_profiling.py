"""Runtime memory profiling (#740).

The compiler emits an opt-in profiler that reports heap allocation count/bytes,
peak live heap and peak RSS when FLOW_MEM_PROFILE is set at program start. It
stays dormant (and prints nothing) when the variable is unset.
"""

from __future__ import annotations

import os
import subprocess
import tempfile

import pytest

from tests.unit.compiler_helpers import to_c, needs_clang


ALLOCATING_PROG = """
function main() -> i32 {
    let mut total: i32 = 0
    let mut i: i32 = 0
    while i < 40 {
        let a: array<i32> = array<i32>(128)
        a[0] = i
        total = total + a[0]
        i = i + 1
    }
    let mut s: string = ""
    let mut j: i32 = 0
    while j < 16 {
        s = s + "x"
        j = j + 1
    }
    return 0
}
"""


def test_profiler_block_emitted():
    """The report block and env-var gate are present in generated C."""
    c = to_c(ALLOCATING_PROG)
    assert "FLOW_MEM_PROFILE" in c
    assert "flow_mem_profile_init" in c
    assert "flow_mem_report" in c
    assert "getrusage" in c
    assert "Flow memory profile (#740)" in c
    # Allocation entry points are routed through the counting wrappers.
    assert "flow_mem_calloc" in c
    assert "flow_mem_note_alloc" in c


def test_profiler_init_called_in_main():
    """main() reads the env var once at entry."""
    c = to_c(ALLOCATING_PROG)
    assert "flow_mem_profile_init();" in c


def test_deferred_metrics_reported_not_faked():
    """Stack/arena and per-site copy attribution are labelled deferred."""
    c = to_c(ALLOCATING_PROG)
    assert "stack/arena bytes" in c
    assert "deferred" in c


def _build(c_code: str, td: str) -> str:
    c_path = os.path.join(td, "prog.c")
    bin_path = os.path.join(td, "prog")
    with open(c_path, "w") as f:
        f.write(c_code)
    build = subprocess.run(
        ["clang", "-O0", "-o", bin_path, c_path, "-lm"],
        capture_output=True, text=True,
    )
    assert build.returncode == 0, f"clang failed:\n{build.stderr}\n---\n{c_code}"
    return bin_path


@needs_clang
def test_report_printed_when_env_set():
    """With FLOW_MEM_PROFILE set, a report with non-zero counts hits stderr."""
    c = to_c(ALLOCATING_PROG)
    with tempfile.TemporaryDirectory() as td:
        bin_path = _build(c, td)
        env = dict(os.environ, FLOW_MEM_PROFILE="1")
        res = subprocess.run([bin_path], capture_output=True, text=True, env=env)
    assert res.returncode == 0
    err = res.stderr
    assert "Flow memory profile (#740)" in err
    # 40 array allocations + 16 string concatenations = 56 routed allocations.
    for line in err.splitlines():
        if line.startswith("heap allocations"):
            count = int(line.split(":")[1])
            assert count >= 56, f"expected >=56 allocations, got {count}"
        if line.startswith("heap bytes requested"):
            assert int(line.split(":")[1]) > 0
        if line.startswith("peak RSS"):
            assert int(line.split(":")[1]) > 0


@needs_clang
def test_no_report_when_env_unset():
    """With the variable unset the program is silent on stderr."""
    c = to_c(ALLOCATING_PROG)
    with tempfile.TemporaryDirectory() as td:
        bin_path = _build(c, td)
        env = dict(os.environ)
        env.pop("FLOW_MEM_PROFILE", None)
        res = subprocess.run([bin_path], capture_output=True, text=True, env=env)
    assert res.returncode == 0
    assert "Flow memory profile" not in res.stderr


@needs_clang
def test_env_zero_disables_report():
    """FLOW_MEM_PROFILE=0 is treated as off."""
    c = to_c(ALLOCATING_PROG)
    with tempfile.TemporaryDirectory() as td:
        bin_path = _build(c, td)
        env = dict(os.environ, FLOW_MEM_PROFILE="0")
        res = subprocess.run([bin_path], capture_output=True, text=True, env=env)
    assert res.returncode == 0
    assert "Flow memory profile" not in res.stderr
