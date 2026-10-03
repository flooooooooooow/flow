import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

class MLIROptimizer:
    """MLIR optimization pipeline for FLOW."""

    def __init__(self, mlir_opt_path: str = "mlir-opt"):
        self.mlir_opt = mlir_opt_path
        self._opt_capable = True

    @staticmethod
    def _copy_if_different(src: str, dst: str) -> None:
        if Path(src).resolve() != Path(dst).resolve():
            shutil.copyfile(src, dst)

    @staticmethod
    def build_pass_pipeline(
        enable_vectorization: bool = True,
        enable_loop_fusion: bool = False,
        enable_mem2reg: bool = True,
        enable_sccp: bool = True,
        enable_licm: bool = True,
        enable_gvn: bool = True,
        enable_dce: bool = True,
        enable_inline: bool = True,
        enable_loop_pipelining: bool = False,
        enable_multi_buffering: bool = False,
        optimization_level: str = "O2",
    ) -> str:
        """
        Build an mlir-opt --pass-pipeline string from flags and O-level.
        """
        module_prefix = []
        func_passes = []
        module_suffix = []

        try:
            level = int(optimization_level[-1]) if optimization_level.startswith("O") else 2
        except (ValueError, IndexError):
            level = 2

        o1_plus = level >= 1
        o2_plus = level >= 2
        o3 = level == 3

        if o1_plus:
            func_passes.append("canonicalize")
            if enable_gvn:
                func_passes.append("cse")
            module_prefix.append("one-shot-bufferize{bufferize-function-boundaries=1}")

        if o2_plus:
            if enable_inline:
                module_prefix.append("inline")
            if enable_sccp:
                func_passes.append("sccp")
            if enable_mem2reg:
                func_passes.append("mem2reg")
            if enable_licm:
                func_passes.append("loop-invariant-code-motion")
            if enable_loop_fusion:
                func_passes.append("affine-loop-fusion")
                func_passes.append("linalg-fuse-elementwise-ops")
            if enable_multi_buffering:
                func_passes.append("test-multi-buffering{multiplier=2}")
            if enable_loop_pipelining:
                func_passes.append("test-scf-pipelining")

        if o3 and enable_vectorization:
            func_passes.append("affine-super-vectorize")

        if enable_dce and o1_plus:
            module_suffix.append("symbol-dce")
            module_suffix.append("canonicalize")

        return MLIROptimizer._format_pipeline(module_prefix, func_passes, module_suffix)

    @staticmethod
    def _format_pipeline(module_prefix: List[str], func_passes: List[str], module_suffix: List[str]) -> str:
        parts = module_prefix[:]
        if func_passes:
            parts.append(f"func.func({','.join(func_passes)})")
        parts.extend(module_suffix)
        return f"builtin.module({','.join(parts)})"

    def _toolchain_supports_flow_mlir(self) -> bool:
        if not self._opt_capable:
            return False
        if shutil.which(self.mlir_opt) is None:
            self._opt_capable = False
            return False
        return True

    def optimize(self, input_mlir: str, output_mlir: str,
                 enable_vectorization: bool = True,
                 enable_loop_fusion: bool = False,
                 enable_mem2reg: bool = True,
                 enable_sccp: bool = True,
                 enable_licm: bool = True,
                 enable_gvn: bool = True,
                 enable_dce: bool = True,
                 enable_inline: bool = True,
                 enable_loop_pipelining: bool = False,
                 enable_multi_buffering: bool = False,
                 optimization_level: str = "O2") -> int:
        """
        Apply MLIR optimization passes.
        """
        pipeline = self.build_pass_pipeline(
            enable_vectorization=enable_vectorization,
            enable_loop_fusion=enable_loop_fusion,
            enable_mem2reg=enable_mem2reg,
            enable_sccp=enable_sccp,
            enable_licm=enable_licm,
            enable_gvn=enable_gvn,
            enable_dce=enable_dce,
            enable_inline=enable_inline,
            enable_loop_pipelining=enable_loop_pipelining,
            enable_multi_buffering=enable_multi_buffering,
            optimization_level=optimization_level,
        )

        if not self._toolchain_supports_flow_mlir():
            self._copy_if_different(input_mlir, output_mlir)
            return 0

        cmd = [
            self.mlir_opt,
            "--mlir-print-op-on-diagnostic=false",
            f"--pass-pipeline={pipeline}",
            input_mlir,
            "-o",
            output_mlir
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                err = result.stderr or ""
                if "func.func" in err and "unknown" in err:
                    self._copy_if_different(input_mlir, output_mlir)
                    self._opt_capable = False
                    return 0
                print(f"MLIR optimization failed: {err}", file=sys.stderr)
            return result.returncode
        except Exception as e:
            print(f"Error running MLIR optimizer: {e}", file=sys.stderr)
            return 1
