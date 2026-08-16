import timeit
import re

asm = "mov rax, 1\n" * 10000 + "ymm0\n"

patterns = [
    r"\bymm\d+",
    r"\bzmm\d+",
    r"\bv(add|mul|fmadd)ps\b",
    r"\b(vpadd|vpmul)\w+\b",
]

def test_unoptimized():
    if any(re.search(p, asm) for p in patterns):
        pass

def test_optimized():
    compiled_patterns = [re.compile(p) for p in patterns]
    if any(p.search(asm) for p in compiled_patterns):
        pass

print("Unoptimized:", timeit.timeit(test_unoptimized, number=100))
print("Optimized:", timeit.timeit(test_optimized, number=100))

def test_unoptimized2():
    interesting = []
    for line in asm.splitlines():
        if re.search(r"\.4s\b|\bldr\s+q|\bstr\s+q|\bld1\b|\bst1\b|\bymm\d+|\bzmm\d+|\bv(add|mul|fmadd)ps\b", line):
            interesting.append(line)
            if len(interesting) >= 30:
                break

def test_optimized2():
    interesting = []
    pattern = re.compile(r"\.4s\b|\bldr\s+q|\bstr\s+q|\bld1\b|\bst1\b|\bymm\d+|\bzmm\d+|\bv(add|mul|fmadd)ps\b")
    for line in asm.splitlines():
        if pattern.search(line):
            interesting.append(line)
            if len(interesting) >= 30:
                break

print("Unoptimized 2:", timeit.timeit(test_unoptimized2, number=100))
print("Optimized 2:", timeit.timeit(test_optimized2, number=100))
