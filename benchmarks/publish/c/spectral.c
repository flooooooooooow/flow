/* Spectral norm, from the Computer Language Benchmarks Game.
 * Same algorithm and size as spectral.flow. */
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <time.h>

#define N 500

static double A(int i, int j) {
    double div = ((i + j) * (i + j + 1)) / 2 + i + 1;
    return 1.0 / div;
}

static void mult_Av(double *v, double *Av, int n) {
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum = sum + A(i, j) * v[j];
        }
        Av[i] = sum;
    }
}

static void mult_Atv(double *v, double *Atv, int n) {
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum = sum + A(j, i) * v[j];
        }
        Atv[i] = sum;
    }
}

static void mult_AtAv(double *v, double *AtAv, double *tmp, int n) {
    mult_Av(v, tmp, n);
    mult_Atv(tmp, AtAv, n);
}

static double u[N];
static double v[N];
static double tmp[N];

int main(void) {
    for (int i = 0; i < N; i++) {
        u[i] = 1.0;
    }

    uint64_t t0 = clock_gettime_nsec_np(CLOCK_MONOTONIC);

    for (int i = 0; i < 10; i++) {
        mult_AtAv(u, v, tmp, N);
        mult_AtAv(v, u, tmp, N);
    }

    double vBv = 0.0, vv = 0.0;
    for (int i = 0; i < N; i++) {
        vBv = vBv + u[i] * v[i];
        vv = vv + v[i] * v[i];
    }
    double result = sqrt(vBv / vv);

    uint64_t t1 = clock_gettime_nsec_np(CLOCK_MONOTONIC);
    double secs = (t1 - t0) / 1e9;

    printf("result %.9f\n", result);
    printf("seconds %.9f\n", secs);
    return 0;
}
