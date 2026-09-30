# Spectral norm, from the Computer Language Benchmarks Game.
# Same algorithm and size as spectral.flow. Plain CPython.
import math
import time

N = 500


def A(i, j):
    return 1.0 / (((i + j) * (i + j + 1)) // 2 + i + 1)


def mult_Av(v, Av, n):
    for i in range(n):
        s = 0.0
        for j in range(n):
            s = s + A(i, j) * v[j]
        Av[i] = s


def mult_Atv(v, Atv, n):
    for i in range(n):
        s = 0.0
        for j in range(n):
            s = s + A(j, i) * v[j]
        Atv[i] = s


def mult_AtAv(v, AtAv, tmp, n):
    mult_Av(v, tmp, n)
    mult_Atv(tmp, AtAv, n)


def main():
    u = [1.0] * N
    v = [0.0] * N
    tmp = [0.0] * N

    t0 = time.perf_counter()

    for _ in range(10):
        mult_AtAv(u, v, tmp, N)
        mult_AtAv(v, u, tmp, N)

    vBv = 0.0
    vv = 0.0
    for i in range(N):
        vBv = vBv + u[i] * v[i]
        vv = vv + v[i] * v[i]
    result = math.sqrt(vBv / vv)

    secs = time.perf_counter() - t0

    print("result %.9f" % result)
    print("seconds %.9f" % secs)


if __name__ == "__main__":
    main()
