/* Thin forever POSIX / ABI helpers for Flow-implemented runtime modules.
 * Logic lives in lib/runtime/ Flow sources; this file wraps syscalls and
 * things Flow cannot express yet (calling through opaque C function
 * pointers, errno, host error UI).
 *
 * Feature (C fnptr call): Flow cannot cast ptr<void> to a C function type
 * and invoke it. Until the language grows a raw C-fnptr type + call-through,
 * these flow_rt_call_* trampolines are the supported escape hatch. See
 * lib/runtime/c_call.flow and docs/language/c-fnptr-call.md.
 */
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#if defined(__APPLE__) || defined(__linux__)
#include <sched.h>
#endif

#ifdef __APPLE__
#include <CoreFoundation/CFUserNotification.h>
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

int32_t flow_rt_unlink(const char *path) {
    return path ? (int32_t)unlink(path) : -1;
}

int32_t flow_rt_rename(const char *old_path, const char *new_path) {
    if (!old_path || !new_path)
        return -1;
    return (int32_t)rename(old_path, new_path);
}

int32_t flow_rt_mkdir(const char *path, int32_t mode) {
    if (!path)
        return -1;
#ifdef _WIN32
    (void)mode;
    return (int32_t)mkdir(path);
#else
    return (int32_t)mkdir(path, (mode_t)mode);
#endif
}

/* Milliseconds since epoch (gettimeofday).
 * When FLOW_TEST_CLOCK is defined, this function is omitted so the
 * Emscripten --js-library override (deterministic_clock.js) takes effect. */
#ifndef FLOW_TEST_CLOCK
uint32_t flow_rt_time_ms(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (uint32_t)(tv.tv_sec * 1000 + tv.tv_usec / 1000);
}
#endif


/* ---- C function-pointer call trampolines ---------------------------- */

void flow_rt_call_void(void *fn) {
    if (fn != NULL)
        ((void (*)(void))fn)();
}

void flow_rt_call_p1(void *fn, void *arg) {
    if (fn != NULL)
        ((void (*)(void *))fn)(arg);
}

void flow_rt_call_p2(void *fn, void *a, void *b) {
    if (fn != NULL)
        ((void (*)(void *, void *))fn)(a, b);
}

/* Doom-style boolean (unsigned int) predicates → 0/1. */
int32_t flow_rt_call_p1_bool(void *fn, void *arg) {
    if (fn == NULL)
        return 0;
    return ((unsigned int (*)(void *))fn)(arg) ? 1 : 0;
}

int32_t flow_rt_call_p3_bool(void *fn, void *a, int32_t x, int32_t y) {
    if (fn == NULL)
        return 0;
    return ((unsigned int (*)(void *, int, int))fn)(a, (int)x, (int)y) ? 1 : 0;
}

/* ---- errno / filesystem helpers ------------------------------------- */

int32_t flow_rt_errno(void) {
    return (int32_t)errno;
}

int32_t flow_rt_errno_is_isdir(void) {
    return errno == EISDIR ? 1 : 0;
}

/* ---- host fatal-error UI (optional) --------------------------------- */

void flow_rt_error_popup(const char *msg) {
#ifdef __APPLE__
    char buf[512];
    size_t n;
    size_t i;
    CFStringRef message;

    if (msg == NULL)
        return;
    n = strlen(msg);
    if (n >= sizeof(buf))
        n = sizeof(buf) - 1;
    memcpy(buf, msg, n);
    buf[n] = '\0';
    for (i = 0; buf[i] != '\0'; i++) {
        if (buf[i] == '\n')
            buf[i] = ' ';
    }
    message = CFStringCreateWithCString(NULL, buf, kCFStringEncodingUTF8);
    CFUserNotificationDisplayNotice(
        0, kCFUserNotificationCautionAlertLevel,
        NULL, NULL, NULL,
        CFSTR("Flow"), message, NULL);
#else
    (void)msg;
#endif
}
