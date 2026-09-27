"""Dual CPU backends on the WASM page builder (scripts/wasm_build.sh).

The builder is the Flow program in scripts/tools/wasm_build. These tests
drive it through its shim, so they cover the argument handling, the emcc
command line and the pages it writes.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SHIM = ROOT / "scripts" / "wasm_build.sh"
HELLO = ROOT / "examples" / "wasm" / "hello_wasm.flow"
SNAKE = ROOT / "examples" / "games" / "snake_gfx.flow"


def _env(**extra: str) -> dict:
    env = dict(os.environ)
    src = str(ROOT / "src")
    env["PYTHONPATH"] = src + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env.update(extra)
    return env


def run_shim(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(SHIM), *args], cwd=ROOT, env=env or _env(), capture_output=True, text=True
    )


def _emcc_ok() -> bool:
    if shutil.which("emcc") is None:
        return False
    env = dict(os.environ)
    for key, value in {
        "EMSDK_PYTHON": "/opt/homebrew/bin/python3.14",
        "EM_LLVM_ROOT": "/opt/homebrew/opt/emscripten/libexec/llvm/bin",
        "EM_BINARYEN_ROOT": "/opt/homebrew/opt/emscripten/libexec/binaryen",
    }.items():
        if not env.get(key) and Path(value).exists():
            env[key] = value
    try:
        return subprocess.run(["emcc", "-v"], capture_output=True, env=env, timeout=30).returncode == 0
    except Exception:
        return False


needs_cc = pytest.mark.skipif(
    shutil.which("cc") is None and shutil.which("clang") is None, reason="no C compiler"
)


@needs_cc
def test_backend_from_environment_is_validated(tmp_path: Path):
    result = run_shim(str(HELLO), "--out", str(tmp_path), env=_env(FLOW_CPU_BACKEND="spirv"))
    assert result.returncode == 1
    assert result.stderr == "error: unknown backend 'spirv' (expected c|mlir)\n"


@needs_cc
def test_backend_choice_is_checked_by_the_parser():
    result = run_shim(str(HELLO), "--backend", "spirv")
    assert result.returncode == 2
    assert "invalid choice: 'spirv' (choose from c, mlir)" in result.stderr


@needs_cc
@pytest.mark.skipif(not HELLO.exists(), reason="hello_wasm.flow missing")
def test_emcc_command_preload_link_and_opt(tmp_path: Path):
    """A fake emcc records the command line the builder hands it."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    log = tmp_path / "argv.txt"
    fake = bindir / "emcc"
    fake.write_text(
        "#!/bin/sh\n"
        '[ "$1" = "-v" ] && exit 0\n'
        f'for a in "$@"; do printf "%s\\n" "$a"; done > "{log}"\n'
        'echo "emcc: error: fake emcc" >&2\n'
        "exit 1\n"
    )
    fake.chmod(0o755)
    env = _env(PATH=f"{bindir}:{os.environ['PATH']}")
    support = ROOT / "runtime" / "flow_rt_support.c"
    result = run_shim(
        str(HELLO),
        "--out", str(tmp_path / "out"),
        "-O1",
        "--preload", "/tmp/data@/data",
        "--link", str(support),
        "--link", "runtime/gfx_macos.m",
        "--initial-memory", "64MB",
        env=env,
    )
    assert result.returncode == 1
    assert result.stderr == "error: emcc: error: fake emcc\n"
    cmd = log.read_text().splitlines()
    assert "-sFORCE_FILESYSTEM=1" in cmd
    assert cmd[cmd.index("--preload-file") + 1] == "/tmp/data@/data"
    assert str(support.resolve()) in cmd
    assert not any(c.endswith(".m") for c in cmd)
    assert "-sINITIAL_MEMORY=64MB" in cmd
    assert "-O1" in cmd


@needs_cc
@pytest.mark.skipif(not HELLO.exists(), reason="hello_wasm.flow missing")
@pytest.mark.skipif(not _emcc_ok(), reason="emcc not usable")
@pytest.mark.parametrize("backend", ["c", "mlir"])
def test_wasm_build_both_backends(backend: str, tmp_path: Path):
    out = tmp_path / backend
    result = run_shim(str(HELLO), "--out", str(out), "--backend", backend, "-O1", "--json")
    assert result.returncode == 0, result.stderr
    info = json.loads(result.stdout)
    assert info["backend"] == backend
    assert (out / "hello_wasm.wasm").exists()
    assert (out / "hello_wasm.js").exists()
    html = (out / "index.html").read_text()
    assert ("MLIR" in html) if backend == "mlir" else ("C &rarr; WebAssembly" in html)


@needs_cc
@pytest.mark.skipif(not HELLO.exists(), reason="hello_wasm.flow missing")
@pytest.mark.skipif(not _emcc_ok(), reason="emcc not usable")
@pytest.mark.parametrize("backend", ["c", "mlir"])
def test_wasm_build_preload_emits_data(backend: str, tmp_path: Path):
    data_dir = tmp_path / "pack"
    data_dir.mkdir()
    (data_dir / "note.txt").write_text("hello from preload\n")
    out = tmp_path / f"out-{backend}"
    result = run_shim(
        str(HELLO), "--out", str(out), "--backend", backend, "-O1",
        "--preload", f"{data_dir}@/data",
        "--link", str(ROOT / "runtime" / "flow_rt_support.c"),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    info = json.loads(result.stdout)
    assert info["backend"] == backend
    assert (out / "hello_wasm.wasm").exists()
    assert (out / "hello_wasm.data").exists()
    assert info.get("data_bytes", 0) > 0


@needs_cc
@pytest.mark.skipif(not SNAKE.exists(), reason="snake_gfx.flow missing")
@pytest.mark.skipif(not _emcc_ok(), reason="emcc not usable")
def test_wasm_mlir_gfx_snake(tmp_path: Path):
    """Epic #221: MLIR backend builds a gfx+ASYNCIFY canvas page."""
    out = tmp_path / "snake-mlir"
    result = run_shim(str(SNAKE), "--out", str(out), "--backend", "mlir", "-O1", "--json")
    assert result.returncode == 0, result.stderr
    info = json.loads(result.stdout)
    assert info["backend"] == "mlir"
    assert info["gfx"] is True
    assert (out / "snake_gfx.wasm").exists()
    html = (out / "index.html").read_text()
    assert "MLIR" in html
    assert "canvas" in html.lower()
