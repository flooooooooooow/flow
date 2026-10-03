#!/usr/bin/env python3
"""
FLOW MLIR Optimizer
Applies various MLIR optimization passes to improve performance
"""

import shutil
import subprocess
import tempfile
import re
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
        enable_loop_pipelining: bool = False,
        enable_multi_buffering: bool = False,
        enable_aosoa: bool = False,
        enable_conflict_padding: bool = False,
        enable_swizzling: bool = False,
        optimization_level: str = "O2",
        **_ignored,
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
            
            # Tensor bufferization (value semantics -> reference semantics)
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
                 enable_loop_pipelining: bool = False,
                 enable_multi_buffering: bool = False,
                 enable_aosoa: bool = False,
                 enable_conflict_padding: bool = False,
                 enable_swizzling: bool = False,
                 aosoa_tile_size: int = 16,
                 padding_amount: int = 1,
                 min_stride_multiple: int = 16,
                 swizzle_tile_width: int = 16,
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
            enable_loop_pipelining=enable_loop_pipelining,
            enable_multi_buffering=enable_multi_buffering,
            optimization_level=optimization_level,
        )

        if not self._toolchain_supports_flow_mlir():
            self._copy_if_different(input_mlir, output_mlir)
            code = Path(output_mlir).read_text()
            if enable_aosoa:
                code = transform_aosoa_memref(code, tile_size=aosoa_tile_size)
            if enable_conflict_padding:
                code = apply_conflict_padding(code, pad_amount=padding_amount, min_stride_multiple=min_stride_multiple)
            if enable_swizzling:
                code = apply_swizzled_indexing(code, tile_width=swizzle_tile_width)
            Path(output_mlir).write_text(code)
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
                    code = Path(output_mlir).read_text()
                    if enable_aosoa:
                        code = transform_aosoa_memref(code, tile_size=aosoa_tile_size)
                    if enable_conflict_padding:
                        code = apply_conflict_padding(code, pad_amount=padding_amount, min_stride_multiple=min_stride_multiple)
                    if enable_swizzling:
                        code = apply_swizzled_indexing(code, tile_width=swizzle_tile_width)
                    Path(output_mlir).write_text(code)
                    return 0
                print(f"MLIR optimization failed: {err}", file=sys.stderr)
                return result.returncode

            # Apply memory layout transformations
            if enable_aosoa or enable_conflict_padding or enable_swizzling:
                code = Path(output_mlir).read_text()
                if enable_aosoa:
                    code = transform_aosoa_memref(code, tile_size=aosoa_tile_size)
                if enable_conflict_padding:
                    code = apply_conflict_padding(code, pad_amount=padding_amount, min_stride_multiple=min_stride_multiple)
                if enable_swizzling:
                    code = apply_swizzled_indexing(code, tile_width=swizzle_tile_width)
                Path(output_mlir).write_text(code)

            return 0
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

    kwargs = dict(
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
        print(MLIROptimizer.build_pass_pipeline(**kwargs))
        sys.exit(0)

    optimizer = MLIROptimizer()
    result = optimizer.optimize(input_file, output_file, **kwargs)
    
    if result == 0:
        print(f"Optimized {input_file} -> {output_file}")
    else:
        print(f"Optimization failed with exit code {result}")
    
    sys.exit(result)

def transform_aosoa_memref(mlir_code: str, tile_size: int = 16) -> str:
    """
    Transform Array of Structs (AoS) memrefs to Array of Structs of Arrays (AoSoA)
    layout at the memref level.

    For 2D memref<NxFxELEM> (e.g. N elements, F fields):
      New shape: memref<(N/V)xFxVxELEM>
    For 1D memref<NxELEM>:
      New shape: memref<(N/V)xVxELEM>
    where V is `tile_size`.

    Accesses `memref.load %a[%i, %f] : memref<NxFxELEM>` are rewritten to:
      %c_tile = arith.constant tile_size : index
      %outer = arith.divui %i, %c_tile : index
      %inner = arith.remui %i, %c_tile : index
      memref.load %a[%outer, %f, %inner] : memref<(N/V)xFxVxELEM>
    """
    # 1. Transform 2D memref types memref<N x F x elem> where N >= tile_size
    pattern_2d = re.compile(r"\bmemref<(\d+)x(\d+)x([a-zA-Z][a-zA-Z0-9_]*)>")

    def repl_2d(m):
        n = int(m.group(1))
        f = int(m.group(2))
        elem = m.group(3)
        if n >= tile_size and n % tile_size == 0:
            outer = n // tile_size
            return f"memref<{outer}x{f}x{tile_size}x{elem}>"
        return m.group(0)

    mlir_code = pattern_2d.sub(repl_2d, mlir_code)

    # 2. Transform 1D memref types memref<N x elem> where N >= tile_size
    pattern_1d = re.compile(r"\bmemref<(\d+)x([a-zA-Z][a-zA-Z0-9_]*)>")

    def repl_1d(m):
        n = int(m.group(1))
        elem = m.group(2)
        if n >= tile_size and n % tile_size == 0 and elem != "i8":
            outer = n // tile_size
            return f"memref<{outer}x{tile_size}x{elem}>"
        return m.group(0)

    mlir_code = pattern_1d.sub(repl_1d, mlir_code)

    # 3. Rewrite memref.load and memref.store indexing for transformed memrefs
    lines = mlir_code.splitlines()
    new_lines = []
    op_id = 0

    load_store_pattern_2d = re.compile(
        r"^(?P<indent>\s*)(?P<result>%\w+\s*=\s*)?(?P<op>memref\.(?:load|store))\s+(?P<args>.+?)\[(?P<idx>%\w+),\s*(?P<field>%\w+|\d+)\]\s*:\s*memref<(?P<outer>\d+)x(?P<f>\d+)x(?P<tile>\d+)x(?P<elem>[a-zA-Z0-9_!]+)>"
    )

    load_store_pattern_1d = re.compile(
        r"^(?P<indent>\s*)(?P<result>%\w+\s*=\s*)?(?P<op>memref\.(?:load|store))\s+(?P<args>.+?)\[(?P<idx>%\w+)\]\s*:\s*memref<(?P<outer>\d+)x(?P<tile>\d+)x(?P<elem>[a-zA-Z0-9_!]+)>"
    )

    for line in lines:
        m2d = load_store_pattern_2d.match(line)
        m1d = load_store_pattern_1d.match(line)
        if m2d:
            op_id += 1
            indent = m2d.group("indent")
            result = m2d.group("result") or ""
            op = m2d.group("op")
            args = m2d.group("args")
            idx = m2d.group("idx")
            field = m2d.group("field")
            outer = m2d.group("outer")
            f = m2d.group("f")
            tile = m2d.group("tile")
            elem = m2d.group("elem")

            tile_val = int(tile)
            c_name = f"%c_tile_{tile_val}_{op_id}"
            idx_clean = idx.lstrip('%')
            outer_name = f"%aosoa_outer_{idx_clean}_{op_id}"
            inner_name = f"%aosoa_inner_{idx_clean}_{op_id}"

            new_lines.append(f"{indent}{c_name} = arith.constant {tile_val} : index")
            new_lines.append(f"{indent}{outer_name} = arith.divui {idx}, {c_name} : index")
            new_lines.append(f"{indent}{inner_name} = arith.remui {idx}, {c_name} : index")

            memref_ty = f"memref<{outer}x{f}x{tile}x{elem}>"
            if op == "memref.load":
                new_lines.append(f"{indent}{result}{op} {args}[{outer_name}, {field}, {inner_name}] : {memref_ty}")
            else:
                new_lines.append(f"{indent}{op} {args}[{outer_name}, {field}, {inner_name}] : {memref_ty}")
        elif m1d:
            op_id += 1
            indent = m1d.group("indent")
            result = m1d.group("result") or ""
            op = m1d.group("op")
            args = m1d.group("args")
            idx = m1d.group("idx")
            outer = m1d.group("outer")
            tile = m1d.group("tile")
            elem = m1d.group("elem")

            tile_val = int(tile)
            c_name = f"%c_tile_{tile_val}_{op_id}"
            idx_clean = idx.lstrip('%')
            outer_name = f"%aosoa_outer_{idx_clean}_{op_id}"
            inner_name = f"%aosoa_inner_{idx_clean}_{op_id}"

            new_lines.append(f"{indent}{c_name} = arith.constant {tile_val} : index")
            new_lines.append(f"{indent}{outer_name} = arith.divui {idx}, {c_name} : index")
            new_lines.append(f"{indent}{inner_name} = arith.remui {idx}, {c_name} : index")

            memref_ty = f"memref<{outer}x{tile}x{elem}>"
            if op == "memref.load":
                new_lines.append(f"{indent}{result}{op} {args}[{outer_name}, {inner_name}] : {memref_ty}")
            else:
                new_lines.append(f"{indent}{op} {args}[{outer_name}, {inner_name}] : {memref_ty}")
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def apply_conflict_padding(mlir_code: str, pad_amount: int = 1, min_stride_multiple: int = 16) -> str:
    """
    Insert compile-time padding for 2D/3D memref tile strides to eliminate GPU
    shared memory bank conflicts and CPU cache set / 4K aliasing.

    For 2D `memref<M x N x T>` where N >= min_stride_multiple and N % min_stride_multiple == 0:
      Padded type: `memref<M x (N + pad_amount) x T>`
    For 3D `memref<D1 x D2 x D3 x T>` where D3 >= min_stride_multiple and D3 % min_stride_multiple == 0:
      Padded type: `memref<D1 x D2 x (D3 + pad_amount) x T>`
    """
    pattern_3d = re.compile(r"\bmemref<(\d+)x(\d+)x(\d+)x([a-zA-Z][a-zA-Z0-9_]*)>")

    def repl_3d(m):
        d1, d2, d3, elem = m.group(1), m.group(2), int(m.group(3)), m.group(4)
        if d3 >= min_stride_multiple and d3 % min_stride_multiple == 0:
            padded_d3 = d3 + pad_amount
            return f"memref<{d1}x{d2}x{padded_d3}x{elem}>"
        return m.group(0)

    mlir_code = pattern_3d.sub(repl_3d, mlir_code)

    pattern_2d = re.compile(r"\bmemref<(\d+)x(\d+)x([a-zA-Z][a-zA-Z0-9_]*)>")

    def repl_2d(m):
        m_dim, n_dim, elem = m.group(1), int(m.group(2)), m.group(3)
        if n_dim >= min_stride_multiple and n_dim % min_stride_multiple == 0:
            padded_n = n_dim + pad_amount
            return f"memref<{m_dim}x{padded_n}x{elem}>"
        return m.group(0)

    mlir_code = pattern_2d.sub(repl_2d, mlir_code)

    return mlir_code


def apply_swizzled_indexing(mlir_code: str, tile_width: int = 16) -> str:
    """
    Apply XOR swizzled memory indexing for non-major dimension accesses on 2D memrefs
    to enable contiguous/bank-conflict-free SIMD memory loads/stores.

    Transforms accesses of form `memref.load %arr[%row, %col] : memref<MxNxT>`
    on 2D memref structures automatically:
      %mask = arith.constant (tile_width - 1) : index
      %row_mod = arith.andi %row, %mask : index
      %swizzled_col = arith.xori %col, %row_mod : index
      memref.load %arr[%row, %swizzled_col] : memref<MxNxT>
    """
    lines = mlir_code.splitlines()
    new_lines = []
    mask_val = tile_width - 1
    op_id = 0

    pattern_2d_access = re.compile(
        r"^(?P<indent>\s*)(?P<result>%\w+\s*=\s*)?(?P<op>memref\.(?:load|store))\s+(?P<args>.+?)\[(?P<row>%\w+),\s*(?P<col>%\w+)\](?P<rest>.*:\s*memref<\d+x\d+x[a-zA-Z0-9_!]+>.*)"
    )

    for line in lines:
        m = pattern_2d_access.match(line)
        if m:
            op_id += 1
            indent = m.group("indent")
            result = m.group("result") or ""
            op = m.group("op")
            args = m.group("args")
            row = m.group("row")
            col = m.group("col")
            rest = m.group("rest")

            row_clean = row.lstrip("%")
            col_clean = col.lstrip("%")
            mask_name = f"%c_mask_{tile_width}_{op_id}"
            row_mod_name = f"%swiz_mod_{row_clean}_{op_id}"
            swiz_col_name = f"%swiz_col_{col_clean}_{op_id}"

            new_lines.append(f"{indent}{mask_name} = arith.constant {mask_val} : index")
            new_lines.append(f"{indent}{row_mod_name} = arith.andi {row}, {mask_name} : index")
            new_lines.append(f"{indent}{swiz_col_name} = arith.xori {col}, {row_mod_name} : index")

            if op == "memref.load":
                new_lines.append(f"{indent}{result}{op} {args}[{row}, {swiz_col_name}]{rest}")
            else:
                new_lines.append(f"{indent}{op} {args}[{row}, {swiz_col_name}]{rest}")
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


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
