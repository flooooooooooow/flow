#!/usr/bin/env python3
"""
FLOW MLIR Optimizer
Applies various MLIR optimization passes to improve performance
"""

from dataclasses import dataclass, fields, asdict
import shutil
import subprocess
import tempfile
import re
import sys
from pathlib import Path
from typing import List, Optional, Any, Dict


@dataclass
class OptimizationConfig:
    """Configuration options for MLIR optimization passes."""

    enable_vectorization: bool = True
    enable_loop_fusion: bool = False
    enable_mem2reg: bool = True
    enable_sccp: bool = True
    enable_licm: bool = True
    enable_gvn: bool = True
    enable_dce: bool = True
    enable_inline: bool = True
    enable_loop_pipelining: bool = False
    enable_multi_buffering: bool = False
    optimization_level: str = "O2"

    @classmethod
    def from_kwargs(cls, kwargs: Dict[str, Any]) -> "OptimizationConfig":
        """Construct OptimizationConfig from a dictionary, filtering out unexpected keys."""
        valid_keys = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in kwargs.items() if k in valid_keys}
        return cls(**filtered)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def keys(self):
        return [f.name for f in fields(self)]

    def items(self):
        return [(f.name, getattr(self, f.name)) for f in fields(self)]


def resolve_config(
    config: Optional[OptimizationConfig] = None, **kwargs
) -> OptimizationConfig:
    """Helper to resolve an OptimizationConfig from an optional instance and/or kwargs."""
    if config is None:
        if kwargs:
            return OptimizationConfig.from_kwargs(kwargs)
        return OptimizationConfig()
    if kwargs:
        d = config.to_dict()
        valid_keys = {f.name for f in fields(OptimizationConfig)}
        d.update({k: v for k, v in kwargs.items() if k in valid_keys})
        return OptimizationConfig(**d)
    return config


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
        config: Optional[OptimizationConfig] = None,
        **kwargs,
    ) -> str:
        """
        Build an mlir-opt --pass-pipeline string from configuration and O-level.

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
        cfg = resolve_config(config, **kwargs)
        level = cfg.optimization_level
        o1_plus = level in ("O1", "O2", "O3")
        o2_plus = level in ("O2", "O3")
        o3 = level == "O3"

        module_prefix: List[str] = []
        func_passes: List[str] = []
        module_suffix: List[str] = []

        if o1_plus:
            func_passes.append("canonicalize")
            # enable_gvn → cse (no dedicated MLIR GVN pass)
            if cfg.enable_gvn:
                func_passes.append("cse")
            
            # Tensor bufferization (value semantics -> reference semantics)
            module_prefix.append("one-shot-bufferize{bufferize-function-boundaries=1}")

        if o2_plus:
            if cfg.enable_inline:
                module_prefix.append("inline")
            if cfg.enable_sccp:
                func_passes.append("sccp")
            if cfg.enable_mem2reg:
                func_passes.append("mem2reg")
            if cfg.enable_licm:
                func_passes.append("loop-invariant-code-motion")
            if cfg.enable_loop_fusion:
                func_passes.append("affine-loop-fusion")
                func_passes.append("linalg-fuse-elementwise-ops")
            if cfg.enable_multi_buffering:
                func_passes.append("test-multi-buffering{multiplier=2}")
            if cfg.enable_loop_pipelining:
                func_passes.append("test-scf-pipelining")

        if o3 and cfg.enable_vectorization:
            # Best available mlir-opt vectorize pass. Needs affine/scf loops
            # from the generator; otherwise this pass has nothing to transform.
            func_passes.append("affine-super-vectorize")

        if cfg.enable_dce and o1_plus:
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
                 config: Optional[OptimizationConfig] = None,
                 **kwargs) -> int:
        """
        Apply MLIR optimization passes.

        Args:
            input_mlir: Path to input MLIR file
            output_mlir: Path to output MLIR file
            config: Optional OptimizationConfig instance. Individual pass flags or
                optimization_level can also be passed as keyword arguments.
        
        Returns:
            Exit code of mlir-opt process
        """
        pipeline = self.build_pass_pipeline(config, **kwargs)

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
    
    def autotune_transform(self, kernel_mlir: str, transform_template: str, parameter_values: List[int], evaluator_fn=None) -> tuple[str, Optional[int], float]:
        """
        Auto-tunes a single parameter (e.g., tile size) in a transform dialect template.
        Uses the provided `evaluator_fn(optimized_mlir)` to measure runtime performance.
        Returns a tuple: (best_mlir_string, best_parameter_value, best_metric).
        """
        best_metric = float('inf')
        best_mlir = kernel_mlir
        best_param = None
        
        if not self._toolchain_supports_flow_mlir():
            return kernel_mlir, None, float('inf')

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            for param in parameter_values:
                # Format the template with the tuning parameter
                try:
                    transform_ir = transform_template.format(param=param)
                except KeyError:
                    # Fallback if the template doesn't match the expected {param}
                    transform_ir = transform_template.replace("{param}", str(param))
                
                # Combine kernel and transform
                full_mlir = kernel_mlir + "\n" + transform_ir
                
                mlir_in = tmp_path / f"in_{param}.mlir"
                mlir_out = tmp_path / f"out_{param}.mlir"
                mlir_in.write_text(full_mlir)
                
                cmd = [
                    self.mlir_opt,
                    "--mlir-print-op-on-diagnostic=false",
                    "--pass-pipeline=builtin.module(transform-interpreter)",
                    str(mlir_in),
                    "-o",
                    str(mlir_out)
                ]
                
                try:
                    subprocess.run(cmd, capture_output=True, text=True, check=True)
                    optimized_mlir = mlir_out.read_text()
                    
                    if evaluator_fn:
                        metric = evaluator_fn(optimized_mlir)
                        if metric is None:
                            continue
                    else:
                        metric = 0.0 # dummy metric if no evaluator

                    if metric < best_metric:
                        best_metric = metric
                        best_mlir = optimized_mlir
                        best_param = param
                        
                except subprocess.CalledProcessError:
                    continue
                    
        return best_mlir, best_param, best_metric

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
    
    def get_optimization_report(self, mlir_file: str,
                                config: Optional[OptimizationConfig] = None,
                                **opt_kwargs) -> str:
        """Generate optimization report using the same pipeline as optimize()."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mlir', delete=False) as tmp:
            tmp.write(Path(mlir_file).read_text())
            tmp_path = tmp.name
        
        try:
            pipeline = self.build_pass_pipeline(config, **opt_kwargs)

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


def optimize_mlir_file(input_file: str, output_file: str,
                       config: Optional[OptimizationConfig] = None,
                       **kwargs) -> int:
    """Convenience function to optimize a single MLIR file."""
    optimizer = MLIROptimizer()
    return optimizer.optimize(input_file, output_file, config, **kwargs)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print(
            "Usage: python mlir_optimizer.py <input.mlir> <output.mlir> "
            "[--O0|--O1|--O2|--O3] [--no-vectorization] [--no-loop-fusion] "
            "[--no-mem2reg] [--no-sccp] [--no-licm] [--no-cse] [--no-dce] "
            "[--no-inline] [--enable-loop-pipelining] "
            "[--enable-multi-buffering] [--print-pass-pipeline]"
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
    enable_loop_pipelining = "--enable-loop-pipelining" in argv
    enable_multi_buffering = "--enable-multi-buffering" in argv
    optimization_level = "O2"
    
    for arg in argv:
        if arg.startswith("--O") and arg[3:].isdigit():
            optimization_level = arg[2:]

    config = OptimizationConfig(
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

    if "--print-pass-pipeline" in argv:
        print(MLIROptimizer.build_pass_pipeline(config))
        sys.exit(0)

    optimizer = MLIROptimizer()
    result = optimizer.optimize(input_file, output_file, config)
    
    if result == 0:
        print(f"Optimized {input_file} -> {output_file}")
    else:
        print(f"Optimization failed with exit code {result}")
    
    sys.exit(result)

def specialize_shapes(mlir_code: str, func_name: str, replacements: dict[str, str]) -> str:
    """
    Replace dynamic shapes in a specified MLIR function.
    
    Args:
        mlir_code: The original MLIR code.
        func_name: The name of the function to specialize (e.g. 'compute').
        replacements: A dictionary mapping dynamic types to static types 
                     (e.g., {'memref<?xf32>': 'memref<1024xf32>'}).
                     
    Returns:
        The specialized MLIR code.
    """
    pattern = re.compile(rf"(func\.func\s+@{func_name}\b.*?)(\n[ \t]*}}\n|\n[ \t]*}}\r\n|\n[ \t]*}}$)", re.DOTALL | re.MULTILINE)
    
    def replacer(match):
        func_body = match.group(1)
        suffix = match.group(2)
        for dyn_type, static_type in replacements.items():
            func_body = func_body.replace(dyn_type, static_type)
        return func_body + suffix

    new_mlir, count = pattern.subn(replacer, mlir_code)
    return new_mlir
