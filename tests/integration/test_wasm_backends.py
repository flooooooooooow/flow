"""Unit tests for dual CPU backends on the WASM page builder."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HELLO = ROOT / "examples" / "wasm" / "hello_wasm.flow"


def _emcc_ok() -> bool:
    if shutil.which("emcc") is None:
        return False
    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    for key, value in {
        "EMSDK_PYTHON": "/opt/homebrew/bin/python3.14",
        "EM_LLVM_ROOT": "/opt/homebrew/opt/emscripten/libexec/llvm/bin",
        "EM_BINARYEN_ROOT": "/opt/homebrew/opt/emscripten/libexec/binaryen",
    }.items():
        if not env.get(key) and Path(value).exists():
            env[key] = value
    try:
        return (
            subprocess.run(
                ["emcc", "-v"], capture_output=True, env=env, timeout=30
            ).returncode
            == 0
        )
    except Exception:
        return False


def test_resolve_backend_defaults_and_env(monkeypatch):
    sys.path.insert(0, str(ROOT / "scripts"))
    import wasm_build as wb  # type: ignore

    monkeypatch.delenv("FLOW_CPU_BACKEND", raising=False)
    assert wb.resolve_backend(None) == "c"
    monkeypatch.setenv("FLOW_CPU_BACKEND", "mlir")
    assert wb.resolve_backend(None) == "mlir"
    assert wb.resolve_backend("c") == "c"
    with pytest.raises(wb.BuildError):
        wb.resolve_backend("spirv")


def test_emcc_command_preload_and_link():
    sys.path.insert(0, str(ROOT / "scripts"))
    import wasm_build as wb  # type: ignore

    out = Path("/tmp/out.js")
    support = ROOT / "runtime" / "flow_rt_support.c"
    cocoa = ROOT / "runtime" / "gfx_macos.m"
    cmd = wb.emcc_command(
        Path("prog.c"),
        out,
        gfx=True,
        opt="-O1",
        preload=["/tmp/data@/data"],
        extra_link=[support, cocoa],
        initial_memory="64MB",
        asyncify_stack_size=65536,
    )
    assert "-sFORCE_FILESYSTEM=1" in cmd
    assert "--preload-file" in cmd
    assert "/tmp/data@/data" in cmd
    assert str(support.resolve()) in cmd
    assert not any(str(cocoa) in c or c.endswith(".m") for c in cmd)
    assert "-sINITIAL_MEMORY=64MB" in cmd
    assert "-sASYNCIFY_STACK_SIZE=65536" in cmd
    assert any(c.endswith("gfx_wasm.c") for c in cmd)


@pytest.mark.skipif(not HELLO.exists(), reason="hello_wasm.flow missing")
@pytest.mark.skipif(not _emcc_ok(), reason="emcc not usable")
@pytest.mark.parametrize("backend", ["c", "mlir"])
def test_wasm_build_both_backends(backend: str, tmp_path: Path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import wasm_build as wb  # type: ignore

    out = tmp_path / backend
    result = wb.build(HELLO, out, backend=backend, opt="-O1", timeout=120)
    assert result["backend"] == backend
    assert (out / "hello_wasm.wasm").exists()
    assert (out / "hello_wasm.js").exists()
    assert (out / "index.html").exists()
    html = (out / "index.html").read_text()
    if backend == "mlir":
        assert "MLIR" in html
    else:
        assert "C" in html


@pytest.mark.skipif(not HELLO.exists(), reason="hello_wasm.flow missing")
@pytest.mark.skipif(not _emcc_ok(), reason="emcc not usable")
@pytest.mark.parametrize("backend", ["c", "mlir"])
def test_wasm_build_preload_emits_data(backend: str, tmp_path: Path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import wasm_build as wb  # type: ignore

    data_dir = tmp_path / "pack"
    data_dir.mkdir()
    (data_dir / "note.txt").write_text("hello from preload\n")
    out = tmp_path / f"out-{backend}"
    result = wb.build(
        HELLO,
        out,
        backend=backend,
        opt="-O1",
        timeout=180,
        preload=[f"{data_dir}@/data"],
        extra_link=[ROOT / "runtime" / "flow_rt_support.c"],
        initial_memory="32MB",
    )
    assert result["backend"] == backend
    assert (out / "hello_wasm.wasm").exists()
    assert (out / "hello_wasm.data").exists()
    assert result.get("data_bytes", 0) > 0
