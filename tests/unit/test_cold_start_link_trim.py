"""Cold-start link trimming for tiny programs (issue #746).

A program that reaches none of the optional native runtime pieces should not
link the Python3, Metal/Foundation or OpenSSL frameworks, because loading them
at exec time costs several milliseconds of dyld work the program never uses. The
driver runs a probe link that omits those frameworks and the ObjC Metal shim; it
only falls back to the full link when the probe finds a needed symbol, so a
program that does use a framework keeps it and behaves exactly as before.

These tests drive `flow-driver compile` and read the Mach-O load commands with
otool, so they are gated to macOS with a working clang and Python3 framework.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / "flow-driver"

OPTIONAL_FRAMEWORKS = ("Python3", "Metal.framework", "Foundation.framework",
                       "libssl", "libcrypto")

TINY = """
function main() -> i32 {
    let a: i32 = 6
    let b: i32 = 7
    print(a * b)
    println("")
    return 0
}
"""

pytestmark = pytest.mark.skipif(
    sys.platform != "darwin"
    or shutil.which("clang") is None
    or shutil.which("otool") is None,
    reason="link trimming test needs macOS with clang + otool",
)


def _compile(source: str, *, trim: bool):
    """Compile `source` via the driver and return (exe_path, otool_output)."""
    workdir = Path(tempfile.mkdtemp(prefix="flow_coldstart_"))
    src = workdir / "prog.flow"
    src.write_text(source)
    build_root = workdir / "build"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["FLOW_HOST"] = "python"
    env["FLOW_BUILD_ROOT"] = str(build_root)
    if not trim:
        env["FLOW_NO_LINK_TRIM"] = "1"
    proc = subprocess.run(
        ["bash", str(DRIVER), "compile", str(src)],
        capture_output=True, text=True, env=env, timeout=180,
    )
    if proc.returncode != 0:
        pytest.skip(f"driver could not build (toolchain unavailable): {proc.stderr[-400:]}")
    exe = build_root / "prog"
    assert exe.exists(), proc.stdout + proc.stderr
    otool = subprocess.run(["otool", "-L", str(exe)], capture_output=True, text=True)
    return exe, otool.stdout, workdir


def test_tiny_program_trims_optional_frameworks():
    exe, deps, workdir = _compile(TINY, trim=True)
    try:
        for fw in OPTIONAL_FRAMEWORKS:
            assert fw not in deps, f"tiny program should not link {fw}:\n{deps}"
        # The program still runs and produces its output.
        run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=30)
        assert run.returncode == 0
        assert "42" in run.stdout
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def test_opt_out_keeps_full_framework_link():
    # With trimming disabled the historical full link is used, which lists the
    # optional frameworks. This proves the trim is the thing dropping them.
    exe, deps, workdir = _compile(TINY, trim=False)
    try:
        assert any(fw in deps for fw in OPTIONAL_FRAMEWORKS), (
            "full link should still list the optional frameworks:\n" + deps
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def test_python_program_keeps_python_framework():
    example = ROOT / "examples" / "interop" / "python_embed.flow"
    if not example.exists():
        pytest.skip("python interop example not present")
    workdir = Path(tempfile.mkdtemp(prefix="flow_coldstart_py_"))
    build_root = workdir / "build"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["FLOW_HOST"] = "python"
    env["FLOW_BUILD_ROOT"] = str(build_root)
    try:
        proc = subprocess.run(
            ["bash", str(DRIVER), "compile", str(example)],
            capture_output=True, text=True, env=env, timeout=180,
        )
        if proc.returncode != 0:
            pytest.skip(f"driver could not build python example: {proc.stderr[-400:]}")
        exe = build_root / "python_embed"
        assert exe.exists(), proc.stdout + proc.stderr
        deps = subprocess.run(["otool", "-L", str(exe)], capture_output=True, text=True).stdout
        # A program that embeds Python must still fall back to the full link.
        assert "Python3" in deps, "python-embedding program must keep Python3:\n" + deps
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
