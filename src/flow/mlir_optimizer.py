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
from typing import List, Optional


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
            # Try to find mlir-opt in common locations
            import shutil
            mlir_opt_path = shutil.which("mlir-opt")
            if mlir_opt_path is None:
                # Try Homebrew LLVM
                mlir_opt_path = "/opt/homebrew/opt/llvm/bin/mlir-opt"
                if not Path(mlir_opt_path).exists():
                    mlir_opt_path = "mlir-opt"  # Fallback
        self.mlir_opt = mlir_opt_path
        self._opt_capable: Optional[bool] = None

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
        optimization_level: str = "O2",
    ) -> str:
        """
        Build an mlir-opt --pass-pipeline string from flags and O-level.

        Inspectable without running mlir-opt (for unit tests).

        Nesting notes:
        - ``inline`` and ``symbol-dce`` are module-level (need a symbol table).
        - Most other passes nest under ``func.func(...)``.
        - ``affine-super-vectorize`` and ``affine-loop-fusion`` require affine
          dialect loop IR from the generator. The Flow MLIR generator currently
          emits scf/cf loops, not affine, so these passes are disabled by
          default. Enabling them on large non-affine modules causes mlir-opt to
          hang (flow#466). They will be re-enabled when the generator emits
          affine dialect operations.
        - MLIR has no standalone ``gvn`` pass; ``enable_gvn`` maps to ``cse``.
        """
        level = optimization_level
        o1_plus = level in ("O1", "O2", "O3")
        o2_plus = level in ("O2", "O3")
        o3 = level == "O3"

        module_prefix: List[str] = []
        func_passes: List[str] = []
        module_suffix: List[str] = []

        if o1_plus:
            func_passes.append("canonicalize")
            # enable_gvn → cse (no dedicated MLIR GVN pass)
            if enable_gvn:
                func_passes.append("cse")

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

        if o3 and enable_vectorization:
            # Best available mlir-opt vectorize pass. Needs affine/scf loops
            # from the generator; otherwise this pass has nothing to transform.
            func_passes.append("affine-super-vectorize")

        if enable_dce and o1_plus:
            # symbol-dce is module-scoped; follow with a canonicalize round
            module_suffix.append("symbol-dce")
            module_suffix.append("canonicalize")

        return MLIROptimizer._format_pipeline(module_prefix, func_passes, module_suffix)

    @staticmethod
    def _format_pipeline(
        module_prefix: List[str],
        func_passes: List[str],
        module_suffix: List[str],
    ) -> str:
        parts: List[str] = []
        parts.extend(module_prefix)
        if func_passes:
            parts.append(f"func.func({','.join(func_passes)})")
        parts.extend(module_suffix)
        if not parts:
            return "builtin.module()"
        return f"builtin.module({','.join(parts)})"

    @staticmethod
    def pipeline_pass_names(pipeline: str) -> List[str]:
        """Extract ordered pass names from a pipeline string (test helper)."""
        # Strip outer builtin.module(...)
        inner = pipeline
        if inner.startswith("builtin.module(") and inner.endswith(")"):
            inner = inner[len("builtin.module(") : -1]
        names: List[str] = []
        i = 0
        while i < len(inner):
            if inner.startswith("func.func(", i):
                j = inner.find(")", i)
                nested = inner[i + len("func.func(") : j]
                if nested:
                    names.extend(p for p in nested.split(",") if p)
                i = j + 1
                if i < len(inner) and inner[i] == ",":
                    i += 1
                continue
            # next comma-separated module-level pass
            j = inner.find(",", i)
            if j < 0:
                token = inner[i:].strip()
                if token:
                    names.append(token)
                break
            token = inner[i:j].strip()
            if token:
                names.append(token)
            i = j + 1
        return names

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

    def optimize(self, input_mlir: str, output_mlir: str,
                 enable_vectorization: bool = True,
                 enable_loop_fusion: bool = False,
                 enable_mem2reg: bool = True,
                 enable_sccp: bool = True,
                 enable_licm: bool = True,
                 enable_gvn: bool = True,
                 enable_dce: bool = True,
                 enable_inline: bool = True,
                 optimization_level: str = "O2") -> int:
        """
        Apply MLIR optimization passes.

        Args:
            input_mlir: Path to input MLIR file
            output_mlir: Path to output MLIR file
            enable_vectorization: Enable loop vectorization (O3; needs affine/scf)
            enable_loop_fusion: Enable affine loop fusion (O2+; disabled by
                default since the generator emits scf/cf, not affine. See flow#466.)
            enable_mem2reg: Enable memory-to-register promotion (O2+)
            enable_sccp: Enable sparse conditional constant propagation (O2+)
            enable_licm: Enable loop invariant code motion (O2+)
            enable_gvn: Enable CSE as GVN stand-in (O1+; no MLIR gvn pass)
            enable_dce: Enable symbol-dce + canonicalize round (O1+)
            enable_inline: Enable module inliner (O2+; default True)
            optimization_level: O0, O1, O2, or O3
        
        Returns:
            Exit code of mlir-opt process
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
            optimization_level=optimization_level,
        )

        if not self._toolchain_supports_flow_mlir():
            self._copy_if_different(input_mlir, output_mlir)
            return 0

        # Run mlir-opt with optimization pipeline
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
    
    def get_optimization_report(self, mlir_file: str, **opt_kwargs) -> str:
        """Generate optimization report using the same pipeline as optimize()."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mlir', delete=False) as tmp:
            tmp.write(Path(mlir_file).read_text())
            tmp_path = tmp.name
        
        try:
            pipeline = self.build_pass_pipeline(**opt_kwargs)

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
            report.append(f"Pass pipeline: {pipeline}")
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
            "Usage: python mlir_optimizer.py <input.mlir> <output.mlir> "
            "[--O0|--O1|--O2|--O3] [--no-vectorization] [--no-loop-fusion] "
            "[--no-mem2reg] [--no-sccp] [--no-licm] [--no-cse] [--no-dce] "
            "[--no-inline] [--print-pass-pipeline]"
        )
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    argv = sys.argv[3:]

    enable_vectorization = "--no-vectorization" not in argv
    enable_loop_fusion = "--no-loop-fusion" not in argv
    enable_mem2reg = "--no-mem2reg" not in argv
    enable_sccp = "--no-sccp" not in argv
    enable_licm = "--no-licm" not in argv
    enable_gvn = "--no-cse" not in argv
    enable_dce = "--no-dce" not in argv
    enable_inline = "--no-inline" not in argv
    optimization_level = "O2"
    
    for arg in argv:
        if arg.startswith("--O") and arg[3:].isdigit():
            optimization_level = arg[2:]

    kwargs = dict(
        enable_vectorization=enable_vectorization,
        enable_loop_fusion=enable_loop_fusion,
        enable_mem2reg=enable_mem2reg,
        enable_sccp=enable_sccp,
        enable_licm=enable_licm,
        enable_gvn=enable_gvn,
        enable_dce=enable_dce,
        enable_inline=enable_inline,
        optimization_level=optimization_level,
    )

    if "--print-pass-pipeline" in argv:
        print(MLIROptimizer.build_pass_pipeline(**kwargs))
        sys.exit(0)

    optimizer = MLIROptimizer()
    result = optimizer.optimize(input_file, output_file, **kwargs)
    
    if result == 0:
        print(f"Optimized {input_file} -> {output_file}")
    else:
        print(f"Optimization failed with exit code {result}")
    
    sys.exit(result)
