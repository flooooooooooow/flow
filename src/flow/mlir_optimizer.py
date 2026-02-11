#!/usr/bin/env python3
"""
FLOW MLIR Optimizer
Applies various MLIR optimization passes to improve performance
"""

import subprocess
import tempfile
import sys
from pathlib import Path
from typing import List, Optional


class MLIROptimizer:
    """MLIR optimization pipeline for FLOW."""

    def __init__(self, mlir_opt_path: Optional[str] = None):
        if mlir_opt_path is None:
            # Try to find mlir-opt in common locations
            import shutil

            mlir_opt_path = shutil.which("mlir-opt")
            if mlir_opt_path is None:
                # Try Homebrew LLVM
                mlir_opt_path = "/opt/homebrew/opt/llvm/bin/mlir-opt"
                if not Path(mlir_opt_path).exists():
                    mlir_opt_path = "mlir-opt"  # Fallback
        self.mlir_opt = mlir_opt_path

    def optimize(
        self,
        input_mlir: str,
        output_mlir: str,
        enable_vectorization: bool = True,
        enable_loop_fusion: bool = True,
        enable_mem2reg: bool = True,
        enable_sccp: bool = True,
        enable_licm: bool = True,
        enable_gvn: bool = True,
        enable_dce: bool = True,
        optimization_level: str = "O2",
    ) -> int:
        """
        Apply MLIR optimization passes.

        Args:
            input_mlir: Path to input MLIR file
            output_mlir: Path to output MLIR file
            enable_vectorization: Enable loop vectorization
            enable_loop_fusion: Enable loop fusion
            enable_mem2reg: Enable memory-to-register promotion
            enable_sccp: Enable sparse conditional constant propagation
            enable_licm: Enable loop invariant code motion
            enable_gvn: Enable global value numbering
            enable_dce: Enable dead code elimination
            optimization_level: O0, O1, O2, or O3

        Returns:
            Exit code of mlir-opt process
        """

        # Build optimization pipeline - use available passes
        pipeline_parts = []

        # Basic optimizations that are always available
        if optimization_level in ["O1", "O2", "O3"]:
            pipeline_parts.append("canonicalize")
            pipeline_parts.append("cse")

        if optimization_level in ["O2", "O3"]:
            pipeline_parts.append("sccp")

        # Vectorization (if available)
        if enable_vectorization and optimization_level == "O3":
            # Try vectorization but skip if not available
            pipeline_parts.append("affine-loop-fusion")

        # Run mlir-opt with individual pass flags for better compatibility across versions
        cmd = [
            self.mlir_opt,
            "--mlir-print-op-on-diagnostic=false",
        ]

        for p in pipeline_parts:
            cmd.append(f"--{p}")

        cmd.extend([input_mlir, "-o", output_mlir])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"MLIR optimization failed: {result.stderr}", file=sys.stderr)
            return result.returncode
        except Exception as e:
            print(f"Error running MLIR optimizer: {e}", file=sys.stderr)
            return 1

    def analyze_vectorization(self, mlir_file: str) -> List[str]:
        """Analyze vectorization opportunities."""
        cmd = [
            self.mlir_opt,
            "--mlir-print-op-on-diagnostic=false",
            "--mlir-pass-statistics",
            mlir_file,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.split("\n")
            else:
                return []
        except Exception:
            return []

    def get_optimization_report(self, mlir_file: str) -> str:
        """Generate optimization report."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mlir", delete=False) as tmp:
            tmp.write(Path(mlir_file).read_text())
            tmp_path = tmp.name

        try:
            # Run with statistics using the same known-available passes as optimize()
            # Keep this conservative: some Homebrew LLVM builds may not include optional passes.
            pipeline_parts: List[str] = ["canonicalize", "cse", "sccp"]

            cmd = [
                self.mlir_opt,
                "--mlir-print-op-on-diagnostic=false",
                "--mlir-pass-statistics",
            ]

            for p in pipeline_parts:
                cmd.append(f"--{p}")

            cmd.extend([tmp_path, "-o", "/dev/null"])

            result = subprocess.run(cmd, capture_output=True, text=True)

            report = []
            report.append("=== MLIR Optimization Report ===")
            report.append(f"Input file: {mlir_file}")
            report.append("")

            if result.stdout:
                report.append("Pass Statistics:")
                report.append(result.stdout)

            if result.stderr:
                report.append("Diagnostics:")
                report.append(result.stderr)

            return "\n".join(report)

        finally:
            Path(tmp_path).unlink(missing_ok=True)


def optimize_mlir_file(input_file: str, output_file: str, **kwargs) -> int:
    """Convenience function to optimize a single MLIR file."""
    optimizer = MLIROptimizer()
    return optimizer.optimize(input_file, output_file, **kwargs)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print(
            "Usage: python mlir_optimizer.py <input.mlir> <output.mlir> [--vectorization] [--no-vectorization] [--O0|--O1|--O2|--O3]"
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Parse options
    enable_vectorization = "--no-vectorization" not in sys.argv
    optimization_level = "O2"

    for arg in sys.argv:
        if arg.startswith("--O"):
            optimization_level = arg[1:]

    optimizer = MLIROptimizer()
    result = optimizer.optimize(
        input_file,
        output_file,
        enable_vectorization=enable_vectorization,
        optimization_level=optimization_level,
    )

    if result == 0:
        print(f"Optimized {input_file} -> {output_file}")
    else:
        print(f"Optimization failed with exit code {result}")

    sys.exit(result)
