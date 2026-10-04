# CPython twin of benchmarks/cross_harness/memory/allocation_copy.

n = 256
size = 1024
copies = 0
for i in range(n):
    src = bytearray(size)
    src[0] = i % 251
    src[1023] = 7
    dst = bytearray(src)
    copies += size
    if dst[0] + dst[1023] < 0:
        raise SystemExit(1)
print("allocations:", n * 2)
print("copies:", copies)
