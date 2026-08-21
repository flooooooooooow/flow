"""flowc lowers a slice using the sliced variable's own element type.

Slice lowering in compiler/src/cgen.flow used to carry this comment:

    the element type is unknown here, so use int32_t as the default

so slicing a ptr<f64> emitted a flowc_span_int32_t that no typedef ever
declared, and the user saw clang complain about a generated identifier they
never wrote. See issue #613.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / "compiler" / "build" / "stage_a_driver_flow_self"

pytestmark = pytest.mark.skipif(
    not DRIVER.exists() or not shutil.which("cc"),
    reason="needs a built flowc driver and a C compiler",
)

SOURCE = """
extern {
    function malloc(size: i64) -> ptr<void>
    function printf(fmt: string, a: f64) -> i32
}

function total(v: span<f64>) -> f64 {
    let mut acc: f64 = 0.0
    for i in 0 to v.len as i32 { acc = acc + v[i] }
    return acc
}

function main() -> i32 {
    let raw: ptr<f64> = malloc(24)
    raw[0] = 1.0
    raw[1] = 2.0
    raw[2] = 3.0
    printf("%.1f\\n", total(raw[0..3]))
    return 0
}
"""


def test_slicing_a_double_pointer_builds_a_double_span(tmp_path):
    src = tmp_path / "sp.flow"
    src.write_text(textwrap.dedent(SOURCE))

    run = subprocess.run(
        ["./flow", "run", str(src)],
        cwd=ROOT, capture_output=True, text=True,
        env={**os.environ, "FLOW_HOST": "flowc"},
    )
    combined = run.stdout + run.stderr
    assert "flowc_span_int32_t" not in combined, combined[-2000:]
    assert "6.0" in run.stdout, combined[-2000:]

    generated = (ROOT / "build" / "sp.c").read_text()
    assert "(flowc_span_double){ (double*)raw" in generated
