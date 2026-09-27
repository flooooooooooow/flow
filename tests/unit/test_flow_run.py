"""Tests for the shell-independent Python runner (#400)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import flow.run
from flow.run import _emit_json, main

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


@pytest.mark.skipif(not shutil.which("mlir-opt"), reason="mlir-opt not found")
def test_run_mlir_backend():
    result = _run_flow(HELLO, "--backend=mlir")
    assert result.returncode == 0
    assert "hello from flow" in result.stdout


@pytest.mark.skipif(not shutil.which("mlir-opt"), reason="mlir-opt not found")
def test_run_mlir_backend_exit_code():
    result = _run_flow(EXIT42, "--backend=mlir")
    assert result.returncode == 42
    assert "exiting with 42" in result.stdout


def test_emit_json_direct(capsys):
    t0 = time.monotonic() - 1.0
    _emit_json("out_str", 0, t0, transpile_s=0.1, compile_s=0.2, run_s=0.3, stderr="err_str")
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["stdout"] == "out_str"
    assert data["stderr"] == "err_str"
    assert data["exit_code"] == 0
    assert data["timing"]["transpile_s"] == 0.1
    assert data["timing"]["compile_s"] == 0.2
    assert data["timing"]["run_s"] == 0.3
    assert "error" not in data

    _emit_json("", 1, t0, error="test error")
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error"] == "test error"


def test_run_lenient_flag():
    result = _run_flow(HELLO, "--lenient")
    assert result.returncode == 0
    assert "hello from flow" in result.stdout


def test_run_extra_cflags():
    result = _run_flow(HELLO, "--extra-cflags=-O1")
    assert result.returncode == 0
    assert "hello from flow" in result.stdout


def test_run_backend_auto():
    result = _run_flow(HELLO, "--backend=auto")
    assert result.returncode == 0
    assert "hello from flow" in result.stdout


def test_run_transpile_failure():
    result = _run_flow("invalid flow syntax @@#$")
    assert result.returncode == 1
    assert "Transpile failed:" in result.stderr


def test_run_transpile_failure_json():
    result = _run_flow("invalid flow syntax @@#$", "--json")
    data = json.loads(result.stdout)
    assert data["exit_code"] == 1
    assert "error" in data
    assert "transpile failed" in data["error"]


def test_run_compile_failure():
    result = _run_flow(HELLO, "--extra-cflags=-invalid-clang-flag-xyz999")
    assert result.returncode == 1
    assert "Compile failed:" in result.stderr


def test_run_compile_failure_json():
    result = _run_flow(HELLO, "--json", "--extra-cflags=-invalid-clang-flag-xyz999")
    data = json.loads(result.stdout)
    assert data["exit_code"] == 1
    assert "error" in data
    assert "compile failed" in data["error"]


def test_main_missing_clang_normal(monkeypatch, capsys, tmp_path):
    flow_file = tmp_path / "hello.flow"
    flow_file.write_text(HELLO)
    monkeypatch.setattr(shutil, "which", lambda cmd: None)
    monkeypatch.setattr("sys.argv", ["flow.run", str(flow_file)])
    ret = main()
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: clang not found" in captured.err


def test_main_missing_clang_json(monkeypatch, capsys, tmp_path):
    flow_file = tmp_path / "hello.flow"
    flow_file.write_text(HELLO)
    monkeypatch.setattr(shutil, "which", lambda cmd: None)
    monkeypatch.setattr("sys.argv", ["flow.run", str(flow_file), "--json"])
    ret = main()
    assert ret == 1
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["exit_code"] == 1
    assert data["error"] == "clang not found"


def test_main_in_process_hello(monkeypatch, capsys, tmp_path):
    flow_file = tmp_path / "hello.flow"
    flow_file.write_text(HELLO)
    monkeypatch.setattr("sys.argv", ["flow.run", str(flow_file)])
    ret = main()
    assert ret == 0
    captured = capsys.readouterr()
    assert "hello from flow" in captured.out


def test_main_in_process_json(monkeypatch, capsys, tmp_path):
    flow_file = tmp_path / "hello.flow"
    flow_file.write_text(HELLO)
    monkeypatch.setattr("sys.argv", ["flow.run", str(flow_file), "--json"])
    ret = main()
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["exit_code"] == 0
    assert "hello from flow" in data["stdout"]


def test_main_in_process_missing_file(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["flow.run", "/nonexistent.flow"])
    ret = main()
    assert ret == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_main_in_process_keep(monkeypatch, tmp_path):
    flow_file = tmp_path / "hello.flow"
    flow_file.write_text(HELLO)
    keep_dir = tmp_path / "keep_dir"
    monkeypatch.setattr("sys.argv", ["flow.run", str(flow_file), "--keep", str(keep_dir)])
    ret = main()
    assert ret == 0
    c_files = list(keep_dir.glob("*.c"))
    assert len(c_files) >= 1


def test_main_in_process_backend_auto_success(monkeypatch, capsys, tmp_path):
    flow_file = tmp_path / "hello.flow"
    flow_file.write_text(HELLO)
    monkeypatch.setattr("sys.argv", ["flow.run", str(flow_file), "--backend=auto"])
    ret = main()
    assert ret == 0
    captured = capsys.readouterr()
    assert "hello from flow" in captured.out


def test_main_in_process_backend_auto_fallback(monkeypatch, capsys, tmp_path):
    # Invalid syntax forces auto backend detection exception -> fallback to "c" -> transpile failure
    flow_file = tmp_path / "bad.flow"
    flow_file.write_text("invalid syntax @@@")
    monkeypatch.setattr("sys.argv", ["flow.run", str(flow_file), "--backend=auto"])
    ret = main()
    assert ret == 1
    captured = capsys.readouterr()
    assert "Transpile failed:" in captured.err


def test_main_in_process_transpile_failure_json(monkeypatch, capsys, tmp_path):
    flow_file = tmp_path / "bad.flow"
    flow_file.write_text("invalid syntax @@@")
    monkeypatch.setattr("sys.argv", ["flow.run", str(flow_file), "--json"])
    ret = main()
    assert ret == 1
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["exit_code"] == 1
    assert "transpile failed" in data["error"]


def test_main_in_process_compile_failure_normal(monkeypatch, capsys, tmp_path):
    flow_file = tmp_path / "hello.flow"
    flow_file.write_text(HELLO)
    monkeypatch.setattr("sys.argv", ["flow.run", str(flow_file), "--extra-cflags=-invalid-clang-flag-xyz999"])
    ret = main()
    assert ret == 1
    captured = capsys.readouterr()
    assert "Compile failed:" in captured.err


def test_main_in_process_compile_failure_json(monkeypatch, capsys, tmp_path):
    flow_file = tmp_path / "hello.flow"
    flow_file.write_text(HELLO)
    monkeypatch.setattr("sys.argv", ["flow.run", str(flow_file), "--json", "--extra-cflags=-invalid-clang-flag-xyz999"])
    ret = main()
    assert ret == 1
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["exit_code"] == 1
    assert "compile failed" in data["error"]
