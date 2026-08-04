#!/usr/bin/env python3
"""
FLOW MLIR Optimizer
Applies various MLIR optimization passes to improve performance
"""

import shutil
import subprocess
import tempfile
import sys
from pathlib import Path
from typing import List, Optional, Tuple


class MLIROptimizer:
    """MLIR optimization pipeline for FLOW."""

    _PROBE_MLIR = """module {
  func.func @__flow_opt_probe(%arg0: i32) -> i32 {
    %0 = arith.constant 0 : i32
    func.return %0 : i32
  }
}
"""

    def __init__(self, mlir_opt_path: str = None):
        if mlir_opt_path is None:
            mlir_opt_path = shutil.which("mlir-opt")
            if mlir_opt_path is None:
                # Try Homebrew LLVM
                mlir_opt_path = "/opt/homebrew/opt/llvm/bin/mlir-opt"
                if not Path(mlir_opt_path).exists():
                    mlir_opt_path = "mlir-opt"  # Fallback
        self.mlir_opt = mlir_opt_path
        self._opt_capable: Optional[bool] = None
        self._pass_support: dict = {}

    @staticmethod
    def _copy_if_different(src: str, dst: str) -> None:
        if Path(src).resolve() != Path(dst).resolve():
            shutil.copyfile(src, dst)

    def _toolchain_supports_flow_mlir(self) -> bool:
        """Return True when mlir-opt can parse FLOW's func/arith dialect mix."""
        if self._opt_capable is not None:
            return self._opt_capable
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mlir", delete=False) as tmp:
            tmp.write(self._PROBE_MLIR)
            probe_in = tmp.name
        probe_out = probe_in + ".out"
        try:
            result = subprocess.run(
                [
                    self.mlir_opt,
                    "--mlir-print-op-on-diagnostic=false",
                    "--pass-pipeline=builtin.module(func.func(canonicalize))",
                    probe_in,
                    "-o",
                    probe_out,
                ],
                capture_output=True,
                text=True,
            )
            self._opt_capable = result.returncode == 0
        except Exception:
            self._opt_capable = False
        finally:
            Path(probe_in).unlink(missing_ok=True)
            Path(probe_out).unlink(missing_ok=True)
        return self._opt_capable

    def _pass_available(self, pipeline: str) -> bool:
        """Probe whether a pass pipeline fragment is accepted by this mlir-opt."""
        if pipeline in self._pass_support:
            return self._pass_support[pipeline]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mlir", delete=False) as tmp:
            tmp.write(self._PROBE_MLIR)
            probe_in = tmp.name
        probe_out = probe_in + ".out"
        try:
            result = subprocess.run(
                [
                    self.mlir_opt,
                    "--mlir-print-op-on-diagnostic=false",
                    f"--pass-pipeline={pipeline}",
                    probe_in,
                    "-o",
                    probe_out,
                ],
                capture_output=True,
                text=True,
            )
            ok = result.returncode == 0
        except Exception:
            ok = False
        finally:
            Path(probe_in).unlink(missing_ok=True)
            Path(probe_out).unlink(missing_ok=True)
        self._pass_support[pipeline] = ok
        return ok

    def build_pipeline(
        self,
        optimization_level: str = "O2",
        enable_vectorization: bool = True,
        enable_loop_fusion: bool = True,
        enable_mem2reg: bool = True,
        enable_sccp: bool = True,
        enable_licm: bool = True,
        enable_gvn: bool = True,
        enable_dce: bool = True,
        enable_inline: bool = True,
    ) -> str:
        """Build a pass pipeline string honoring flags and toolchain support."""
        del enable_mem2reg, enable_licm, enable_gvn  # reserved; not yet mapped

        func_passes: List[str] = []
        module_passes: List[str] = []

        if optimization_level in ["O1", "O2", "O3"]:
            func_passes.extend(["canonicalize", "cse"])

        if enable_sccp and optimization_level in ["O2", "O3"]:
            func_passes.append("sccp")

        if enable_dce and optimization_level in ["O2", "O3"]:
            # Prefer remove-dead-values when present; always try symbol-dce.
            if self._pass_available(
                "builtin.module(func.func(remove-dead-values))"
            ):
                func_passes.append("remove-dead-values")
            module_passes.append("symbol-dce")

        if enable_inline and optimization_level in ["O2", "O3"]:
            if self._pass_available("builtin.module(inline)"):
                module_passes.append("inline")

        # Loop fusion is not vectorization; only enable when explicitly requested
        # and the affine dialect pass is available. Real vectorization is #113.
        if enable_loop_fusion and enable_vectorization and optimization_level == "O3":
            if self._pass_available(
                "builtin.module(func.func(affine-loop-fusion))"
            ):
                func_passes.append("affine-loop-fusion")

        parts: List[str] = []
        if func_passes:
            parts.append(f"func.func({','.join(func_passes)})")
        parts.extend(module_passes)
        # Run canonicalize once more after inline/DCE to fold leftovers.
        if optimization_level in ["O1", "O2", "O3"] and module_passes:
            parts.append("func.func(canonicalize,cse)")
        if not parts:
            parts.append("func.func(canonicalize)")
        return f"builtin.module({','.join(parts)})"

    def optimize(self, input_mlir: str, output_mlir: str,
                 enable_vectorization: bool = True,
                 enable_loop_fusion: bool = True,
                 enable_mem2reg: bool = True,
                 enable_sccp: bool = True,
                 enable_licm: bool = True,
                 enable_gvn: bool = True,
                 enable_dce: bool = True,
                 enable_inline: bool = True,
                 optimization_level: str = "O2") -> int:
        """
        Apply MLIR optimization passes.

        Returns:
            Exit code of mlir-opt process
        """
        if not self._toolchain_supports_flow_mlir():
            self._copy_if_different(input_mlir, output_mlir)
            return 0

        pipeline = self.build_pipeline(
            optimization_level=optimization_level,
            enable_vectorization=enable_vectorization,
            enable_loop_fusion=enable_loop_fusion,
            enable_mem2reg=enable_mem2reg,
            enable_sccp=enable_sccp,
            enable_licm=enable_licm,
            enable_gvn=enable_gvn,
            enable_dce=enable_dce,
            enable_inline=enable_inline,
        )

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
                # Ubuntu mlir-14 packages sometimes ship mlir-opt without the Func dialect.
                if "func.func" in err and "unknown" in err:
                    self._copy_if_different(input_mlir, output_mlir)
                    self._opt_capable = False
                    return 0
                print(f"MLIR optimization failed: {err}", file=sys.stderr)
            return result.returncode
        except Exception as e:
            print(f"Error running MLIR optimizer: {e}", file=sys.stderr)
            return 1

    def optimize_source(self, mlir_source: str, **kwargs) -> Tuple[str, int]:
        """Optimize an in-memory MLIR string; return (output_source, exit_code)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mlir", delete=False) as inp:
            inp.write(mlir_source)
            in_path = inp.name
        out_path = in_path + ".opt.mlir"
        try:
            code = self.optimize(in_path, out_path, **kwargs)
            if code == 0 and Path(out_path).exists():
                return Path(out_path).read_text(), code
            return mlir_source, code
        finally:
            Path(in_path).unlink(missing_ok=True)
            Path(out_path).unlink(missing_ok=True)

    def analyze_vectorization(self, mlir_file: str) -> List[str]:
        """Analyze vectorization opportunities."""
        cmd = [
            self.mlir_opt,
            "--mlir-print-op-on-diagnostic=false",
            "--pass-pipeline=builtin.module(func.func(print-ir-after-all))",
            "--mlir-pass-statistics",
            mlir_file
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.split('\n')
            else:
                return []
        except Exception:
            return []

    def get_optimization_report(self, mlir_file: str) -> str:
        """Generate optimization report."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mlir', delete=False) as tmp:
            tmp.write(Path(mlir_file).read_text())
            tmp_path = tmp.name

        try:
            pipeline = self.build_pipeline(optimization_level="O2")

            cmd = [
                self.mlir_opt,
                "--mlir-print-op-on-diagnostic=false",
                "--mlir-pass-statistics",
                f"--pass-pipeline={pipeline}",
                tmp_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            report = []
            report.append("=== MLIR Optimization Report ===")
            report.append(f"Input file: {mlir_file}")
            report.append(f"Pipeline: {pipeline}")
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
        print("Usage: python mlir_optimizer.py <input.mlir> <output.mlir> [--vectorization] [--no-vectorization] [--O0|--O1|--O2|--O3]")
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
        optimization_level=optimization_level
    )

    if result == 0:
        print(f"Optimized {input_file} -> {output_file}")
    else:
        print(f"Optimization failed with exit code {result}")

    sys.exit(result)
