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
/* Mandelbrot set membership count on a 400x400 grid, 100 max iterations.
 * Same algorithm and size as mandelbrot.flow. */
#include <stdio.h>
#include <stdint.h>
#include <time.h>

#define W 400
#define H 400
#define MAXI 100

static int mandel_count(void) {
    int count = 0;
    for (int py = 0; py < H; py++) {
        double cy = 2.5 * py / H - 1.25;
        for (int px = 0; px < W; px++) {
            double cx = 2.5 * px / W - 2.0;
            double zx = 0.0, zy = 0.0;
            int iter = 0;
            while (zx * zx + zy * zy <= 4.0 && iter < MAXI) {
                double tmp = zx * zx - zy * zy + cx;
                zy = 2.0 * zx * zy + cy;
                zx = tmp;
                iter = iter + 1;
            }
            if (iter == MAXI) {
                count = count + 1;
            }
        }
    }
    return count;
}

int main(void) {
    uint64_t t0 = bench_now_ns();
    int count = mandel_count();
    uint64_t t1 = bench_now_ns();
    double secs = (t1 - t0) / 1e9;
    printf("result %d\n", count);
    printf("seconds %.9f\n", secs);
    return 0;
}
