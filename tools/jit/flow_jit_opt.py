#!/usr/bin/env python3
"""
FLOW JIT with MLIR Optimizations
Similar to flow_jit_pipeline.py but with enhanced optimizations
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flow.transpiler import main as transpiler_main
from flow.mlir_optimizer import MLIROptimizer

def run_flow_jit_optimized(flow_file: str, opt_level: str = "O2"):
    """Run FLOW file with MLIR optimizations."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 1) Generate MLIR
        mlir_file = tmpdir / "out.mlir"
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent.parent / "src")
        
        result = subprocess.run([
            sys.executable, "-m", "flow.transpiler",
            flow_file, "--mlir", "--debug-info",
            "-o", str(mlir_file)
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent, env=env)
        
        if result.returncode != 0:
            print(f"MLIR generation failed: {result.stderr}")
            return result.returncode
        
        # 2) Optimize MLIR
        opt_file = tmpdir / "out.opt.mlir"
        optimizer = MLIROptimizer()
        opt_result = optimizer.optimize(
            str(mlir_file), str(opt_file),
            enable_vectorization=True,
            enable_loop_fusion=True,
            optimization_level=opt_level
        )
        
        if opt_result != 0:
            print(f"MLIR optimization failed")
            return opt_result
        
        # 3) Lower MLIR → LLVM IR
        lowered_mlir_file = tmpdir / "out.lowered.mlir"
        mlir_opt = "/opt/homebrew/opt/llvm/bin/mlir-opt"
        p2 = subprocess.run([
            mlir_opt,
            "--mlir-print-op-on-diagnostic=false",
            "--pass-pipeline=builtin.module(func.func(convert-scf-to-cf),convert-cf-to-llvm,func.func(convert-index-to-llvm,convert-arith-to-llvm,convert-math-to-llvm),convert-func-to-llvm,finalize-memref-to-llvm,convert-vector-to-llvm,reconcile-unrealized-casts)",
            str(opt_file),
            "-o",
            str(lowered_mlir_file),
        ], capture_output=True, text=True)
        
        if p2.returncode != 0:
            print(f"MLIR lowering failed: {p2.stderr}")
            return p2.returncode
        
        # 4) LLVM IR
        ll_file = tmpdir / "out.ll"
        mlir_translate = "/opt/homebrew/opt/llvm/bin/mlir-translate"
        p3 = subprocess.run([mlir_translate, "--mlir-to-llvmir", str(lowered_mlir_file), "-o", str(ll_file)], capture_output=True, text=True)
        
        if p3.returncode != 0:
            print(f"LLVM IR generation failed: {p3.stderr}")
            return p3.returncode
        
        # 5) Compile and run
        exe_file = tmpdir / "out"
        clang = "/opt/homebrew/opt/llvm/bin/clang"
        p4 = subprocess.run([
            clang, "-g", "-O" + opt_level[1:], str(ll_file), "-o", str(exe_file)
        ], capture_output=True, text=True)
        
        if p4.returncode != 0:
            print(f"Compilation failed: {p4.stderr}")
            return p4.returncode
        
        # 6) Run executable
        p5 = subprocess.run([str(exe_file)], capture_output=True, text=True)
        print(p5.stdout, end='')
        if p5.stderr:
            print(p5.stderr, end='', file=sys.stderr)
        
        return p5.returncode

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python flow_jit_opt.py <file.flow> [--O0|--O1|--O2|--O3]")
        sys.exit(1)
    
    flow_file = sys.argv[1]
    opt_level = "O2"
    
    for arg in sys.argv[2:]:
        if arg.startswith("--O"):
            opt_level = arg[2:]
    
    sys.exit(run_flow_jit_optimized(flow_file, opt_level))
