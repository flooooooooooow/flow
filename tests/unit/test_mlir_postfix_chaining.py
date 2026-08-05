"""MLIR parity for postfix-chained AST shapes (#124).

Parser + C backend coverage lives in test_postfix_chaining.py. This module
asserts the MLIR generator lowers the same shapes without unsupported
placeholders, and (when the toolchain is present) that they execute correctly.
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
from tests.unit.test_postfix_chaining import (
    POINTER_STRUCT_PROGRAM,
    ARRAY_OF_STRUCTS_PROGRAM,
)


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


def _generate(source: str) -> str:
    return MLIRGenerator().generate_module(parse_flow_code(source))


class TestMLIRPostfixChainingIR:
    def test_pointer_struct_field_writes_have_no_unsupported(self):
        mlir = _generate(POINTER_STRUCT_PROGRAM)
        assert "Unsupported assignment target" not in mlir
        assert "Unsupported" not in mlir

    def test_pointer_struct_field_writes_use_gep_store(self):
        mlir = _generate(POINTER_STRUCT_PROGRAM)
        assert "llvm.getelementptr" in mlir
        assert "llvm.store" in mlir
        # Nested bodies[0].pos.x needs at least a field GEP into Vec2
        assert "!llvm.struct<(f32, f32)>" in mlir

    def test_pointer_struct_field_reads_use_gep_load(self):
        mlir = _generate(POINTER_STRUCT_PROGRAM)
        assert "llvm.load" in mlir
        # mass is f32 — reads should produce f32 loads, not constant-0 fallbacks
        assert "llvm.load" in mlir and "-> f32" in mlir

    def test_array_of_structs_reads_have_no_unsupported(self):
        mlir = _generate(ARRAY_OF_STRUCTS_PROGRAM)
        assert "Unsupported" not in mlir


class TestMLIRPostfixChainingJIT:
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

    @needs_toolchain
    def test_pointer_struct_chained_fields_exits_zero(self):
        assert self._run_source(POINTER_STRUCT_PROGRAM) == 0

    @needs_toolchain
    def test_array_of_structs_field_reads_exits_zero(self):
        assert self._run_source(ARRAY_OF_STRUCTS_PROGRAM) == 0
