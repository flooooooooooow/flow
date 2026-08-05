"""MLIR struct parity tests.

Struct programs must execute correctly through the MLIR pipeline, matching
the C backend semantics. Covers struct literals, field reads, field stores,
address-of, and pointer-to-struct parameters (the shapes flow blocks lower
to). IR-shape tests always run; end-to-end JIT tests run only when the
mlir-opt / mlir-translate / clang toolchain is available.
"""

import shutil
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code
from flow.mlir_generator import MLIRGenerator
from flow.mlir_jit import MLIRJIT
from flow.jit_runner import compile_flow_to_mlir


REPO_ROOT = Path(__file__).parent.parent.parent


def _toolchain_available() -> bool:
    jit = MLIRJIT()
    return (
        jit._find_mlir_opt() is not None
        and jit._find_mlir_translate() is not None
        and shutil.which("clang") is not None
    )


TOOLCHAIN = _toolchain_available()
needs_toolchain = pytest.mark.skipif(
    not TOOLCHAIN, reason="mlir-opt/mlir-translate/clang not available"
)


STRUCT_LITERAL_PROGRAM = """
struct Point { x: f64, y: f64 }
function main() -> i32 {
    let p: Point = Point { x: 1.0, y: 2.0 }
    let s: f64 = p.x + p.y
    if s > 2.5 { return 0 }
    return 1
}
"""

FLOW_BLOCK_PROGRAM = """
flow Decay {
    state level : f64 = 8.0
    param rate  : f64 = 1.0
    level evolves as -(rate * level)
}

function main() -> i32 {
    let mut d: Decay = Decay_new()
    let start: f64 = d.level
    for k in 0 to 2000 {
        Decay_step(&d, 0.001)
    }
    if start < 7.9 { return 1 }
    if d.level > start { return 2 }
    if d.level < 0.0 { return 3 }
    if d.level > 1.2 { return 4 }
    return 0
}
"""


def _generate(source: str) -> str:
    ast = parse_flow_code(source)
    generator = MLIRGenerator()
    return generator.generate_module(ast)


class TestStructIRShape:
    def test_struct_literal_emits_insertvalue(self):
        mlir = _generate(STRUCT_LITERAL_PROGRAM)
        assert "llvm.mlir.undef : !llvm.struct<(f64, f64)>" in mlir
        assert "llvm.insertvalue" in mlir

    def test_field_access_emits_load_or_extract(self):
        """Field reads may use extractvalue (by-value) or GEP+load (addressable)."""
        mlir = _generate(STRUCT_LITERAL_PROGRAM)
        assert "llvm.extractvalue" in mlir or (
            "llvm.getelementptr" in mlir and "llvm.load" in mlir
        )

    def test_field_add_uses_float_arith(self):
        """p.x + p.y on f64 fields must lower to addf, never addi."""
        mlir = _generate(STRUCT_LITERAL_PROGRAM)
        assert "arith.addf" in mlir
        assert "arith.addi" not in mlir

    def test_field_compare_uses_float_compare(self):
        mlir = _generate(STRUCT_LITERAL_PROGRAM)
        assert "arith.cmpf ogt" in mlir


class TestPointerStructIRShape:
    """flow blocks lower to Name_init/derivs/step taking Name* self."""

    def test_no_unsupported_placeholders(self):
        mlir = _generate(FLOW_BLOCK_PROGRAM)
        assert "Unsupported unary operator" not in mlir
        assert "Unsupported assignment target" not in mlir

    def test_field_read_through_pointer_uses_gep_load(self):
        mlir = _generate(FLOW_BLOCK_PROGRAM)
        assert "llvm.getelementptr %arg0[0, 0]" in mlir
        assert "llvm.load" in mlir

    def test_field_store_through_pointer_uses_gep_store(self):
        mlir = _generate(FLOW_BLOCK_PROGRAM)
        gep_lines = [l for l in mlir.splitlines() if "llvm.getelementptr" in l]
        store_lines = [l for l in mlir.splitlines() if "llvm.store" in l]
        assert gep_lines
        assert store_lines

    def test_address_of_local_produces_pointer_argument(self):
        """&d in main must pass an !llvm.ptr, not a comment placeholder."""
        mlir = _generate(FLOW_BLOCK_PROGRAM)
        call_lines = [l for l in mlir.splitlines() if "func.call @Decay_step" in l]
        assert call_lines
        for line in call_lines:
            assert "//" not in line
            assert "(!llvm.ptr, f64)" in line


class TestStructJITExecution:
    """End-to-end: FLOW -> MLIR -> mlir-opt -> mlir-translate -> clang -> run."""

    def _run_source(self, source: str) -> int:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".flow", delete=False
        ) as f:
            f.write(source)
            flow_file = f.name
        try:
            mlir_code = compile_flow_to_mlir(flow_file)
            jit = MLIRJIT()
            try:
                result = jit.jit_compile_and_run(mlir_code, "main")
            finally:
                jit.cleanup()
            assert result is not None, "JIT pipeline failed to produce a result"
            return result
        finally:
            Path(flow_file).unlink(missing_ok=True)

    def _run_file(self, path: Path) -> int:
        mlir_code = compile_flow_to_mlir(str(path))
        jit = MLIRJIT()
        try:
            result = jit.jit_compile_and_run(mlir_code, "main")
        finally:
            jit.cleanup()
        assert result is not None, "JIT pipeline failed to produce a result"
        return result

    @needs_toolchain
    def test_struct_literal_field_math_exits_zero(self):
        assert self._run_source(STRUCT_LITERAL_PROGRAM) == 0

    @needs_toolchain
    def test_flow_block_struct_mutation_exits_zero(self):
        assert self._run_source(FLOW_BLOCK_PROGRAM) == 0

    @needs_toolchain
    def test_evolves_pendulum_matches_c_semantics(self):
        """Numerically self-checking against the hand-integrated trajectory."""
        path = REPO_ROOT / "tests" / "core" / "test_evolves_pendulum.flow"
        assert path.exists()
        assert self._run_file(path) == 0

    @needs_toolchain
    def test_plain_program_still_works(self):
        source = """
        function main() -> i32 {
            let mut acc: i32 = 0
            for i in 0..10 {
                acc = acc + i
            }
            if acc == 45 { return 0 }
            return 1
        }
        """
        assert self._run_source(source) == 0
