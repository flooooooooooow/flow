"""Spans and complex numbers on the MLIR backend.

The backend refused both until now, which meant every real program went through C.
These pin the representations down, because the point of matching the C backend's
layout is that a value can cross between the two unchanged, and a layout is only
matched if something checks.
"""

import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from flow.mlir_generator import MLIRGenerator  # noqa: E402
from flow.parser import Lexer, Parser, Type  # noqa: E402

HAVE_MLIR = shutil.which("mlir-opt") or Path("/opt/homebrew/opt/llvm/bin/mlir-opt").exists()


def emit(source: str, tmp_path: Path, env_extra=None) -> str:
    path = tmp_path / "case.flow"
    path.write_text(source)
    out = tmp_path / "case.mlir"
    env = {"PYTHONPATH": str(SRC), "PATH": os.environ.get("PATH", "/usr/bin:/bin")}
    env.update(env_extra or {})
    done = subprocess.run(
        [sys.executable, "-m", "flow.transpiler", str(path), "--mlir", "--lenient",
         "-o", str(out)],
        capture_output=True, text=True, env=env,
    )
    assert out.exists(), done.stdout + done.stderr
    return out.read_text()


def body_of(mlir: str, name: str) -> str:
    marker = f"func.func @{name}"
    assert marker in mlir, f"no {name} in generated MLIR"
    rest = mlir[mlir.index(marker):]
    return rest[:rest.index("\n  }")]


# --- representations ----------------------------------------------------------------

def test_span_is_the_same_pair_the_c_backend_emits():
    """`{T *data; int64_t len;}`. If this drifts, the two backends stop agreeing."""
    g = MLIRGenerator()
    assert g.flow_type_to_mlir(Type(name="span_const_f64",
                                    element_type=Type(name="f64"))) == "!llvm.struct<(ptr, i64)>"
    assert g.flow_type_to_mlir(Type(name="span_mut_c64",
                                    element_type=Type(name="c64"))) == "!llvm.struct<(ptr, i64)>"


def test_complex_maps_to_the_complex_dialect():
    g = MLIRGenerator()
    assert g.flow_type_to_mlir(Type(name="c64")) == "complex<f32>"
    assert g.flow_type_to_mlir(Type(name="c128")) == "complex<f64>"


def test_complex_storage_is_two_reals():
    """A pointer to one has to be what cblas expects."""
    g = MLIRGenerator()
    assert g._complex_storage_mlir("complex<f32>") == "!llvm.struct<(f32, f32)>"
    assert g._complex_storage_mlir("complex<f64>") == "!llvm.struct<(f64, f64)>"


def test_float_literals_carry_a_point():
    """MLIR rejects `arith.constant 0 : f32`, and the formatter could produce it."""
    g = MLIRGenerator()
    assert g._format_mlir_numeric("0", "f32") == "0.0"
    # `1e0` formats and strips to `1`, which MLIR will not take for an f64.
    for text in ("0", "1e0", "3", "2.5e3"):
        emitted = g._format_mlir_numeric(text, "f64")
        assert "." in emitted or "e" in emitted.lower(), f"{text!r} became {emitted!r}"
    assert g._format_mlir_numeric("0", "i32") == "0"       # integers are left alone


# --- generated code -----------------------------------------------------------------

SPAN_SOURCE = textwrap.dedent("""
    extern { function malloc(size: i64) -> ptr<f64> }
    function total(xs: span<f64>) -> f64 {
        let mut t: f64 = 0.0
        for i in 0 to xs.len { t = t + xs[i] }
        return t
    }
    function at(xs: span<f64>, i: i32) -> f64 { return xs[i] }
    function main() -> i32 { return 0 }
""")


def test_span_length_is_read_off_the_pair(tmp_path):
    body = body_of(emit(SPAN_SOURCE, tmp_path), "total")
    assert "llvm.extractvalue" in body
    assert "llvm.getelementptr" in body


def test_a_proved_access_gets_no_assert(tmp_path):
    """`for i in 0 to xs.len` is provable, so the check must not be emitted."""
    body = body_of(emit(SPAN_SOURCE, tmp_path), "total")
    assert "cf.assert" not in body


def test_an_unprovable_access_keeps_its_assert(tmp_path):
    body = body_of(emit(SPAN_SOURCE, tmp_path), "at")
    assert "cf.assert" in body
    # unsigned, so a negative index fails the same test
    assert "arith.cmpi ult" in body


def test_the_prover_can_be_turned_off_here_too(tmp_path):
    body = body_of(emit(SPAN_SOURCE, tmp_path, {"FLOW_NO_BOUNDS_PROOF": "1"}), "total")
    assert "cf.assert" in body


COMPLEX_SOURCE = textwrap.dedent("""
    extern {
        function malloc(size: i64) -> ptr<c64>
        function crealf(z: c64) -> f32
    }
    function product(a: c64, b: c64) -> c64 { return a * b }
    function store_it(buf: ptr<c64>, z: c64) -> f32 {
        buf[0] = z
        return crealf(buf[0])
    }
    function main() -> i32 { return 0 }
""")


def test_complex_multiply_uses_the_dialect(tmp_path):
    body = body_of(emit(COMPLEX_SOURCE, tmp_path), "product")
    assert "complex.mul" in body


def test_complex_accessors_are_not_c_calls(tmp_path):
    """Passing a complex by value across an ABI boundary is avoided entirely."""
    body = body_of(emit(COMPLEX_SOURCE, tmp_path), "store_it")
    assert "complex.re" in body
    assert "@crealf" not in body


def test_complex_reaches_memory_as_two_reals(tmp_path):
    body = body_of(emit(COMPLEX_SOURCE, tmp_path), "store_it")
    stores = [line.strip() for line in body.splitlines() if "llvm.store" in line]
    assert stores, "nothing was stored"
    # every one goes through the pair; llvm.store has no size for complex<f32>
    for line in stores:
        assert "complex<" not in line, line
        assert "!llvm.struct<(f32, f32)>" in line, line
    loads = [line.strip() for line in body.splitlines() if "llvm.load" in line]
    for line in loads:
        assert "complex<" not in line, line


# --- end to end ---------------------------------------------------------------------

@pytest.mark.skipif(not HAVE_MLIR, reason="mlir-opt not installed")
def test_the_pipeline_lowers_complex(tmp_path):
    """The lowering had no pass for the complex dialect, so this got as far as text."""
    mlir = emit(COMPLEX_SOURCE, tmp_path)
    src = tmp_path / "lower.mlir"
    src.write_text(mlir)
    opt = shutil.which("mlir-opt") or "/opt/homebrew/opt/llvm/bin/mlir-opt"
    done = subprocess.run(
        [opt, "--convert-scf-to-cf", "--convert-complex-to-standard",
         "--convert-complex-to-llvm", "--convert-math-to-llvm",
         "--convert-arith-to-llvm", "--convert-cf-to-llvm", "--convert-func-to-llvm",
         "--reconcile-unrealized-casts", str(src)],
        capture_output=True, text=True,
    )
    assert done.returncode == 0, done.stderr
    assert "complex." not in done.stdout, "complex dialect survived lowering"
