"""Regression for #817: concurrent `flow run` of two projects that share a
source basename (src/main.flow) must each execute their own program.

Before the fix, `flow run` emitted every executable to build/<basename> in the
repo-global build directory, so two projects both named main.flow raced through
the same build/main artifact and one could launch the other's binary. The fix
gives each run invocation an isolated build root.
"""
import os
import shutil
import subprocess
import concurrent.futures
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DRIVER = REPO / "flow-driver"

PROG = """function main() -> i32 {{
    println("{tag}")
    return 0
}}
"""


def _make_project(root: Path, tag: str) -> Path:
    src = root / "src"
    src.mkdir(parents=True, exist_ok=True)
    main = src / "main.flow"
    main.write_text(PROG.format(tag=tag))
    return main


def _run(main: Path) -> str:
    env = dict(os.environ, FLOW_HOST="python")
    res = subprocess.run(
        [str(DRIVER), "run", str(main)],
        capture_output=True, text=True, env=env, cwd=str(REPO), timeout=180,
    )
    return res.stdout


@pytest.mark.skipif(not DRIVER.exists(), reason="flow-driver not present")
@pytest.mark.skipif(shutil.which("clang") is None, reason="clang required to build")
def test_concurrent_run_does_not_cross_projects(tmp_path):
    a_main = _make_project(tmp_path / "proj_a", "I_AM_PROJECT_A")
    b_main = _make_project(tmp_path / "proj_b", "I_AM_PROJECT_B")

    # Repeat a few times to exercise the compile/launch overlap window.
    for _ in range(3):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            fa = ex.submit(_run, a_main)
            fb = ex.submit(_run, b_main)
            out_a, out_b = fa.result(), fb.result()
        assert "I_AM_PROJECT_A" in out_a, f"project A got: {out_a!r}"
        assert "I_AM_PROJECT_B" not in out_a, f"project A ran B's binary: {out_a!r}"
        assert "I_AM_PROJECT_B" in out_b, f"project B got: {out_b!r}"
        assert "I_AM_PROJECT_A" not in out_b, f"project B ran A's binary: {out_b!r}"
