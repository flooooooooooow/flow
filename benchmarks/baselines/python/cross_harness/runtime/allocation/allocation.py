# CPython twin of benchmarks/cross_harness/runtime/allocation.

n = 1000
for _ in range(n):
    buf = bytearray(64)
    buf[0] = 1
    buf[63] = 2
print("allocations:", n)
print("copies: 0")
