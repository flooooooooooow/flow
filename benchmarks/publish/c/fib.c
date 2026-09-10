#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif
#include <time.h>
#include <stdint.h>
#ifndef __APPLE__
static uint64_t clock_gettime_nsec_np(int clock_id) {
    struct timespec ts;
    clock_gettime(clock_id, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}
#endif
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
