#!/usr/bin/env python3
"""Fibonacci benchmark - with memoization (idiomatic Python).
Pure recursive fib is a bad benchmark for Python.
"""
import time
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

def main():
    print("=" * 50)
    print("  FIBONACCI BENCHMARK - Python (memoized)")
    print("=" * 50)
    print()
    
    for n in [40, 45, 47]:
        fib.cache_clear()  # Reset cache for fair timing
        start = time.perf_counter()
        result = fib(n)
        end = time.perf_counter()
        print(f"fib({n}) = {result}")
        print(f"  Time: {(end - start) * 1000:.3f} ms")
        print()

if __name__ == "__main__":
    main()
