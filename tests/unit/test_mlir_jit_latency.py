import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from flow.mlir_jit import MLIRJIT, JITPhaseTimings
from flow.cost_model import estimate_backend, should_optimize_mlir_workload

def test_jit_phase_timings_structure():
    timings = JITPhaseTimings()
    assert timings.gen_time_ms == 0.0
    assert timings.opt_time_ms == 0.0
    assert timings.lowering_time_ms == 0.0
    assert timings.codegen_link_time_ms == 0.0
    assert timings.cache_lookup_time_ms == 0.0
    assert timings.cold_first_result is True
    assert timings.warm_cache is False

    d = timings.to_dict()
    assert "lowering_time_ms" in d
    assert "codegen_link_time_ms" in d
    assert "cold_first_result" in d

def test_specialization_cache_hit_and_timing_separation(tmp_path):
    jit = MLIRJIT()
    mlir_code = """
module {
  func.func @main() -> i32 {
    %0 = arith.constant 42 : i32
    func.return %0 : i32
  }
}
"""
    mock_exe = tmp_path / "mock_bin"
    mock_exe.write_text("#!/bin/sh\nexit 0")
    mock_exe.chmod(0o755)

    with patch.object(jit, 'compile_mlir_to_llvm', return_value="define i32 @main() { ret i32 0 }"), \
         patch.object(jit, 'compile_llvm_to_executable', return_value=mock_exe), \
         patch.object(jit, '_run_native_executable', return_value=0):

        # Cold run
        res1 = jit.jit_compile_and_run(mlir_code, "main")
        assert res1 == 0
        t1 = jit.last_timings
        assert t1 is not None
        assert t1.cold_first_result is True
        assert t1.warm_cache is False

        # Warm run (cached)
        res2 = jit.jit_compile_and_run(mlir_code, "main")
        assert res2 == 0
        t2 = jit.last_timings
        assert t2 is not None
        assert t2.warm_cache is True
        assert t2.cold_first_result is False
        assert t2.cache_lookup_time_ms >= 0.0

def test_cost_model_small_workload_bypass():
    assert should_optimize_mlir_workload(100, 1, 5) is False
    assert should_optimize_mlir_workload(50000, 2, 50) is True
