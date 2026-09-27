"""Compiled behaviour of `sum(range | range)` and `sum(range & range)`.

The unit tests check the folded arithmetic against Python's own sets. The
run checks (the helper agrees with a brute-force loop, each bound is
evaluated once) live in tests/lang/test_range_algebra.flow. What stays here
is the check on the Python host's generated C.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_literal_algebra_leaves_no_helper_behind():
    """A fully literal expression folds, so no helper is emitted at all."""
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "p.flow"
        c = Path(td) / "p.c"
        src.write_text(
            "function main() -> i32 {\n"
            "    printf(\"%d\\n\", sum(0..1000 step 3 | 0..1000 step 5))\n"
            "    return 0\n"
            "}\n"
        )
        assert subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(src), "--c", "-o", str(c)],
            cwd=ROOT, env=env, capture_output=True, text=True,
        ).returncode == 0
        generated = c.read_text()
    assert "233168" in generated
    assert "__flow_sum_range_union" not in generated
    assert "__flow_range_modinv" not in generated
