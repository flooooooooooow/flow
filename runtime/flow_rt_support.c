/* Thin forever POSIX helpers for Flow-implemented runtime modules.
 * Logic lives in lib/runtime/ Flow sources; this file only wraps syscalls / ABI glue.
 */
#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>

#if defined(__APPLE__) || defined(__linux__)
#include <sched.h>
#endif

/* Fill sec/nsec with CLOCK_MONOTONIC (or REALTIME fallback). Returns 0 on success. */
int32_t flow_rt_monotonic_timespec(int64_t *sec_out, int64_t *nsec_out) {
    struct timespec ts;
#if defined(CLOCK_MONOTONIC)
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        return -1;
    }
#else
    if (clock_gettime(CLOCK_REALTIME, &ts) != 0) {
        return -1;
    }
#endif
    if (sec_out) {
        *sec_out = (int64_t)ts.tv_sec;
    }
    if (nsec_out) {
        *nsec_out = (int64_t)ts.tv_nsec;
    }
    return 0;
}

int64_t flow_rt_monotonic_ns(void) {
    int64_t sec = 0;
    int64_t nsec = 0;
    if (flow_rt_monotonic_timespec(&sec, &nsec) != 0) {
        return 0;
    }
    return sec * 1000000000LL + nsec;
}

/* stderr is a libc global, and its symbol differs per platform (__stderrp on
 * Darwin, stderr on glibc). Flow externs are functions only, so diagnostics
 * written from Flow reach the stream through this. */
void *flow_rt_stderr(void) {
    return (void *)stderr;
}

void flow_rt_usleep(int32_t usec) {
    if (usec > 0) {
        usleep((useconds_t)usec);
    }
}
