"""Smoke tests for hashmap and bigint examples (#252/#267)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


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
