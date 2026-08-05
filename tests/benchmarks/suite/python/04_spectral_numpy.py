#!/usr/bin/env python3
"""Spectral norm benchmark using NumPy.
Power iteration with vectorized operations.
"""
import numpy as np
import time

def A(i, j):
    """Matrix element A[i,j] = 1 / ((i+j)(i+j+1)/2 + i + 1)"""
    return 1.0 / ((i + j) * (i + j + 1) // 2 + i + 1)

def create_A_matrix(n):
    """Create the full matrix (vectorized)."""
    i, j = np.ogrid[0:n, 0:n]
    return 1.0 / ((i + j) * (i + j + 1) // 2 + i + 1)

def spectral_norm_numpy(n):
    """Compute spectral norm using NumPy."""
    # Create matrix
    A_mat = create_A_matrix(n)
    
    # Initial vector
    u = np.ones(n)
    
    # Power iteration
    for _ in range(10):
        v = A_mat @ u           # A * u
        v = A_mat.T @ v         # A^T * (A * u)
        u = A_mat @ v           # A * (A^T * A * u)  
        u = A_mat.T @ u         # A^T * ...
    
    # Compute norm
    v = A_mat @ u
    vBv = np.dot(v, A_mat.T @ v)
    vv = np.dot(v, v)
    
    return np.sqrt(vBv / vv)

def main():
    print("=" * 50)
    print("  SPECTRAL NORM BENCHMARK - Python (NumPy)")
    print("=" * 50)
    print()
    
    for n in [500, 1000, 2000, 3000]:
        start = time.perf_counter()
        result = spectral_norm_numpy(n)
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        
        print(f"N = {n}")
        print(f"  Spectral norm: {result:.9f}")
        print(f"  Time: {elapsed_ms:.2f} ms")
        print()

if __name__ == "__main__":
    main()
