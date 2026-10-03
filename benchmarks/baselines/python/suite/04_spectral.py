#!/usr/bin/env python3
"""Spectral Norm Benchmark - From the Computer Language Benchmarks Game"""
import time
import math

def A(i, j):
    return 1.0 / ((i + j) * (i + j + 1) // 2 + i + 1)

def mult_Av(v, n):
    Av = [0.0] * n
    for i in range(n):
        s = 0.0
        for j in range(n):
            s += A(i, j) * v[j]
        Av[i] = s
    return Av

def mult_Atv(v, n):
    Atv = [0.0] * n
    for i in range(n):
        s = 0.0
        for j in range(n):
            s += A(j, i) * v[j]
        Atv[i] = s
    return Atv

def mult_AtAv(v, n):
    tmp = mult_Av(v, n)
    return mult_Atv(tmp, n)

def spectral_norm(n):
    u = [1.0] * n
    
    for _ in range(10):
        v = mult_AtAv(u, n)
        u = mult_AtAv(v, n)
    
    vBv = sum(u[i] * v[i] for i in range(n))
    vv = sum(v[i] * v[i] for i in range(n))
    
    return math.sqrt(vBv / vv)

def main():
    print("==============================================")
    print("  SPECTRAL NORM BENCHMARK - Python")
    print("==============================================")
    print()
    
    # Use smaller sizes for Python
    sizes = [100, 500, 1000, 2000, 3000]
    
    for n in sizes:
        print(f"N = {n}: ", end="", flush=True)
        
        start = time.perf_counter()
        result = spectral_norm(n)
        elapsed = time.perf_counter() - start
        
        print(f"{result:.9f} | {elapsed:.3f} sec")
    
    print()
    print("Benchmark complete.")

if __name__ == "__main__":
    main()
