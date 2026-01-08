#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <string.h>

// High-resolution timer
double get_time() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

// Matrix multiplication (CPU)
void matmul_cpu(float* A, float* B, float* C, int N) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            float sum = 0.0f;
            for (int k = 0; k < N; k++) {
                sum += A[i * N + k] * B[k * N + j];
            }
            C[i * N + j] = sum;
        }
    }
}

// Bubble sort
void bubble_sort(float* arr, int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                float temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

// Quick sort
void quick_sort_recursive(float* arr, int low, int high) {
    if (low < high) {
        float pivot = arr[high];
        int i = low - 1;
        
        for (int j = low; j < high; j++) {
            if (arr[j] < pivot) {
                i++;
                float temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }
        
        float temp = arr[i + 1];
        arr[i + 1] = arr[high];
        arr[high] = temp;
        
        int pi = i + 1;
        quick_sort_recursive(arr, low, pi - 1);
        quick_sort_recursive(arr, pi + 1, high);
    }
}

void quick_sort(float* arr, int n) {
    quick_sort_recursive(arr, 0, n - 1);
}

// Vector operations
void vector_add(float* a, float* b, float* result, int n) {
    for (int i = 0; i < n; i++) {
        result[i] = a[i] + b[i];
    }
}

void vector_multiply(float* a, float* b, float* result, int n) {
    for (int i = 0; i < n; i++) {
        result[i] = a[i] * b[i];
    }
}

// Fibonacci (recursive)
int fibonacci_recursive(int n) {
    if (n <= 1) return n;
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);
}

// Fibonacci (iterative)
int fibonacci_iterative(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1, c;
    for (int i = 2; i <= n; i++) {
        c = a + b;
        a = b;
        b = c;
    }
    return b;
}

// Prime number test
int is_prime(int n) {
    if (n <= 1) return 0;
    if (n <= 3) return 1;
    if (n % 2 == 0 || n % 3 == 0) return 0;
    
    for (int i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) return 0;
    }
    return 1;
}

// Count primes up to N
int count_primes(int N) {
    int count = 0;
    for (int i = 2; i <= N; i++) {
        if (is_prime(i)) count++;
    }
    return count;
}

// Monte Carlo Pi estimation
double monte_carlo_pi(int samples) {
    int inside_circle = 0;
    srand(time(NULL));
    
    for (int i = 0; i < samples; i++) {
        double x = (double)rand() / RAND_MAX;
        double y = (double)rand() / RAND_MAX;
        if (x * x + y * y <= 1.0) {
            inside_circle++;
        }
    }
    
    return 4.0 * inside_circle / samples;
}

// Benchmark runner
void run_benchmark(const char* name, void (*func)(void), double* time_taken) {
    double start = get_time();
    func();
    double end = get_time();
    *time_taken = end - start;
    printf("%-30s: %.6f seconds\n", name, *time_taken);
}

// Benchmark data structures
typedef struct {
    float* A;
    float* B;
    float* C;
    int N;
    int size;
} MatrixData;

typedef struct {
    float* arr;
    int n;
} SortData;

// Matrix benchmark
void benchmark_matrices() {
    const int N = 512;
    const int size = N * N;
    
    float* A = malloc(size * sizeof(float));
    float* B = malloc(size * sizeof(float));
    float* C = malloc(size * sizeof(float));
    
    // Initialize matrices
    for (int i = 0; i < size; i++) {
        A[i] = 1.0f;
        B[i] = 2.0f;
        C[i] = 0.0f;
    }
    
    double start = get_time();
    matmul_cpu(A, B, C, N);
    double end = get_time();
    
    printf("Matrix Multiplication (%dx%d): %.6f seconds\n", N, N, end - start);
    printf("Checksum: %.2f\n", C[0] + C[size - 1]);
    
    free(A);
    free(B);
    free(C);
}

// Sorting benchmark
void benchmark_sorting() {
    const int n = 10000;
    float* arr_bubble = malloc(n * sizeof(float));
    float* arr_quick = malloc(n * sizeof(float));
    
    // Initialize arrays
    srand(time(NULL));
    for (int i = 0; i < n; i++) {
        float val = (float)rand() / RAND_MAX * 1000.0f;
        arr_bubble[i] = val;
        arr_quick[i] = val;
    }
    
    double start = get_time();
    bubble_sort(arr_bubble, n);
    double end = get_time();
    printf("Bubble Sort (%d elements): %.6f seconds\n", n, end - start);
    
    start = get_time();
    quick_sort(arr_quick, n);
    end = get_time();
    printf("Quick Sort (%d elements): %.6f seconds\n", n, end - start);
    
    free(arr_bubble);
    free(arr_quick);
}

// Vector operations benchmark
void benchmark_vectors() {
    const int n = 1000000;
    float* a = malloc(n * sizeof(float));
    float* b = malloc(n * sizeof(float));
    float* result = malloc(n * sizeof(float));
    
    // Initialize vectors
    for (int i = 0; i < n; i++) {
        a[i] = (float)i;
        b[i] = (float)(i * 2);
    }
    
    double start = get_time();
    vector_add(a, b, result, n);
    double end = get_time();
    printf("Vector Addition (%d elements): %.6f seconds\n", n, end - start);
    
    start = get_time();
    vector_multiply(a, b, result, n);
    end = get_time();
    printf("Vector Multiplication (%d elements): %.6f seconds\n", n, end - start);
    
    free(a);
    free(b);
    free(result);
}

// Fibonacci benchmark
void benchmark_fibonacci() {
    const int n = 40;
    
    double start = get_time();
    int fib_rec = fibonacci_recursive(n);
    double end = get_time();
    printf("Fibonacci Recursive (n=%d): %.6f seconds (result: %d)\n", n, end - start, fib_rec);
    
    start = get_time();
    int fib_iter = fibonacci_iterative(n);
    end = get_time();
    printf("Fibonacci Iterative (n=%d): %.6f seconds (result: %d)\n", n, end - start, fib_iter);
}

// Prime counting benchmark
void benchmark_primes() {
    const int N = 1000000;
    
    double start = get_time();
    int count = count_primes(N);
    double end = get_time();
    printf("Prime Counting (up to %d): %.6f seconds (result: %d)\n", N, end - start, count);
}

// Monte Carlo benchmark
void benchmark_monte_carlo() {
    const int samples = 10000000;
    
    double start = get_time();
    double pi_estimate = monte_carlo_pi(samples);
    double end = get_time();
    printf("Monte Carlo Pi (%d samples): %.6f seconds (estimate: %.6f)\n", samples, end - start, pi_estimate);
}

int main() {
    printf("=== C Performance Benchmarks ===\n\n");
    
    printf("CPU Benchmarks:\n");
    printf("---------------\n");
    benchmark_matrices();
    benchmark_sorting();
    benchmark_vectors();
    benchmark_fibonacci();
    benchmark_primes();
    benchmark_monte_carlo();
    
    printf("\n=== Benchmark Complete ===\n");
    return 0;
}
