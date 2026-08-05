/* Naive recursive Fibonacci. Same algorithm and size as fib.flow. */
#include <stdio.h>
#include <stdint.h>
#include <time.h>

static int64_t fib(int n) {
    if (n < 2) return n;
    return fib(n - 1) + fib(n - 2);
}

int main(void) {
    uint64_t t0 = clock_gettime_nsec_np(CLOCK_MONOTONIC);
    int64_t result = fib(35);
    uint64_t t1 = clock_gettime_nsec_np(CLOCK_MONOTONIC);
    double secs = (t1 - t0) / 1e9;
    printf("result %lld\n", (long long)result);
    printf("seconds %.9f\n", secs);
    return 0;
}
