"""Tests for temp arena (#267/#268), hashmap/bigint (#252), safety profile (#273)."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def test_strcat_uses_temp_arena():
    c = flow_to_c(
        parse_flow_code(
            """
            function main() -> i32 {
                let s: string = "a" + "b"
                return 0
            }
            """
        )
    )
    assert "flow_temp_alloc" in c
    assert "flow_temp_free_all" in c
    assert "atexit(flow_temp_free_all)" in c


def test_escaping_closure_env_uses_temp_arena():
    c = flow_to_c(
        parse_flow_code(
            """
            function main() -> i32 {
                let n: i32 = 3
                let f: (i32) -> i32 = |x: i32| -> i32 { return x + n }
                return f(1)
            }
            """
        )
    )
    assert "flow_temp_alloc(sizeof(" in c
    assert "malloc(sizeof(" not in c or "flow_temp_alloc" in c


def _compile_and_run(code: str, expected: int) -> None:
    with tempfile.TemporaryDirectory() as td:
        c_path = Path(td) / "t.c"
        exe = Path(td) / "t"
        c_path.write_text(flow_to_c(parse_flow_code(code)))
        subprocess.check_call(["cc", "-O0", str(c_path), "-o", str(exe)])
        r = subprocess.run([str(exe)], check=False)
        assert r.returncode == expected


def test_hashmap_i64_i64_runs():
    src = ROOT / "examples" / "basics" / "hashmap_i64_smoke.flow"
    _compile_and_run(src.read_text(), 30)


def test_bigint_mod_u32_runs():
    src = ROOT / "examples" / "basics" / "bigint_smoke.flow"
    _compile_and_run(src.read_text(), 7)


def test_safety_profile_rejects_recursion():
    code = """
function boom(n: i32) -> i32 {
    if n <= 0 { return 0 }
    return boom(n - 1)
}
function main() -> i32 {
    return boom(3)
}
"""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "rec.flow"
        p.write_text(code)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        env["FLOW_PROFILE"] = "safety"
        r = subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(p), "--c", "--lenient", "-o", str(Path(td) / "out.c")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        assert r.returncode != 0
        assert "recursion" in (r.stderr + r.stdout).lower()


def test_safety_profile_rejects_unbounded_while():
    code = """
function main() -> i32 {
    let mut i: i32 = 0
    while i < 10 {
        i = i + 1
    }
    return i
}
"""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "w.flow"
        p.write_text(code)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        env["FLOW_PROFILE"] = "safety"
        r = subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(p), "--c", "-o", str(Path(td) / "out.c")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        assert r.returncode != 0
        assert "max_iterations" in (r.stderr + r.stdout).lower()


def test_max_iterations_emits_runtime_guard():
    c = flow_to_c(
        parse_flow_code(
            """
            function main() -> i32 {
                let mut i: i32 = 0
                @max_iterations(100)
                while i < 10 {
                    i = i + 1
                }
                return i
            }
            """
        )
    )
    assert "__flow_while_bound_" in c
    assert "max_iterations(100)" in c
