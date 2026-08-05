/* Fibonacci Benchmark - Tests recursive function call overhead */
#include <stdio.h>
#include <time.h>
#include <stdint.h>

int64_t fib(int32_t n) {
    if (n < 2) return n;
    return fib(n - 1) + fib(n - 2);
}

double benchmark(int32_t n, int32_t iterations) {
    clock_t start = clock();
    
    int64_t result = 0;
    for (int i = 0; i < iterations; i++) {
        result = fib(n);
    }
    
    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("  fib(%d) = %lld | %.4f sec | %.2f calls/sec\n", 
           n, result, elapsed, iterations / elapsed);
    
    return elapsed;
}

int main() {
    printf("==============================================\n");
    printf("  FIBONACCI BENCHMARK (Naive Recursive) - C\n");
    printf("==============================================\n\n");
    
    /* Warm up */
    int64_t warmup = fib(20);
    (void)warmup;
    
    printf("N=35 (1 iteration):\n");
    benchmark(35, 1);
    
    printf("\nN=40 (1 iteration):\n");
    benchmark(40, 1);
    
    printf("\nN=30 (10 iterations):\n");
    benchmark(30, 10);
    
    printf("\nBenchmark complete.\n");
    return 0;
}
