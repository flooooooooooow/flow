# CPython twin of benchmarks/cross_harness/runtime/allocation.

n = 50000
checksum = 0
for _ in range(n):
    buf = bytearray(64)
    buf[0] = 1
    buf[63] = 2
    checksum += buf[0] + buf[63]
if checksum != 150000:
    raise ValueError("checksum mismatch")
print("allocations:", n)
print("copies: 0")
