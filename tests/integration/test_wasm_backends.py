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
