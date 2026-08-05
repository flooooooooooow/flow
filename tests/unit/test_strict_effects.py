"""Tests for fail-loud unhandled effects (FLOW_STRICT_EFFECTS / --strict-effects)."""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


UNHANDLED = """
effect Log {
    info(msg: string) -> void,
    metric(name: string, value: i32) -> i32,
}

function main() -> i32 {
    Log.info("no handler")
    let v: i32 = Log.metric("x", 1)
    return v
}
"""


def test_dispatch_emits_unhandled_helper():
    c = flow_to_c(parse_flow_code(UNHANDLED))
    assert "_flow_unhandled_effect" in c
    assert 'getenv("FLOW_STRICT_EFFECTS")' in c
    assert "_flow_unhandled_effect(\"Log\", \"info\")" in c


def test_strict_effects_compile_flag_hardcodes_abort():
    c = flow_to_c(parse_flow_code(UNHANDLED), strict_effects=True)
    assert "FLOW_STRICT_EFFECTS_COMPILE" in c
    assert 'getenv("FLOW_STRICT_EFFECTS")' not in c
    assert "abort()" in c


def test_debug_info_emits_statement_line_directives():
    code = """
function main() -> i32 {
    let x: i32 = 1
    return x
}
"""
    c = flow_to_c(
        parse_flow_code(code),
        source_file="/tmp/demo.flow",
        debug_info=True,
    )
    assert '#line ' in c
    assert "/tmp/demo.flow" in c


@pytest.mark.skipif(not Path("/usr/bin/clang").exists() and not Path("/usr/bin/cc").exists(), reason="no C compiler")
def test_runtime_strict_effects_aborts():
    """FLOW_STRICT_EFFECTS=1 must abort on unhandled effect call."""
    c = flow_to_c(parse_flow_code(UNHANDLED))
    cc = "clang" if Path("/usr/bin/clang").exists() or subprocess.call(["which", "clang"], stdout=subprocess.DEVNULL) == 0 else "cc"
    with tempfile.TemporaryDirectory() as td:
        c_path = Path(td) / "unhandled.c"
        exe = Path(td) / "unhandled"
        c_path.write_text(c)
        subprocess.check_call([cc, "-O0", str(c_path), "-o", str(exe)])
        env = os.environ.copy()
        env["FLOW_STRICT_EFFECTS"] = "1"
        proc = subprocess.run(
            [str(exe)],
            env=env,
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0
        assert "unhandled effect" in (proc.stderr or "")

        env["FLOW_STRICT_EFFECTS"] = "0"
        proc_soft = subprocess.run(
            [str(exe)],
            env=env,
            capture_output=True,
            text=True,
        )
        assert proc_soft.returncode == 0
