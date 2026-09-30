#!/usr/bin/env python3
"""Matrix multiplication using NumPy.
This uses BLAS under the hood - the real way to do matmul in Python.
"""
import numpy as np
import time

def main():
    print("=" * 50)
    print("  MATRIX MULTIPLY BENCHMARK - Python (NumPy)")
    print("=" * 50)
    print()
    print("Using np.dot() which calls optimized BLAS")
    print()
    
    for n in [256, 512, 1024, 2048]:
        # Create random matrices
        np.random.seed(42)
        A = np.random.rand(n, n).astype(np.float64)
        B = np.random.rand(n, n).astype(np.float64)
        
        # Warmup
        _ = np.dot(A[:10, :10], B[:10, :10])
        
        # Benchmark
        start = time.perf_counter()
        C = np.dot(A, B)
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        
        # Calculate GFLOPS: 2*N^3 operations for matmul
        flops = 2.0 * n * n * n
        gflops = flops / (end - start) / 1e9
        
        # Checksum
        checksum = C.sum()
        
        print(f"Size: {n}x{n}")
        print(f"  Time: {elapsed_ms:.2f} ms")
        print(f"  GFLOPS: {gflops:.2f}")
        print(f"  Checksum: {checksum:.6f}")
        print()

if __name__ == "__main__":
    main()
