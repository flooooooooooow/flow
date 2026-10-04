# CPython twin of benchmarks/cross_harness/memory/peak_rss.

n = 4194304
buf = bytearray(n)
for i in range(0, n, 4096):
    buf[i] = i % 251
if buf[0] != 0:
    raise SystemExit(1)
print("allocations: 1")
print("copies: 0")
