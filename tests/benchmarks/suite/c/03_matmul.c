/* Matrix Multiplication Benchmark - Tests loop performance and cache efficiency */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void matmul(double* A, double* B, double* C, int N) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            double sum = 0.0;
            for (int k = 0; k < N; k++) {
                sum += A[i * N + k] * B[k * N + j];
            }
            C[i * N + j] = sum;
        }
    }
}

void matmul_transposed(double* A, double* B, double* C, int N) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            double sum = 0.0;
            for (int k = 0; k < N; k++) {
                sum += A[i * N + k] * B[j * N + k];
            }
            C[i * N + j] = sum;
        }
    }
}

void init_matrix(double* M, int N, double seed) {
    for (int i = 0; i < N * N; i++) {
        M[i] = (i + 1) * seed;
    }
}

void transpose(double* M, double* MT, int N) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            MT[j * N + i] = M[i * N + j];
        }
    }
}

double checksum(double* M, int N) {
    double sum = 0.0;
    for (int i = 0; i < N * N; i++) {
        sum += M[i];
    }
    return sum;
}

double calculate_gflops(int N, double time_sec) {
    double flops = 2.0 * N * N * N;
    return flops / time_sec / 1e9;
}

int main() {
    printf("==============================================\n");
    printf("  MATRIX MULTIPLICATION BENCHMARK - C\n");
    printf("==============================================\n\n");
    
    int sizes[] = {128, 256, 512, 1024};
    
    for (int s = 0; s < 4; s++) {
        int N = sizes[s];
        int size = N * N;
        
        printf("Matrix size: %dx%d\n", N, N);
        
        double* A = (double*)malloc(size * sizeof(double));
        double* B = (double*)malloc(size * sizeof(double));
        double* BT = (double*)malloc(size * sizeof(double));
        double* C = (double*)malloc(size * sizeof(double));
        
        init_matrix(A, N, 0.0001);
        init_matrix(B, N, 0.0002);
        transpose(B, BT, N);
        
        /* Naive version */
        clock_t start1 = clock();
        matmul(A, B, C, N);
        clock_t end1 = clock();
        double time1 = (double)(end1 - start1) / CLOCKS_PER_SEC;
        double gflops1 = calculate_gflops(N, time1);
        double check1 = checksum(C, N);
        
        printf("  Naive:      %.3f sec | %.2f GFLOPS | checksum: %.6f\n",
               time1, gflops1, check1);
        
        /* Transposed version */
        clock_t start2 = clock();
        matmul_transposed(A, BT, C, N);
        clock_t end2 = clock();
        double time2 = (double)(end2 - start2) / CLOCKS_PER_SEC;
        double gflops2 = calculate_gflops(N, time2);
        double check2 = checksum(C, N);
        
        printf("  Transposed: %.3f sec | %.2f GFLOPS | checksum: %.6f\n",
               time2, gflops2, check2);
        
        printf("  Speedup: %.2fx\n\n", time1 / time2);
        
        free(A);
        free(B);
        free(BT);
        free(C);
    }
    
    printf("Benchmark complete.\n");
    return 0;
}
