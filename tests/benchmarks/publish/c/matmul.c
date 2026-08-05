/* Dense matrix multiply, naive i-j-k triple loop, 300x300 doubles.
 * Same algorithm and size as matmul.flow. */
#include <stdio.h>
#include <stdint.h>
#include <time.h>

#define N 300

static double A[N * N];
static double B[N * N];
static double C[N * N];

static void matmul(double *a, double *b, double *c, int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) {
                sum = sum + a[i * n + k] * b[k * n + j];
            }
            c[i * n + j] = sum;
        }
    }
}

int main(void) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            A[i * N + j] = 0.001 * (i + j);
            B[i * N + j] = 0.001 * (i - j);
        }
    }

    uint64_t t0 = clock_gettime_nsec_np(CLOCK_MONOTONIC);
    matmul(A, B, C, N);
    uint64_t t1 = clock_gettime_nsec_np(CLOCK_MONOTONIC);
    double secs = (t1 - t0) / 1e9;

    double check = 0.0;
    for (int i = 0; i < N * N; i++) {
        check = check + C[i];
    }

    printf("result %.6f\n", check);
    printf("seconds %.9f\n", secs);
    return 0;
}
