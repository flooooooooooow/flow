"""Tests for the shell-independent Python runner (#400)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

HELLO = """
function main() -> i32 {
    println("hello from flow")
    return 0
}
"""

EXIT42 = """
function main() -> i32 {
    println("exiting with 42")
    return 42
}
"""


def _run_flow(source: str, *extra_args: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile(suffix=".flow", mode="w", delete=False) as f:
        f.write(source)
        path = f.name
    try:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-m", "flow.run", path, *extra_args],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
    finally:
        Path(path).unlink(missing_ok=True)


def test_run_hello_world():
    result = _run_flow(HELLO)
    assert result.returncode == 0
    assert "hello from flow" in result.stdout


def test_run_exit_code():
    result = _run_flow(EXIT42)
    assert result.returncode == 42
    assert "exiting with 42" in result.stdout


def test_run_json_output():
    result = _run_flow(HELLO, "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["exit_code"] == 0
    assert "hello from flow" in data["stdout"]
    assert "timing" in data
    assert data["timing"]["total_s"] > 0


def test_run_json_exit_code():
    result = _run_flow(EXIT42, "--json")
    data = json.loads(result.stdout)
    assert data["exit_code"] == 42


def test_run_missing_file():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "flow.run", "/nonexistent.flow"],
        capture_output=True, text=True, env=env, timeout=10,
    )
    assert result.returncode == 1
    assert "not found" in result.stderr


def test_run_keep_intermediate():
    with tempfile.TemporaryDirectory() as tmp:
        with tempfile.NamedTemporaryFile(suffix=".flow", mode="w", delete=False) as f:
            f.write(HELLO)
            path = f.name
        try:
            env = dict(os.environ)
            env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
            result = subprocess.run(
                [sys.executable, "-m", "flow.run", path, "--keep", tmp],
                capture_output=True, text=True, env=env, timeout=30,
            )
            assert result.returncode == 0
            # The C file should be kept
            c_files = list(Path(tmp).glob("*.c"))
            assert len(c_files) >= 1
        finally:
            Path(path).unlink(missing_ok=True)
