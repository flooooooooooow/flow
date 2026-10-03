#!/usr/bin/env python3
"""
FLOW MLIR Outer-Product Register Tiling and Hardware Micro-Kernel Lowering
Lowers matrix and tensor contractions to 2D/3D vector.outerproduct tiles,
analyzes register pressure budgets to prevent spilling, and synthesizes
silicon matrix accelerator intrinsics (Intel AMX, ARM SME, NVIDIA Tensor Cores/TMA).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class TargetHardwareSpec:
    """Hardware target profile and register file budget constraints."""

    name: str
    num_vector_regs: int
    vector_width_bits: int
    max_accumulator_regs: int
    supports_amx: bool = False
    supports_sme: bool = False
    supports_nvvm_tma: bool = False

    def vector_len(self, dtype: str = "f32") -> int:
        """Return SIMD vector length in elements for the given element data type."""
        element_bits = {"f64": 64, "i64": 64, "f32": 32, "i32": 32, "f16": 16, "bf16": 16, "i8": 8}[dtype]
        return max(1, self.vector_width_bits // element_bits)


# Target hardware database
TARGET_SPECS: Dict[str, TargetHardwareSpec] = {
    "avx512": TargetHardwareSpec(
        name="Intel AVX-512",
        num_vector_regs=32,          # 32 ZMM registers (ZMM0-ZMM31)
        vector_width_bits=512,       # 512 bits (16 x f32)
        max_accumulator_regs=20,     # Keep <=20 ZMMs for accs to leave 12 for A/B loads + temp
    ),
    "arm_neon": TargetHardwareSpec(
        name="ARM Neon",
        num_vector_regs=32,          # 32 Q registers (v0-v31)
        vector_width_bits=128,       # 128 bits (4 x f32)
        max_accumulator_regs=20,     # Keep <=20 Qs for accs to leave 12 for A/B loads + temp
    ),
    "intel_amx": TargetHardwareSpec(
        name="Intel AMX",
        num_vector_regs=32,
        vector_width_bits=512,
        max_accumulator_regs=20,
        supports_amx=True,
    ),
    "arm_sme": TargetHardwareSpec(
        name="ARM SME / SME2",
        num_vector_regs=32,
        vector_width_bits=256,       # SVE / SME vector width
        max_accumulator_regs=20,
        supports_sme=True,
    ),
    "nvvm_tma": TargetHardwareSpec(
        name="NVIDIA Tensor Cores (TMA/WGMMA)",
        num_vector_regs=255,         # 255 32-bit registers per thread
        vector_width_bits=128,
        max_accumulator_regs=64,
        supports_nvvm_tma=True,
    ),
}


class RegisterPressureAnalyzer:
    """Analyzes register pressure and budget for 2D/3D register tiles."""

    def __init__(self, target_arch: str = "avx512"):
        arch_key = target_arch.lower()
        if arch_key not in TARGET_SPECS:
            arch_key = "avx512"
        self.spec = TARGET_SPECS[arch_key]

    def analyze_tile_pressure(
        self,
        tile_m: int,
        tile_n: int,
        tile_k: int = 1,
        dtype: str = "f32",
    ) -> Dict[str, Any]:
        """
        Calculates register usage and spill risk for a proposed (tile_m, tile_n, tile_k) tile.

        For 2D vector.outerproduct:
        - Tile requires ceil(tile_m / vec_len) x tile_n vector accumulator registers.
        - Loads / broadcast vectors require ceil(tile_m / vec_len) registers for A and tile_n for B.
        - Overhead / index registers: ~2-4 registers.
        """
        vec_len = self.spec.vector_len(dtype)
        vec_m = (tile_m + vec_len - 1) // vec_len

        # Accumulator register count
        acc_regs = vec_m * tile_n

        # Operand register count (broadcast operands loaded per outerproduct iteration)
        a_operand_regs = vec_m * tile_k
        b_operand_regs = tile_n * tile_k

        total_vector_regs = acc_regs + a_operand_regs + b_operand_regs + 2  # 2 scratch/overhead

        is_within_budget = (acc_regs <= self.spec.max_accumulator_regs) and (total_vector_regs <= self.spec.num_vector_regs)
        utilization_ratio = round(total_vector_regs / self.spec.num_vector_regs, 3)

        spill_risk = "none"
        if not is_within_budget:
            spill_risk = "high" if total_vector_regs > self.spec.num_vector_regs + 4 else "medium"

        # Auto-recommendation for tile dimensions if over budget
        recommended_tile = (tile_m, tile_n, tile_k)
        if not is_within_budget:
            rec_m, rec_n = tile_m, tile_n
            while (rec_m * rec_n // (vec_len) > self.spec.max_accumulator_regs) and (rec_m > vec_len or rec_n > 1):
                if rec_m > rec_n * vec_len:
                    rec_m = max(vec_len, rec_m // 2)
                else:
                    rec_n = max(1, rec_n // 2)
            recommended_tile = (rec_m, rec_n, tile_k)

        return {
            "target": self.spec.name,
            "dtype": dtype,
            "tile_m": tile_m,
            "tile_n": tile_n,
            "tile_k": tile_k,
            "vector_len": vec_len,
            "acc_regs": acc_regs,
            "a_operand_regs": a_operand_regs,
            "b_operand_regs": b_operand_regs,
            "total_vector_regs": total_vector_regs,
            "max_vector_regs": self.spec.num_vector_regs,
            "max_acc_regs": self.spec.max_accumulator_regs,
            "is_within_budget": is_within_budget,
            "spill_risk": spill_risk,
            "utilization_ratio": utilization_ratio,
            "recommended_tile": recommended_tile,
        }


class OuterProductTiler:
    """Generates tiled GEMM contractions using MLIR vector.outerproduct."""

    def __init__(self, target_arch: str = "avx512"):
        self.target_arch = target_arch.lower()
        self.analyzer = RegisterPressureAnalyzer(self.target_arch)

    def generate_gemm_tile(
        self,
        m: int = 128,
        n: int = 128,
        k: int = 128,
        tile_m: int = 16,
        tile_n: int = 4,
        tile_k: int = 4,
        dtype: str = "f32",
        function_name: str = "gemm_outerproduct_kernel",
    ) -> str:
        """
        Generates MLIR code for matrix multiplication C = A * B tiled via vector.outerproduct.

        Args:
            m, n, k: Full problem dimensions.
            tile_m, tile_n, tile_k: Register tile sizes.
            dtype: Data element type ('f32', 'f64', 'f16').
            function_name: Generated MLIR function name.

        Returns:
            MLIR module string containing tiled GEMM using vector.outerproduct with proper scf.for iter_args.
        """
        # Validate register pressure budget and auto-adjust tile if spilling
        analysis = self.analyzer.analyze_tile_pressure(tile_m, tile_n, tile_k, dtype)
        if not analysis["is_within_budget"]:
            tile_m, tile_n, tile_k = analysis["recommended_tile"]

        vec_len = self.analyzer.spec.vector_len(dtype)
        vec_n_type = f"vector<{vec_len}x{dtype}>"

        mlir_lines = [
            f"module {{",
            f"  func.func @{function_name}(",
            f"    %A: memref<{m}x{k}x{dtype}>,",
            f"    %B: memref<{k}x{n}x{dtype}>,",
            f"    %C: memref<{m}x{n}x{dtype}>",
            f"  ) {{",
            f"    %c0 = arith.constant 0 : index",
            f"    %c1 = arith.constant 1 : index",
            f"    %cm = arith.constant {m} : index",
            f"    %cn = arith.constant {n} : index",
            f"    %ck = arith.constant {k} : index",
            f"    %step_m = arith.constant {tile_m} : index",
            f"    %step_n = arith.constant {tile_n} : index",
            f"    %step_k = arith.constant {tile_k} : index",
            f"    %zero = arith.constant 0.0 : {dtype}",
            f"",
            f"    // Tiled outer-product GEMM loop nest (M_R={tile_m}, N_R={tile_n}, K_R={tile_k})",
            f"    scf.for %i = %c0 to %cm step %step_m {{",
            f"      scf.for %j = %c0 to %cn step %step_n {{",
        ]

        # Load initial accumulators for tile M_R x N_R from C (contiguous along N dimension)
        mlir_lines.append(f"        // Load initial accumulator registers for tile {tile_m}x{tile_n}")
        for mi in range(tile_m):
            mlir_lines.append(f"        %offset_i_{mi} = arith.constant {mi} : index")
            mlir_lines.append(f"        %curr_i_{mi} = arith.addi %i, %offset_i_{mi} : index")
            mlir_lines.append(f"        %acc_init_{mi} = vector.transfer_read %C[%curr_i_{mi}, %j], %zero {{in_bounds = [true]}} : memref<{m}x{n}x{dtype}>, {vec_n_type}")

        # Iter args string for reduction loop over K
        iter_args_def = ", ".join([f"%k_acc_{mi} = %acc_init_{mi}" for mi in range(tile_m)])
        iter_types = ", ".join([vec_n_type for _ in range(tile_m)])
        final_ssas = [f"%final_acc_{mi}" for mi in range(tile_m)]
        final_str = ", ".join(final_ssas)

        mlir_lines.append(f"        {final_str} = scf.for %kk = %c0 to %ck step %step_k iter_args({iter_args_def}) -> ({iter_types}) {{")

        # Inner K_R loop with iter_args
        k_sub_iter_args = ", ".join([f"%sub_acc_{mi} = %k_acc_{mi}" for mi in range(tile_m)])
        sub_ssas = [f"%sub_res_{mi}" for mi in range(tile_m)]
        sub_str = ", ".join(sub_ssas)

        mlir_lines.append(f"          {sub_str} = scf.for %k_sub = %c0 to %step_k step %c1 iter_args({k_sub_iter_args}) -> ({iter_types}) {{")
        mlir_lines.append(f"            %curr_k = arith.addi %kk, %k_sub : index")

        # Load row slice from B (contiguous along N dimension)
        mlir_lines.append(f"            %vec_b = vector.transfer_read %B[%curr_k, %j], %zero {{in_bounds = [true]}} : memref<{k}x{n}x{dtype}>, {vec_n_type}")

        # Outer-product update: multiply row vec_b by scalar A[curr_i, curr_k]
        yield_sub_ssas = []
        for mi in range(tile_m):
            mlir_lines.append(f"            %a_val_{mi} = memref.load %A[%curr_i_{mi}, %curr_k] : memref<{m}x{k}x{dtype}>")
            mlir_lines.append(f"            %updated_{mi} = vector.outerproduct %vec_b, %a_val_{mi}, %sub_acc_{mi} : {vec_n_type}, {dtype}")
            yield_sub_ssas.append(f"%updated_{mi}")

        mlir_lines.append(f"            scf.yield {', '.join(yield_sub_ssas)} : {iter_types}")
        mlir_lines.append(f"          }}")
        mlir_lines.append(f"          scf.yield {sub_str} : {iter_types}")
        mlir_lines.append(f"        }}")

        # Store final accumulators back to C memory
        mlir_lines.append(f"        // Store final accumulators back to memory")
        for mi in range(tile_m):
            mlir_lines.append(f"        vector.transfer_write %final_acc_{mi}, %C[%curr_i_{mi}, %j] {{in_bounds = [true]}} : {vec_n_type}, memref<{m}x{n}x{dtype}>")

        mlir_lines.extend([
            f"      }}",
            f"    }}",
            f"    func.return",
            f"  }}",
            f"}}",
        ])

        return "\n".join(mlir_lines)


class HardwareMatrixLowering:
    """Lowers vector outerproduct register tiles to silicon matrix accelerator intrinsics."""

    def __init__(self, target_arch: str = "intel_amx"):
        self.target_arch = target_arch.lower()

    def lower_outerproduct_to_accelerator(self, mlir_code: str) -> str:
        """
        Transforms vector.outerproduct operations to target hardware accelerator intrinsics:
        - Intel AMX: x86vector.amx.tilezero, x86vector.amx.tileloadd, x86vector.amx.tdpbf16ps
        - ARM SME: arm_sme.zero, arm_sme.mopa
        - NVIDIA Tensor Core / TMA: nvvm.tma.async.load, nvvm.wgmma.mma_async
        """
        if "intel_amx" in self.target_arch or "amx" in self.target_arch:
            return self._lower_to_intel_amx(mlir_code)
        elif "arm_sme" in self.target_arch or "sme" in self.target_arch:
            return self._lower_to_arm_sme(mlir_code)
        elif "nvvm" in self.target_arch or "tma" in self.target_arch:
            return self._lower_to_nvvm_tma(mlir_code)
        return mlir_code

    def _lower_to_intel_amx(self, mlir_code: str) -> str:
        """Synthesize Intel AMX tile operations for vector outerproduct tiles."""
        lines = mlir_code.split("\n")
        lowered_lines = []

        memref_match = re.search(r"%\w+:\s*memref<(\d+)x(\d+)x(\w+)>", mlir_code)
        dim_m, dim_k, dtype = ("128", "128", "f32") if not memref_match else (memref_match.group(1), memref_match.group(2), memref_match.group(3))

        outerproduct_pattern = re.compile(
            r"(%\w+)\s*=\s*vector\.outerproduct\s+(%\w+),\s*(%\w+),\s*(%\w+)\s*:\s*(vector<(\d+)x\w+>),\s*(\w+)"
        )

        counter = 0
        tile_zeroed = False
        for line in lines:
            if "scf.for %i =" in line and not tile_zeroed:
                lowered_lines.append(line)
                indent = line[:line.find("scf.for")] + "  "
                lowered_lines.append(f"{indent}// Intel AMX tilezero accumulator initialization")
                lowered_lines.append(f"{indent}%tmm_c_init = x86vector.amx.tilezero : vector<16x16x{dtype}>")
                tile_zeroed = True
                continue

            match = outerproduct_pattern.search(line)
            if match:
                out_ssa, vec_b, scalar_a, acc_c, vec_type, vec_len, elem_type = match.groups()
                counter += 1
                indent = line[:line.find("%")]
                lowered_lines.append(f"{indent}// Intel AMX tile multiply-accumulate for {vec_b} x {scalar_a}")
                lowered_lines.append(f"{indent}%tmm_a_{counter} = x86vector.amx.tileloadd %A[%curr_i_0, %curr_k] : memref<{dim_m}x{dim_k}x{elem_type}> -> vector<{vec_len}x16x{elem_type}>")
                lowered_lines.append(f"{indent}%tmm_b_{counter} = x86vector.amx.tileloadd %B[%curr_k, %j] : memref<{dim_k}x{dim_m}x{elem_type}> -> vector<{vec_len}x16x{elem_type}>")
                lowered_lines.append(f"{indent}{out_ssa} = x86vector.amx.tdpbf16ps %tmm_a_{counter}, %tmm_b_{counter}, {acc_c} : vector<{vec_len}x16x{elem_type}>, vector<{vec_len}x16x{elem_type}>, vector<{vec_len}x16x{elem_type}>")
            else:
                lowered_lines.append(line)

        return "\n".join(lowered_lines)

    def _lower_to_arm_sme(self, mlir_code: str) -> str:
        """Synthesize ARM SME / SME2 matrix outer-product accumulate operations."""
        lines = mlir_code.split("\n")
        lowered_lines = []

        outerproduct_pattern = re.compile(
            r"(%\w+)\s*=\s*vector\.outerproduct\s+(%\w+),\s*(%\w+),\s*(%\w+)\s*:\s*(vector<[^>]+>),\s*(\w+)"
        )

        counter = 0
        sme_zeroed = False
        for line in lines:
            if "scf.for %i =" in line and not sme_zeroed:
                lowered_lines.append(line)
                indent = line[:line.find("scf.for")] + "  "
                lowered_lines.append(f"{indent}// ARM SME ZA tile initialization")
                lowered_lines.append(f"{indent}arm_sme.zero {{tile_id = 0 : i32}}")
                sme_zeroed = True
                continue

            match = outerproduct_pattern.search(line)
            if match:
                out_ssa, vec_b, scalar_a, acc_c, vec_type, elem_type = match.groups()
                counter += 1
                indent = line[:line.find("%")]
                lowered_lines.append(f"{indent}// ARM SME / SME2 matrix tile outerproduct accumulate")
                lowered_lines.append(f"{indent}%vec_a_bc_{counter} = vector.broadcast {scalar_a} : {elem_type} to {vec_type}")
                lowered_lines.append(f"{indent}{out_ssa} = arm_sme.mopa %vec_a_bc_{counter}, {vec_b}, {acc_c} : {vec_type}, {vec_type} into {vec_type}")
            else:
                lowered_lines.append(line)

        return "\n".join(lowered_lines)

    def _lower_to_nvvm_tma(self, mlir_code: str) -> str:
        """Synthesize NVIDIA NVVM Tensor Memory Accelerator (TMA) + WGMMA asynchronous load/multiply."""
        lines = mlir_code.split("\n")
        lowered_lines = []

        outerproduct_pattern = re.compile(
            r"(%\w+)\s*=\s*vector\.outerproduct\s+(%\w+),\s*(%\w+),\s*(%\w+)\s*:\s*(vector<[^>]+>),\s*(\w+)"
        )

        counter = 0
        for line in lines:
            match = outerproduct_pattern.search(line)
            if match:
                out_ssa, vec_b, scalar_a, acc_c, vec_type, elem_type = match.groups()
                counter += 1
                indent = line[:line.find("%")]
                lowered_lines.append(f"{indent}// NVIDIA NVVM TMA async load + WGMMA Tensor Core multiply")
                lowered_lines.append(f"{indent}%tma_a_{counter} = nvvm.tma.async.load %A[%curr_i_0, %curr_k] : !llvm.ptr -> {vec_type}")
                lowered_lines.append(f"{indent}%vec_a_bc_{counter} = vector.broadcast {scalar_a} : {elem_type} to {vec_type}")
                lowered_lines.append(f"{indent}{out_ssa} = nvvm.wgmma.mma_async %tma_a_{counter}, {vec_b}, {acc_c} : {vec_type}")
            else:
                lowered_lines.append(line)

        return "\n".join(lowered_lines)


def synthesize_gemm_microkernel(
    m: int = 128,
    n: int = 128,
    k: int = 128,
    tile_m: int = 16,
    tile_n: int = 4,
    tile_k: int = 4,
    target_arch: str = "avx512",
    dtype: str = "f32",
    function_name: str = "gemm_microkernel",
) -> str:
    """
    Synthesizes a complete GEMM micro-kernel using vector.outerproduct tiling
    and target-specific matrix accelerator intrinsics.
    """
    tiler = OuterProductTiler(target_arch=target_arch)
    mlir_tiled = tiler.generate_gemm_tile(
        m=m, n=n, k=k,
        tile_m=tile_m, tile_n=tile_n, tile_k=tile_k,
        dtype=dtype, function_name=function_name
    )

    lowering = HardwareMatrixLowering(target_arch=target_arch)
    return lowering.lower_outerproduct_to_accelerator(mlir_tiled)
