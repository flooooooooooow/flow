#!/usr/bin/env python3
"""
GEMM Micro-Kernel Benchmark Harness (#666)
Compares synthesized vector.outerproduct micro-kernels and hardware accelerator tile lowerings
against reference BLAS / NumPy GEMM implementations.
"""

from __future__ import annotations

import time
import numpy as np
from flow.mlir_outerproduct_tile import (
    RegisterPressureAnalyzer,
    OuterProductTiler,
    HardwareMatrixLowering,
    synthesize_gemm_microkernel,
)


def benchmark_gemm_microkernel(m: int = 512, n: int = 512, k: int = 512, target_arch: str = "avx512"):
    print(f"=== GEMM Micro-Kernel Benchmark ({m}x{n}x{k}, target={target_arch}) ===")

    # 1. Register Pressure Budget Analysis
    analyzer = RegisterPressureAnalyzer(target_arch)
    analysis = analyzer.analyze_tile_pressure(tile_m=16, tile_n=4, tile_k=4, dtype="f32")
    print(f"  Register Pressure Analysis:")
    print(f"    Target: {analysis['target']}")
    print(f"    Acc Registers: {analysis['acc_regs']} / {analysis['max_acc_regs']}")
    print(f"    Total Vector Regs: {analysis['total_vector_regs']} / {analysis['max_vector_regs']}")
    print(f"    Utilization Ratio: {analysis['utilization_ratio']}")
    print(f"    Is Within Budget: {analysis['is_within_budget']} (Spill Risk: {analysis['spill_risk']})")

    # 2. Synthesize Micro-Kernel IR
    kernel_mlir = synthesize_gemm_microkernel(
        m=m, n=n, k=k,
        tile_m=16, tile_n=4, tile_k=4,
        target_arch=target_arch,
        dtype="f32"
    )
    lines = kernel_mlir.splitlines()
    print(f"  Synthesized MLIR Micro-Kernel Size: {len(lines)} lines")

    # Verify IR structure
    assert "func.func @gemm_microkernel" in kernel_mlir
    assert "scf.for" in kernel_mlir

    # 3. Reference Execution via NumPy / BLAS
    A = np.random.randn(m, k).astype(np.float32)
    B = np.random.randn(k, n).astype(np.float32)

    # Warmup
    C_ref = np.dot(A, B)

    iterations = 20
    t0 = time.perf_counter()
    for _ in range(iterations):
        C_out = np.dot(A, B)
    t1 = time.perf_counter()

    avg_seconds = (t1 - t0) / iterations
    gflops = (2.0 * m * n * k * 1e-9) / avg_seconds

    print(f"  Reference NumPy/BLAS GEMM:")
    print(f"    Avg Time: {avg_seconds * 1000.0:.3f} ms")
    print(f"    Throughput: {gflops:.2f} GFLOPS")

    # 4. MLIR JIT Execution (if toolchain available)
    jit_gflops = None
    try:
        from flow.mlir_jit import MLIRJIT
        jit = MLIRJIT()
        if jit._is_toolchain_available():
            print("  Executing synthesized MLIR micro-kernel via JIT...")
            t_jit0 = time.perf_counter()
            for _ in range(iterations):
                _ = jit.jit_compile_and_run(kernel_mlir, "gemm_microkernel")
            t_jit1 = time.perf_counter()
            jit_avg_seconds = (t_jit1 - t_jit0) / iterations
            jit_gflops = (2.0 * m * n * k * 1e-9) / jit_avg_seconds
            print(f"  MLIR Micro-Kernel JIT Throughput: {jit_gflops:.2f} GFLOPS ({jit_avg_seconds * 1000.0:.3f} ms)")
        else:
            print("  MLIR JIT Toolchain: Pending toolchain (install mlir-opt / clang)")
    except Exception as e:
        print(f"  MLIR JIT Toolchain status: Pending toolchain ({e})")

    return {
        "m": m, "n": n, "k": k,
        "target_arch": target_arch,
        "avg_seconds": avg_seconds,
        "gflops": gflops,
        "jit_gflops": jit_gflops,
        "analysis": analysis,
        "mlir_lines": len(lines),
    }


if __name__ == "__main__":
    benchmark_gemm_microkernel(256, 256, 256, target_arch="avx512")
    benchmark_gemm_microkernel(512, 512, 512, target_arch="intel_amx")
    benchmark_gemm_microkernel(512, 512, 512, target_arch="arm_sme")
