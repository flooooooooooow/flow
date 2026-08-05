/* Sparse Matrix-Vector Multiply (SpMV) Benchmark
 * The classic "compiler killer" - tests irregular memory access,
 * pointer chasing, and cache behavior. Uses CSR format.
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>

void spmv_csr(
    const double* values,
    const int32_t* col_indices,
    const int32_t* row_ptrs,
    const double* x,
    double* y,
    int32_t num_rows
) {
    for (int32_t i = 0; i < num_rows; i++) {
        int32_t row_start = row_ptrs[i];
        int32_t row_end = row_ptrs[i + 1];
        double sum = 0.0;
        
        for (int32_t j = row_start; j < row_end; j++) {
            sum += values[j] * x[col_indices[j]];
        }
        y[i] = sum;
    }
}

void spmv_csr_unrolled(
    const double* values,
    const int32_t* col_indices,
    const int32_t* row_ptrs,
    const double* x,
    double* y,
    int32_t num_rows
) {
    for (int32_t i = 0; i < num_rows; i++) {
        int32_t row_start = row_ptrs[i];
        int32_t row_end = row_ptrs[i + 1];
        int32_t row_len = row_end - row_start;
        
        double sum0 = 0.0, sum1 = 0.0, sum2 = 0.0, sum3 = 0.0;
        
        int32_t unroll_end = row_start + (row_len / 4) * 4;
        int32_t j;
        
        for (j = row_start; j < unroll_end; j += 4) {
            sum0 += values[j] * x[col_indices[j]];
            sum1 += values[j+1] * x[col_indices[j+1]];
            sum2 += values[j+2] * x[col_indices[j+2]];
            sum3 += values[j+3] * x[col_indices[j+3]];
        }
        
        for (; j < row_end; j++) {
            sum0 += values[j] * x[col_indices[j]];
        }
        
        y[i] = sum0 + sum1 + sum2 + sum3;
    }
}

int32_t generate_sparse_matrix(
    double* values,
    int32_t* col_indices,
    int32_t* row_ptrs,
    int32_t n,
    int32_t nnz_per_row,
    uint32_t seed
) {
    uint32_t s = seed;
    int32_t nnz = 0;
    
    for (int32_t i = 0; i < n; i++) {
        row_ptrs[i] = nnz;
        
        for (int32_t k = 0; k < nnz_per_row; k++) {
            s = s * 1664525 + 1013904223;
            col_indices[nnz] = s % n;
            
            s = s * 1664525 + 1013904223;
            values[nnz] = (s % 1000) * 0.001;
            
            nnz++;
        }
    }
    row_ptrs[n] = nnz;
    
    return nnz;
}

void init_vector(double* v, int32_t n, uint32_t seed) {
    uint32_t s = seed;
    for (int32_t i = 0; i < n; i++) {
        s = s * 1664525 + 1013904223;
        v[i] = (s % 1000) * 0.001;
    }
}

double checksum(const double* v, int32_t n) {
    double sum = 0.0;
    for (int32_t i = 0; i < n; i++) {
        sum += v[i];
    }
    return sum;
}

int main() {
    printf("==============================================\n");
    printf("  SpMV BENCHMARK (Sparse Matrix-Vector) - C\n");
    printf("==============================================\n\n");
    printf("CSR format, random sparse matrices\n\n");
    
    int32_t sizes[] = {1000, 2000, 4000, 8000};
    int32_t nnz_per_row = 10;
    
    for (int s = 0; s < 4; s++) {
        int32_t n = sizes[s];
        int32_t max_nnz = n * nnz_per_row;
        
        printf("Matrix: %dx%d, ~%d nnz/row, %d total nnz\n", 
               n, n, nnz_per_row, max_nnz);
        
        double* values = (double*)malloc(max_nnz * sizeof(double));
        int32_t* col_indices = (int32_t*)malloc(max_nnz * sizeof(int32_t));
        int32_t* row_ptrs = (int32_t*)malloc((n + 1) * sizeof(int32_t));
        double* x = (double*)malloc(n * sizeof(double));
        double* y = (double*)malloc(n * sizeof(double));
        
        int32_t nnz = generate_sparse_matrix(values, col_indices, row_ptrs, n, nnz_per_row, 42);
        init_vector(x, n, 123);
        
        int32_t iterations = 100000 / n + 1;
        
        /* Benchmark basic SpMV */
        clock_t start1 = clock();
        for (int32_t iter = 0; iter < iterations; iter++) {
            spmv_csr(values, col_indices, row_ptrs, x, y, n);
        }
        clock_t end1 = clock();
        double time1 = (double)(end1 - start1) / CLOCKS_PER_SEC;
        double check1 = checksum(y, n);
        double gflops1 = 2.0 * nnz * iterations / time1 / 1e9;
        
        printf("  Basic:    %.3f sec | %.3f GFLOPS | checksum: %.6f\n",
               time1, gflops1, check1);
        
        /* Benchmark unrolled SpMV */
        clock_t start2 = clock();
        for (int32_t iter = 0; iter < iterations; iter++) {
            spmv_csr_unrolled(values, col_indices, row_ptrs, x, y, n);
        }
        clock_t end2 = clock();
        double time2 = (double)(end2 - start2) / CLOCKS_PER_SEC;
        double check2 = checksum(y, n);
        double gflops2 = 2.0 * nnz * iterations / time2 / 1e9;
        
        printf("  Unrolled: %.3f sec | %.3f GFLOPS | checksum: %.6f\n",
               time2, gflops2, check2);
        
        printf("  Speedup: %.2fx\n\n", time1 / time2);
        
        free(values);
        free(col_indices);
        free(row_ptrs);
        free(x);
        free(y);
    }
    
    printf("Benchmark complete.\n");
    return 0;
}
