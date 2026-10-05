# Dense matrix multiply, naive i-j-k triple loop, 300x300 doubles.
# Same algorithm and size as matmul.flow. Plain CPython, flat lists.
import time

N = 300


def matmul(a, b, c, n):
    for i in range(n):
        for j in range(n):
            s = 0.0
            for k in range(n):
                s = s + a[i * n + k] * b[k * n + j]
            c[i * n + j] = s


def main():
    a = [0.0] * (N * N)
    b = [0.0] * (N * N)
    c = [0.0] * (N * N)

    for i in range(N):
        for j in range(N):
            a[i * N + j] = 0.001 * (i + j)
            b[i * N + j] = 0.001 * (i - j)

    t0 = time.perf_counter()
    matmul(a, b, c, N)
    secs = time.perf_counter() - t0

    check = 0.0
    for i in range(N * N):
        check = check + c[i]

    print("result %.6f" % check)
    print("seconds %.9f" % secs)


if __name__ == "__main__":
    main()
