#include <stdint.h>
#include <time.h>

// Provides jit_time() for native builds (seconds as f64)
double jit_time() {
    struct timespec ts;
#if defined(CLOCK_MONOTONIC)
    clock_gettime(CLOCK_MONOTONIC, &ts);
#else
    clock_gettime(CLOCK_REALTIME, &ts);
#endif
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}
