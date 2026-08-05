#!/usr/bin/env python3
"""Fibonacci Benchmark - Tests recursive function call overhead"""
import time

def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

def benchmark(n: int, iterations: int) -> float:
    start = time.perf_counter()
    
    result = 0
    for _ in range(iterations):
        result = fib(n)
    
    elapsed = time.perf_counter() - start
    
    print(f"  fib({n}) = {result} | {elapsed:.4f} sec | {iterations / elapsed:.2f} calls/sec")
    return elapsed

def main():
    print("==============================================")
    print("  FIBONACCI BENCHMARK (Naive Recursive) - Python")
    print("==============================================")
    print()
    
    # Warm up
    fib(20)
    
    print("N=35 (1 iteration):")
    benchmark(35, 1)
    
    print()
    print("N=40 (1 iteration):")
    benchmark(40, 1)
    
    print()
    print("N=30 (10 iterations):")
    benchmark(30, 10)
    
    print()
    print("Benchmark complete.")

if __name__ == "__main__":
    main()
