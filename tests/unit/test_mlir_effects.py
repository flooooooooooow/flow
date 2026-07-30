"""MLIR effects parity tests.

Effect, capability, and handle programs must execute correctly through the
MLIR pipeline, matching the C backend semantics:

- per effect: one current-handler pointer global plus NULL-checked dispatch
  functions returning zeroed defaults when unhandled;
- per capability: plain functions plus one vtable global per handled effect;
- handle blocks save, install, and restore the current handler pointer;
- effect calls lexically inside a handle block whose capability implements
  the operation compile to direct calls (zero-cost substitution), while
  calls in other functions go through the dispatch function.

IR-shape tests always run; end-to-end JIT tests run only when the
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


CLOCK_PROGRAM = """
effect Clock {
    now() -> i32,
}

capability WallClock {
    effect Clock,
    function now() -> i32 {
        return 1721224800
    },
}

function read_clock() -> i32 {
    return Clock.now()
}

function main() -> i32 {
    let bare: i32 = read_clock()
    if bare != 0 { return 1 }
    let mut inside: i32 = 0
    let mut direct: i32 = 0
    handle Clock with WallClock {
        inside = read_clock()
        direct = Clock.now()
    }
    if inside != 1721224800 { return 2 }
    if direct != 1721224800 { return 3 }
    let after: i32 = read_clock()
    if after != 0 { return 4 }
    return 0
}
"""

MULTI_EFFECT_PROGRAM = """
effect Inventory {
    stock_of(sku: i32) -> i32,
    reserve(sku: i32, qty: i32) -> i32,
}

effect Notify {
    send(recipient: string, msg: string) -> void,
}

capability TestBackend {
    effect Inventory, Notify,
    function stock_of(sku: i32) -> i32 {
        return 99
    },
    function reserve(sku: i32, qty: i32) -> i32 {
        return 42
    },
    function send(recipient: string, msg: string) -> void {
    },
}

function place_order(sku: i32, qty: i32) -> i32 {
    let available: i32 = Inventory.stock_of(sku)
    if available < qty {
        Notify.send("ops@example.com", "restock")
        return -1
    }
    return Inventory.reserve(sku, qty)
}

function main() -> i32 {
    let bare: i32 = place_order(1001, 2)
    if bare != -1 { return 1 }
    let mut mocked: i32 = 0
    handle Inventory, Notify with TestBackend {
        mocked = place_order(1001, 2)
    }
    if mocked != 42 { return 2 }
    return 0
}
"""

PARTIAL_CAPABILITY_PROGRAM = """
effect Store {
    get(k: i32) -> i32,
    put(k: i32, v: i32) -> i32,
}

capability GetOnly {
    effect Store,
    function get(k: i32) -> i32 {
        return k + 10
    },
}

function main() -> i32 {
    let mut got: i32 = 0
    let mut put_result: i32 = 0
    handle Store with GetOnly {
        got = Store.get(5)
        put_result = Store.put(1, 2)
    }
    if got != 15 { return 1 }
    if put_result != 0 { return 2 }
    return 0
}
"""


def _generate(source: str) -> str:
    ast = parse_flow_code(source)
    generator = MLIRGenerator()
    return generator.generate_module(ast)


class TestEffectRuntimeIRShape:
    def test_current_handler_global_emitted(self):
        mlir = _generate(CLOCK_PROGRAM)
        assert "llvm.mlir.global internal @_current_Clock_handler" in mlir

    def test_vtable_global_emitted(self):
        mlir = _generate(CLOCK_PROGRAM)
        assert "llvm.mlir.global internal @_WallClock_Clock_vtable" in mlir
        assert "!llvm.array<1 x ptr>" in mlir

    def test_dispatch_function_emitted_with_null_check(self):
        mlir = _generate(CLOCK_PROGRAM)
        assert "func.func @Clock_now" in mlir
        assert 'llvm.icmp "ne"' in mlir

    def test_dispatch_uses_indirect_call(self):
        mlir = _generate(CLOCK_PROGRAM)
        indirect = [
            l for l in mlir.splitlines() if "llvm.call %" in l and "!llvm.ptr," in l
        ]
        assert indirect, "dispatch must perform an indirect call via the vtable slot"

    def test_capability_method_emitted_as_function(self):
        mlir = _generate(CLOCK_PROGRAM)
        assert "func.func @WallClock_now" in mlir

    def test_init_function_fills_vtable(self):
        mlir = _generate(CLOCK_PROGRAM)
        assert "func.func @_flow_effects_init" in mlir
        assert "func.constant @WallClock_now" in mlir

    def test_main_calls_init_first(self):
        mlir = _generate(CLOCK_PROGRAM)
        assert "func.call @_flow_effects_init() : () -> ()" in mlir


class TestDevirtualizationIRShape:
    def test_direct_call_inside_handle_block(self):
        """Effect calls lexically inside handle Clock with WallClock are
        devirtualized to the capability function."""
        mlir = _generate(CLOCK_PROGRAM)
        assert "func.call @WallClock_now() : () -> i32" in mlir

    def test_dynamic_dispatch_outside_handle_block(self):
        """read_clock is defined outside any handle block, so its effect call
        must go through the dispatch function."""
        mlir = _generate(CLOCK_PROGRAM)
        assert "func.call @Clock_now() : () -> i32" in mlir

    def test_handle_block_saves_installs_and_restores(self):
        mlir = _generate(CLOCK_PROGRAM)
        lines = mlir.splitlines()
        installs = [
            l for l in lines if "llvm.mlir.addressof @_WallClock_Clock_vtable" in l
        ]
        handler_stores = [
            l
            for l in lines
            if "llvm.store" in l and l.strip().endswith(": !llvm.ptr, !llvm.ptr")
        ]
        assert installs
        # install in handle prologue + restore in epilogue + init stores
        assert len(handler_stores) >= 2

    def test_multi_effect_capability_gets_one_vtable_per_effect(self):
        mlir = _generate(MULTI_EFFECT_PROGRAM)
        assert "@_TestBackend_Inventory_vtable" in mlir
        assert "@_TestBackend_Notify_vtable" in mlir

    def test_unimplemented_operation_dispatches_dynamically(self):
        """GetOnly does not implement put, so even inside the handle block the
        put call must go through dispatch, while get is devirtualized."""
        mlir = _generate(PARTIAL_CAPABILITY_PROGRAM)
        assert "func.call @GetOnly_get" in mlir
        assert "func.call @Store_put" in mlir
        assert "func.call @GetOnly_put" not in mlir


class TestEffectJITExecution:
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
    def test_handle_install_restore_and_defaults(self):
        assert self._run_source(CLOCK_PROGRAM) == 0

    @needs_toolchain
    def test_multi_effect_capability_and_string_args(self):
        assert self._run_source(MULTI_EFFECT_PROGRAM) == 0

    @needs_toolchain
    def test_partial_capability_falls_back_to_default(self):
        assert self._run_source(PARTIAL_CAPABILITY_PROGRAM) == 0

    @needs_toolchain
    def test_effects_showcase_runtime_suite_passes(self):
        path = REPO_ROOT / "tests" / "runtime" / "test_effects_showcase.flow"
        assert path.exists()
        assert self._run_file(path) == 0

    @needs_toolchain
    def test_legacy_effects_runtime_suite_passes(self):
        path = REPO_ROOT / "tests" / "runtime" / "test_effects.flow"
        assert path.exists()
        assert self._run_file(path) == 0
