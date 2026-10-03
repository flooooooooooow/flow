"""
Unit tests for MLIR vector.outerproduct register tiling, pressure analysis,
and silicon matrix accelerator intrinsics lowering (#666).
"""

from types import SimpleNamespace
from flow.mlir_outerproduct_tile import (
    RegisterPressureAnalyzer,
    OuterProductTiler,
    HardwareMatrixLowering,
    synthesize_gemm_microkernel,
    TARGET_SPECS,
)
from flow.mlir_optimizer import MLIROptimizer
from flow.transpiler import mlir_opt_kwargs_from_args


class TestRegisterPressureAnalyzer:
    """Test register pressure modeling across hardware targets."""

    def test_avx512_budget_within_limits(self):
        analyzer = RegisterPressureAnalyzer("avx512")
        analysis = analyzer.analyze_tile_pressure(tile_m=16, tile_n=4, tile_k=4, dtype="f32")
        assert analysis["is_within_budget"] is True
        assert analysis["spill_risk"] == "none"
        assert analysis["acc_regs"] == 4
        assert analysis["total_vector_regs"] <= 32

    def test_avx512_budget_exceeded_spill_risk(self):
        analyzer = RegisterPressureAnalyzer("avx512")
        # 64x16 tile needs (64/16)*16 = 64 acc registers -> exceeds 32 ZMM registers
        analysis = analyzer.analyze_tile_pressure(tile_m=64, tile_n=16, tile_k=4, dtype="f32")
        assert analysis["is_within_budget"] is False
        assert analysis["spill_risk"] in ("medium", "high")
        rec_m, rec_n, _ = analysis["recommended_tile"]
        assert rec_m * rec_n // 16 <= analyzer.spec.max_accumulator_regs

    def test_arm_neon_budget(self):
        analyzer = RegisterPressureAnalyzer("arm_neon")
        analysis = analyzer.analyze_tile_pressure(tile_m=8, tile_n=4, tile_k=1, dtype="f32")
        assert analysis["target"] == "ARM Neon"
        assert analysis["vector_len"] == 4
        assert analysis["acc_regs"] == 8

    def test_hardware_targets_exist(self):
        for target in ("avx512", "arm_neon", "intel_amx", "arm_sme", "nvvm_tma"):
            analyzer = RegisterPressureAnalyzer(target)
            assert analyzer.spec.name != ""


class TestOuterProductTiler:
    """Test MLIR vector.outerproduct code generation."""

    def test_generate_gemm_tile_contains_outerproduct(self):
        tiler = OuterProductTiler("avx512")
        mlir = tiler.generate_gemm_tile(
            m=128, n=128, k=128,
            tile_m=16, tile_n=4, tile_k=4,
            dtype="f32", function_name="gemm_kernel"
        )
        assert "func.func @gemm_kernel" in mlir
        assert "vector.outerproduct" in mlir
        assert "vector.transfer_read" in mlir
        assert "vector.transfer_write" in mlir
        assert "memref.load" in mlir

    def test_auto_adjusts_oversized_tiles(self):
        tiler = OuterProductTiler("arm_neon")
        # 128x128 tile is way over register budget
        mlir = tiler.generate_gemm_tile(
            m=256, n=256, k=256,
            tile_m=128, tile_n=128, tile_k=4,
            dtype="f32"
        )
        assert "vector.outerproduct" in mlir


class TestHardwareMatrixLowering:
    """Test synthesis of matrix accelerator intrinsics."""

    def test_lower_to_intel_amx(self):
        tiler = OuterProductTiler("intel_amx")
        tiled_ir = tiler.generate_gemm_tile(128, 128, 128, 16, 4, 4)
        lowering = HardwareMatrixLowering("intel_amx")
        amx_ir = lowering.lower_outerproduct_to_accelerator(tiled_ir)
        assert "x86vector.amx.tilezero" in amx_ir
        assert "x86vector.amx.tileloadd" in amx_ir
        assert "x86vector.amx.tdpbf16ps" in amx_ir

    def test_lower_to_arm_sme(self):
        tiler = OuterProductTiler("arm_sme")
        tiled_ir = tiler.generate_gemm_tile(128, 128, 128, 16, 4, 4)
        lowering = HardwareMatrixLowering("arm_sme")
        sme_ir = lowering.lower_outerproduct_to_accelerator(tiled_ir)
        assert "arm_sme.zero" in sme_ir
        assert "arm_sme.mopa" in sme_ir

    def test_lower_to_nvvm_tma(self):
        tiler = OuterProductTiler("nvvm_tma")
        tiled_ir = tiler.generate_gemm_tile(128, 128, 128, 16, 4, 4)
        lowering = HardwareMatrixLowering("nvvm_tma")
        nvvm_ir = lowering.lower_outerproduct_to_accelerator(tiled_ir)
        assert "nvvm.tma.async.load" in nvvm_ir
        assert "nvvm.wgmma.mma_async" in nvvm_ir


class TestMLIROptimizerIntegration:
    """Test MLIROptimizer and CLI flags integration."""

    def test_synthesize_gemm_microkernel_helper(self):
        optimizer = MLIROptimizer()
        kernel_ir = optimizer.synthesize_gemm_microkernel(
            m=64, n=64, k=64,
            tile_m=16, tile_n=4, tile_k=4,
            target_arch="intel_amx"
        )
        assert "x86vector.amx" in kernel_ir

    def test_transpiler_cli_flags_mapping(self):
        args = SimpleNamespace(
            no_vectorization=False,
            loop_fusion=False,
            no_mem2reg=False,
            no_sccp=False,
            no_licm=False,
            no_cse=False,
            no_dce=False,
            no_inline=False,
            opt_level="O3",
            enable_outerproduct_tiling=True,
            target_arch="arm_sme",
            tile_m=32,
            tile_n=8,
            tile_k=4,
        )
        kwargs = mlir_opt_kwargs_from_args(args)
        assert kwargs["enable_outerproduct_tiling"] is True
        assert kwargs["target_arch"] == "arm_sme"
        assert kwargs["tile_m"] == 32
        assert kwargs["tile_n"] == 8
        assert kwargs["tile_k"] == 4
