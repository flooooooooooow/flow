#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif
#include <time.h>
#include <stdint.h>
/* Monotonic clock in nanoseconds. clock_gettime(CLOCK_MONOTONIC) is POSIX
   and works on Linux and on macOS 10.12 and later. */
static uint64_t bench_now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000LL + (uint64_t)ts.tv_nsec;
}
/* Naive recursive Fibonacci. Same algorithm and size as fib.flow. */
#include <stdio.h>
#include <stdint.h>
#include <time.h>

static int64_t fib(int n) {
    if (n < 2) return n;
    return fib(n - 1) + fib(n - 2);
}

int main(void) {
    uint64_t t0 = bench_now_ns();
    int64_t result = fib(35);
    uint64_t t1 = bench_now_ns();
    double secs = (t1 - t0) / 1e9;
    printf("result %lld\n", (long long)result);
    printf("seconds %.9f\n", secs);
    return 0;
}
