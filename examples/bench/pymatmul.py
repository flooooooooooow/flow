import time

def benchmark_matmul_python(M, N, K):
    # naive Python matmul for small sizes
    A = [[1.0 for _ in range(K)] for _ in range(M)]
    B = [[2.0 for _ in range(N)] for _ in range(K)]
    C = [[0.0 for _ in range(N)] for _ in range(M)]

    start = time.time()
    for m in range(M):
        for k in range(K):
            a = A[m][k]
            for n in range(N):
                C[m][n] += a * B[k][n]
    end = time.time()

    secs = end - start
    if secs <= 0:
        return 0.0
    gflops = (2.0 * M * N * K) / secs / 1e9
    return gflops
