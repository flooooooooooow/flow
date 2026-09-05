import time
import numpy as np

def benchmark_gemm(size):
    print(f"Benchmarking GEMM for size {size}x{size}")
    
    # 1. Naive Python loops (simulating naive CUDA kernel behavior on CPU/GPU without tiling)
    # We will just do a very small one or estimate to avoid taking hours.
    # A purely naive O(N^3) in python would be extremely slow, so we'll simulate the FLOPs.
    flops = 2.0 * (size ** 3)
    
    print("  Note: Naive implementation on CPU is too slow for large matrices. Simulating bounds...")
    
    # 2. Optimized BLAS via NumPy (simulating cuBLAS / CUTLASS performance bounds)
    A = np.random.rand(size, size).astype(np.float32)
    B = np.random.rand(size, size).astype(np.float32)
    
    # Warmup
    _ = np.dot(A, B)
    
    start_time = time.time()
    for _ in range(10):
        C = np.dot(A, B)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 10.0
    tflops = (flops / avg_time) / 1e12
    
    print(f"  Optimized BLAS time: {avg_time:.5f}s ({tflops:.2f} TFLOPS equivalent)")
    
    return avg_time

if __name__ == "__main__":
    benchmark_gemm(1024)
    benchmark_gemm(4096)
