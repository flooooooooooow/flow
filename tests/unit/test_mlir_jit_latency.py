import time
import pytest
from flow.mlir_jit import MLIRJIT


def test_tool_resolution_caching():
    """Verify tool location resolution is cached across calls."""
    opt1 = MLIRJIT._find_mlir_opt()
    opt2 = MLIRJIT._find_mlir_opt()
    assert opt1 == opt2

    trans1 = MLIRJIT._find_mlir_translate()
    trans2 = MLIRJIT._find_mlir_translate()
    assert trans1 == trans2


def test_in_memory_pipelining():
    """Verify in-memory MLIR lowering produces valid LLVM IR without intermediate files."""
    mlir_code = """
module {
  func.func @main() -> i32 {
    %0 = arith.constant 123 : i32
    func.return %0 : i32
  }
}
"""
    jit = MLIRJIT()
    llvm_ir = jit.compile_mlir_to_llvm(mlir_code)
    assert llvm_ir != ""
    assert "define" in llvm_ir or "declare" in llvm_ir or "@main" in llvm_ir or "123" in llvm_ir


def test_jit_binary_caching_and_latency():
    """Verify second invocation reuses cached executable and reduces latency."""
    mlir_code = """
module {
  func.func @main() -> i32 {
    %0 = arith.constant 77 : i32
    func.return %0 : i32
  }
}
"""
    jit = MLIRJIT()
    res1 = jit.jit_compile_and_run(mlir_code)
    assert res1 == 77

    t0 = time.perf_counter()
    res2 = jit.jit_compile_and_run(mlir_code)
    t1 = time.perf_counter()
    assert res2 == 77

    # Cached execution time should be under 250ms (usually ~80ms)
    cached_duration = t1 - t0
    assert cached_duration < 0.25, f"Cached execution took too long: {cached_duration:.4f}s"
