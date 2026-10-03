import pytest
from flow.mlir_optimizer import MLIROptimizer

class TestMLIROptimizer:
    def test_pipeline_without_pipelining(self):
        pipeline = MLIROptimizer.build_pass_pipeline(
            optimization_level="O3",
            enable_loop_pipelining=False,
            enable_multi_buffering=False
        )
        assert "test-scf-pipelining" not in pipeline
        assert "test-multi-buffering" not in pipeline

    def test_pipeline_with_pipelining(self):
        pipeline = MLIROptimizer.build_pass_pipeline(
            optimization_level="O3",
            enable_loop_pipelining=True,
            enable_multi_buffering=True
        )
        assert "test-scf-pipelining" in pipeline
        assert "test-multi-buffering{multiplier=2}" in pipeline

    def test_pipeline_with_pipelining_o1(self):
        # pipelining requires O2+
        pipeline = MLIROptimizer.build_pass_pipeline(
            optimization_level="O1",
            enable_loop_pipelining=True,
            enable_multi_buffering=True
        )
        assert "test-scf-pipelining" not in pipeline
        assert "test-multi-buffering{multiplier=2}" not in pipeline
