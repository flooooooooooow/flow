"""
Unit tests for MLIROptimizer pass-pipeline construction.

These assert on pipeline strings from build_pass_pipeline() and do not
require mlir-opt to be installed.
"""

from flow.mlir_optimizer import MLIROptimizer


def _names(**kwargs):
    pipeline = MLIROptimizer.build_pass_pipeline(**kwargs)
    return MLIROptimizer.pipeline_pass_names(pipeline), pipeline


class TestMLIROptimizerPassPipeline:
    """Pass list / pipeline string assertions."""

    def test_o2_enable_sccp_includes_sccp(self):
        names, pipeline = _names(optimization_level="O2", enable_sccp=True)
        assert "sccp" in names
        assert "sccp" in pipeline

    def test_o2_disable_sccp_omits_sccp(self):
        names, _ = _names(optimization_level="O2", enable_sccp=False)
        assert "sccp" not in names

    def test_enable_dce_adds_symbol_dce(self):
        names, pipeline = _names(optimization_level="O2", enable_dce=True)
        assert "symbol-dce" in names
        assert "symbol-dce" in pipeline
        # canonicalize round after DCE
        assert names.count("canonicalize") >= 2

    def test_disable_dce_omits_symbol_dce(self):
        names, _ = _names(optimization_level="O2", enable_dce=False)
        assert "symbol-dce" not in names

    def test_enable_inline_adds_inline_at_o2(self):
        names, pipeline = _names(optimization_level="O2", enable_inline=True)
        assert "inline" in names
        assert "inline" in pipeline

    def test_inline_default_true_at_o2(self):
        # enable_inline defaults True; O2+ should include the inliner
        names, _ = _names(optimization_level="O2")
        assert "inline" in names

    def test_inline_not_at_o1(self):
        names, _ = _names(optimization_level="O1", enable_inline=True)
        assert "inline" not in names

    def test_disable_inline_omits_inline(self):
        names, _ = _names(optimization_level="O2", enable_inline=False)
        assert "inline" not in names

    def test_vectorize_gated_o3_only(self):
        names_o2, _ = _names(optimization_level="O2", enable_vectorization=True)
        assert "affine-super-vectorize" not in names_o2

        names_o3, pipeline_o3 = _names(
            optimization_level="O3", enable_vectorization=True
        )
        assert "affine-super-vectorize" in names_o3
        assert "affine-super-vectorize" in pipeline_o3

        names_off, _ = _names(optimization_level="O3", enable_vectorization=False)
        assert "affine-super-vectorize" not in names_off

    def test_loop_fusion_gated_by_flag_and_o2(self):
        names, _ = _names(optimization_level="O2", enable_loop_fusion=True)
        assert "affine-loop-fusion" in names

        names_off, _ = _names(optimization_level="O2", enable_loop_fusion=False)
        assert "affine-loop-fusion" not in names_off

        names_o1, _ = _names(optimization_level="O1", enable_loop_fusion=True)
        assert "affine-loop-fusion" not in names_o1

    def test_mem2reg_licm_gvn_wired(self):
        names, _ = _names(
            optimization_level="O2",
            enable_mem2reg=True,
            enable_licm=True,
            enable_gvn=True,
        )
        assert "mem2reg" in names
        assert "loop-invariant-code-motion" in names
        assert "cse" in names  # gvn → cse stand-in

        names_off, _ = _names(
            optimization_level="O2",
            enable_mem2reg=False,
            enable_licm=False,
            enable_gvn=False,
        )
        assert "mem2reg" not in names_off
        assert "loop-invariant-code-motion" not in names_off
        assert "cse" not in names_off

    def test_o0_empty_module_pipeline(self):
        pipeline = MLIROptimizer.build_pass_pipeline(optimization_level="O0")
        assert pipeline == "builtin.module()"

    def test_pipeline_nests_func_and_module_passes(self):
        pipeline = MLIROptimizer.build_pass_pipeline(optimization_level="O2")
        assert pipeline.startswith("builtin.module(")
        assert "func.func(" in pipeline
        # module-level passes sit outside func.func
        assert "inline," in pipeline or pipeline.startswith("builtin.module(inline,")
        assert "symbol-dce" in pipeline
