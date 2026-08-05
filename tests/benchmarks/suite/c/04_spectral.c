/* Spectral Norm Benchmark - From the Computer Language Benchmarks Game */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

double A(int i, int j) {
    /* A[i,j] = 1.0 / ((i+j)*(i+j+1)/2 + i + 1) */
    return 1.0 / ((double)((i + j) * (i + j + 1)) / 2.0 + i + 1);
}

void mult_Av(double* v, double* Av, int n) {
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum += A(i, j) * v[j];
        }
        Av[i] = sum;
    }
}

void mult_Atv(double* v, double* Atv, int n) {
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum += A(j, i) * v[j];
        }
        Atv[i] = sum;
    }
}

void mult_AtAv(double* v, double* AtAv, double* tmp, int n) {
    mult_Av(v, tmp, n);
    mult_Atv(tmp, AtAv, n);
}

double spectral_norm(int n) {
    double* u = (double*)malloc(n * sizeof(double));
    double* v = (double*)malloc(n * sizeof(double));
    double* tmp = (double*)malloc(n * sizeof(double));
    
    for (int i = 0; i < n; i++) {
        u[i] = 1.0;
    }
    
    for (int i = 0; i < 10; i++) {
        mult_AtAv(u, v, tmp, n);
        mult_AtAv(v, u, tmp, n);
    }
    
    double vBv = 0.0, vv = 0.0;
    for (int i = 0; i < n; i++) {
        vBv += u[i] * v[i];
        vv += v[i] * v[i];
    }
    
    free(u);
    free(v);
    free(tmp);
    
    return sqrt(vBv / vv);
}

int main() {
    printf("==============================================\n");
    printf("  SPECTRAL NORM BENCHMARK - C\n");
    printf("==============================================\n\n");
    
    int sizes[] = {100, 500, 1000, 2000, 5500};
    
    for (int s = 0; s < 5; s++) {
        int n = sizes[s];
        
        printf("N = %d: ", n);
        
        clock_t start = clock();
        double result = spectral_norm(n);
        clock_t end = clock();
        
        double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
        
        printf("%.9f | %.3f sec\n", result, elapsed);
    }
    
    printf("\nBenchmark complete.\n");
    return 0;
}
