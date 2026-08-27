"""MLIR regressions for unified postfix-chaining AST shapes.

The C backend already covers ptr[0].field / f().x / array[i].field (see
test_postfix_chaining.py). These tests exercise the same shapes through the
MLIR generator: IR shape always, mlir-opt acceptance when available.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code
from flow.mlir_generator import MLIRGenerator
from flow.mlir_jit import MLIRJIT


def _mlir_opt_path() -> Optional[str]:
    jit = MLIRJIT()
    return jit._find_mlir_opt()


MLIR_OPT = _mlir_opt_path()
needs_mlir_opt = pytest.mark.skipif(
    MLIR_OPT is None, reason="mlir-opt not available"
)


POINTER_STRUCT_PROGRAM = """
extern {
    function malloc(size: i64) -> ptr<Body>
    function free(p: ptr<Body>)
}

struct Vec2 {
    x: f32,
    y: f32
}

struct Body {
    pos: Vec2,
    mass: f32,
    id: i32
}

function get_mass(b: Body) -> f32 {
    return b.mass
}

function main() -> i32 {
    let bodies: ptr<Body> = malloc(64)
    bodies[0].id = 1
    bodies[0].mass = 2.5
    bodies[0].pos.x = 1.5
    bodies[0].pos.y = 0.5
    bodies[1].id = 2
    bodies[1].mass = 4.0
    let total: f32 = bodies[0].mass + bodies[1].mass + bodies[0].pos.x + bodies[0].pos.y
    let m: f32 = bodies[0].get_mass()
    free(bodies)
    if total == 8.5 {
        if m == 2.5 {
            return 0
        }
    }
    return 1
}
"""

ARRAY_OF_STRUCTS_PROGRAM = """
struct Note {
    pitch: i32,
    duration: i32
}

function main() -> i32 {
    let melody: array<Note, 4> = [
        Note { pitch: 60, duration: 1 },
        Note { pitch: 62, duration: 2 },
        Note { pitch: 64, duration: 3 },
        Note { pitch: 65, duration: 4 }
    ]
    let mut total: i32 = 0
    for i in 0 to 4 {
        total = total + melody[i].duration
    }
    if total == 10 {
        return 0
    }
    return 1
}
"""

CALL_THEN_FIELD_PROGRAM = """
struct Point {
    x: i32,
    y: i32
}

function make() -> Point {
    return Point { x: 3, y: 4 }
}

function main() -> i32 {
    let a: i32 = make().x
    let b: i32 = make().y
    if a == 3 {
        if b == 4 {
            return 0
        }
    }
    return 1
}
"""

NESTED_FIELD_PROGRAM = """
struct Inner {
    value: i32
}

struct Outer {
    inner: Inner,
    count: i32
}

function main() -> i32 {
    let o: Outer = Outer { inner: Inner { value: 42 }, count: 1 }
    if o.inner.value == 42 {
        return 0
    }
    return 1
}
"""

INLINE_STRUCT_ARRAY_LITERAL_PROGRAM = """
struct Slot {
    active: bool,
    note: f32
}

struct Pool {
    count: i32,
    slots: array<Slot, 2>
}

function make_pool() -> Pool {
    let slots: array<Slot, 2> = []
    return Pool { count: 0, slots: slots }
}

function main() -> i32 {
    let pool: Pool = make_pool()
    if pool.count == 0 { return 0 }
    return 1
}
"""


def _generate(source: str) -> str:
    return MLIRGenerator().generate_module(parse_flow_code(source))


class TestChainedPointerStructIR:
    """ptr[i].field reads/writes and nested ptr[i].pos.x stores."""

    def test_no_unsupported_assignment_targets(self):
        mlir = _generate(POINTER_STRUCT_PROGRAM)
        assert "Unsupported assignment target" not in mlir

    def test_index_field_store_uses_gep_store(self):
        mlir = _generate(POINTER_STRUCT_PROGRAM)
        assert "llvm.getelementptr" in mlir
        assert "llvm.store" in mlir
        # Element GEP then field GEP for bodies[0].id (field index 2)
        assert "llvm.getelementptr" in mlir and "[0, 2]" in mlir

    def test_nested_field_store_chains_geps(self):
        """bodies[0].pos.x lowers to element GEP -> pos GEP -> x GEP -> store."""
        mlir = _generate(POINTER_STRUCT_PROGRAM)
        assert "!llvm.struct<(f32, f32)>" in mlir
        store_lines = [l for l in mlir.splitlines() if "llvm.store" in l and "f32" in l]
        assert store_lines

    def test_index_field_read_extracts_field(self):
        mlir = _generate(POINTER_STRUCT_PROGRAM)
        assert "llvm.extractvalue" in mlir
        assert "arith.addf" in mlir
        assert "arith.addi" not in mlir

    def test_index_method_call_desugars(self):
        mlir = _generate(POINTER_STRUCT_PROGRAM)
        assert "func.call @get_mass" in mlir


class TestChainedArrayOfStructsIR:
    def test_element_field_load_uses_llvm_array(self):
        """Struct arrays lower via !llvm.array alloca (memref cannot hold structs)."""
        mlir = _generate(ARRAY_OF_STRUCTS_PROGRAM)
        assert "!llvm.array<4 x !llvm.struct<(i32, i32)>>" in mlir
        assert "llvm.alloca" in mlir
        load_lines = [l for l in mlir.splitlines() if "llvm.load" in l and "!llvm.struct" in l]
        assert load_lines
        assert "memref<?xf32>" not in mlir

    def test_element_field_loads_duration_via_gep(self):
        """Memory-resident struct fields use GEP+load (not extractvalue)."""
        mlir = _generate(ARRAY_OF_STRUCTS_PROGRAM)
        assert "llvm.getelementptr" in mlir
        assert any(
            "getelementptr" in ln and "[0, 1]" in ln for ln in mlir.splitlines()
        ), mlir  # duration is field 1
        assert "llvm.load" in mlir



class TestChainedCallFieldIR:
    def test_call_then_field_extracts(self):
        mlir = _generate(CALL_THEN_FIELD_PROGRAM)
        assert "Unsupported" not in mlir
        assert "func.call @make" in mlir
        assert "llvm.extractvalue" in mlir
        # Must not fall back to a zero constant for .x
        main = mlir.split("func.func @main")[1]
        # After materializing the call result, .x / .y must be extractvalue
        assert main.count("llvm.extractvalue") >= 2


class TestChainedNestedFieldIR:
    def test_nested_value_field_loads_via_gep(self):
        mlir = _generate(NESTED_FIELD_PROGRAM)
        assert "Unsupported" not in mlir
        # Nested field read: GEP into outer, then GEP/load of inner field 0.
        gep_lines = [ln for ln in mlir.splitlines() if "llvm.getelementptr" in ln]
        assert any("[0, 0]" in ln for ln in gep_lines), mlir
        assert "llvm.load" in mlir


class TestInlineStructArrayLiteralIR:
    def test_struct_array_field_uses_inline_array_value(self):
        mlir = _generate(INLINE_STRUCT_ARRAY_LITERAL_PROGRAM)
        assert "llvm.insertvalue" in mlir
        assert "!llvm.array<2 x !llvm.struct<(i1, f32)>>" in mlir
        # The inline field must be an array aggregate, never a pointer cast.
        assert "llvm.inttoptr" not in mlir.split("func.func @make_pool", 1)[1].split("}", 1)[0]

    @needs_mlir_opt
    def test_struct_array_field_is_accepted_by_mlir_opt(self):
        mlir = _generate(INLINE_STRUCT_ARRAY_LITERAL_PROGRAM)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mlir", delete=False) as f:
            f.write(mlir)
            path = f.name
        try:
            result = subprocess.run(
                [MLIR_OPT, path, "-o", os.devnull],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, result.stderr
        finally:
            Path(path).unlink(missing_ok=True)


class TestChainedASTMlirOpt:
    """Generated IR for chained shapes must be accepted by mlir-opt."""

    def _opt_accepts(self, source: str) -> None:
        mlir = _generate(source)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".mlir", delete=False
        ) as f:
            f.write(mlir)
            path = f.name
        try:
            result = subprocess.run(
                [MLIR_OPT, path, "-o", os.devnull],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, result.stderr
        finally:
            Path(path).unlink(missing_ok=True)

    @needs_mlir_opt
    def test_pointer_struct_chain_opt(self):
        self._opt_accepts(POINTER_STRUCT_PROGRAM)

    @needs_mlir_opt
    def test_array_of_structs_chain_opt(self):
        self._opt_accepts(ARRAY_OF_STRUCTS_PROGRAM)

    @needs_mlir_opt
    def test_call_then_field_opt(self):
        self._opt_accepts(CALL_THEN_FIELD_PROGRAM)

    @needs_mlir_opt
    def test_nested_field_opt(self):
        self._opt_accepts(NESTED_FIELD_PROGRAM)
