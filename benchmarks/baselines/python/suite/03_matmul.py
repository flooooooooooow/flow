#!/usr/bin/env python3
"""Matrix Multiplication Benchmark - Tests loop performance"""
import time

def matmul(A, B, N):
    C = [[0.0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            s = 0.0
            for k in range(N):
                s += A[i][k] * B[k][j]
            C[i][j] = s
    return C

def matmul_transposed(A, BT, N):
    C = [[0.0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            s = 0.0
            for k in range(N):
                s += A[i][k] * BT[j][k]
            C[i][j] = s
    return C

def init_matrix(N, seed):
    return [[(i * N + j + 1) * seed for j in range(N)] for i in range(N)]

def transpose(M, N):
    return [[M[i][j] for i in range(N)] for j in range(N)]

def checksum(M, N):
    return sum(sum(row) for row in M)

def calculate_gflops(N, time_sec):
    flops = 2.0 * N * N * N
    return flops / time_sec / 1e9

def main():
    print("==============================================")
    print("  MATRIX MULTIPLICATION BENCHMARK - Python")
    print("==============================================")
    print()
    
    # Use smaller sizes for Python
    sizes = [64, 128, 256, 512]
    
    for N in sizes:
        print(f"Matrix size: {N}x{N}")
        
        A = init_matrix(N, 0.0001)
        B = init_matrix(N, 0.0002)
        BT = transpose(B, N)
        
        # Naive version
        start1 = time.perf_counter()
        C = matmul(A, B, N)
        time1 = time.perf_counter() - start1
        gflops1 = calculate_gflops(N, time1)
        check1 = checksum(C, N)
        
        print(f"  Naive:      {time1:.3f} sec | {gflops1:.4f} GFLOPS | checksum: {check1:.6f}")
        
        # Transposed version
        start2 = time.perf_counter()
        C = matmul_transposed(A, BT, N)
        time2 = time.perf_counter() - start2
        gflops2 = calculate_gflops(N, time2)
        check2 = checksum(C, N)
        
        print(f"  Transposed: {time2:.3f} sec | {gflops2:.4f} GFLOPS | checksum: {check2:.6f}")
        print(f"  Speedup: {time1 / time2:.2f}x")
        print()
    
    print("Benchmark complete.")

if __name__ == "__main__":
    main()
