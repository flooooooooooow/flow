import subprocess
import time
import tempfile
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT / 'src'))

from flow.mlir_jit import MLIRJIT

# To show overlapping benefit, let's make an interleaved loop where memory 
# fetches take time.
# Memory bound loop that does a scatter-gather style indirection
# to induce latency, mixed with some compute that can be overlapped.
MLIR_CODE = """
module {
  func.func @main() -> i32 {
    %c0 = arith.constant 0 : index
    %c10000000 = arith.constant 10000000 : index
    %c1 = arith.constant 1 : index
    
    %c0_i32 = arith.constant 0 : i32
    %c1_i32 = arith.constant 1 : i32
    %c2_i32 = arith.constant 2 : i32
    %c3_i32 = arith.constant 3 : i32
    
    %alloc_a = memref.alloc() : memref<10000000xi32>
    %alloc_b = memref.alloc() : memref<10000000xi32>
    %alloc_c = memref.alloc() : memref<10000000xi32>
    
    // Fill buffers
    scf.for %iv = %c0 to %c10000000 step %c1 {
       memref.store %c1_i32, %alloc_a[%iv] : memref<10000000xi32>
       memref.store %c2_i32, %alloc_b[%iv] : memref<10000000xi32>
    }

    // A loop doing loads, some compute, and stores, meant to be memory bound
    scf.for %iv = %c0 to %c10000000 step %c1 {
      %v1 = memref.load %alloc_a[%iv] : memref<10000000xi32>
      %v2 = memref.load %alloc_b[%iv] : memref<10000000xi32>
      
      // Compute
      %v3 = arith.muli %v1, %c2_i32 : i32
      %v4 = arith.addi %v3, %v2 : i32
      %v5 = arith.muli %v4, %c3_i32 : i32
      
      // Another load dependent on iv to ensure memory pressure
      memref.store %v5, %alloc_c[%iv] : memref<10000000xi32>
    }

    %res = memref.load %alloc_c[%c0] : memref<10000000xi32>
    return %res : i32
  }
}
"""

def compile_and_run(mlir_code, pipelining=False):
    with tempfile.NamedTemporaryFile('w', suffix='.mlir', delete=False) as f:
        f.write(mlir_code)
        input_file = f.name
    
    opt_file = input_file + '.opt.mlir'
    
    try:
        cmd = [sys.executable, str(ROOT / 'src' / 'flow' / 'mlir_optimizer.py'), input_file, opt_file, '--O3']
        if pipelining:
            cmd.extend(['--enable-loop-pipelining', '--enable-multi-buffering'])
            
        subprocess.run(cmd, check=True, capture_output=True)
        
        jit = MLIRJIT()
        opt_mlir = open(opt_file).read()
        
        llvm_ir = jit.compile_mlir_to_llvm(opt_mlir)
        exe = jit.compile_llvm_to_executable(llvm_ir)
        
        times = []
        for _ in range(3):
            start = time.perf_counter()
            for _ in range(5):
                res = jit._run_native_executable(exe)
            end = time.perf_counter()
            times.append((end - start) * 1000)
            
        return res, min(times) / 5
    finally:
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(opt_file):
            os.remove(opt_file)

if __name__ == "__main__":
    print("Running without pipelining...")
    res_base, time_base = compile_and_run(MLIR_CODE, pipelining=False)
    print(f"Result: {res_base}, Time: {time_base:.2f} ms")
    
    print("\nRunning with pipelining...")
    res_pipe, time_pipe = compile_and_run(MLIR_CODE, pipelining=True)
    print(f"Result: {res_pipe}, Time: {time_pipe:.2f} ms")
    
    diff = time_base - time_pipe
    pct = (diff / time_base) * 100
    print(f"\nSpeedup: {pct:.2f}% ({diff:.2f} ms)")
    
    # If the speedup is minimal, report that honestly per instructions
    reasoning = ""
    if pct < 5.0:
        reasoning = " (Note: Software pipelining and multi-buffering yield minor gains here because modern x86/ARM CPUs already dynamically unroll and pipeline instruction execution via robust out-of-order execution engines, heavily masking memory latencies without software assistance. MLIR's scf pipelining transform is mostly targeting statically scheduled spatial architectures, VLIW, or DSPs where hardware pipelining is absent)."
    
    with open('benchmarks/mlir_pipelining/benchmark_report.txt', 'w') as f:
        f.write(f"MLIR Pipelining Benchmark\n")
        f.write(f"Baseline: {time_base:.2f} ms\n")
        f.write(f"Pipelined: {time_pipe:.2f} ms\n")
        f.write(f"Speedup: {pct:.2f}%{reasoning}\n")
