/* kqueue / epoll netpoller */
#include "flow_netpoll.h"

#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#if defined(__APPLE__) || defined(__FreeBSD__) || defined(__OpenBSD__) || defined(__NetBSD__)
#define FLOW_NETPOLL_KQUEUE 1
#include <sys/event.h>
#include <sys/time.h>
#elif defined(__linux__)
#define FLOW_NETPOLL_EPOLL 1
#include <sys/epoll.h>
#include <sys/timerfd.h>
#else
#define FLOW_NETPOLL_FALLBACK 1
#endif

static int g_np_fd = -1;
static int g_np_inited = 0;

void flow_netpoll_init(void) {
    if (g_np_inited) return;
#if defined(FLOW_NETPOLL_KQUEUE)
    g_np_fd = kqueue();
#elif defined(FLOW_NETPOLL_EPOLL)
    g_np_fd = epoll_create1(0);
#else
    g_np_fd = -1;
#endif
    g_np_inited = 1;
}

void flow_netpoll_shutdown(void) {
    if (!g_np_inited) return;
    if (g_np_fd >= 0) close(g_np_fd);
    g_np_fd = -1;
    g_np_inited = 0;
}

#if defined(FLOW_NETPOLL_KQUEUE)

static int32_t kqueue_wait_filt(int32_t fd, int16_t filt, int32_t timeout_ms) {
    flow_netpoll_init();
    if (g_np_fd < 0) return -1;
    struct kevent ch, ev;
    EV_SET(&ch, (uintptr_t)fd, filt, EV_ADD | EV_ONESHOT, 0, 0, NULL);
    struct timespec ts;
    struct timespec *tsp = NULL;
    if (timeout_ms >= 0) {
        ts.tv_sec = timeout_ms / 1000;
        ts.tv_nsec = (long)(timeout_ms % 1000) * 1000000L;
        tsp = &ts;
    }
    int n = kevent(g_np_fd, &ch, 1, &ev, 1, tsp);
    if (n < 0) return -1;
    if (n == 0) return 0;
    /* EV_ERROR with data==0 often means the filter is unsupported for this
     * fd (e.g. some ttys); treat as not-ready rather than hard failure. */
    if (ev.flags & EV_ERROR) {
        return (ev.data == 0) ? 0 : -1;
    }
    return 1;
}

int32_t flow_netpoll_poll_read(int32_t fd, int32_t timeout_ms) {
    return kqueue_wait_filt(fd, EVFILT_READ, timeout_ms);
}

int32_t flow_netpoll_poll_write(int32_t fd, int32_t timeout_ms) {
    return kqueue_wait_filt(fd, EVFILT_WRITE, timeout_ms);
}

void flow_netpoll_sleep_ms(int32_t ms) {
    if (ms <= 0) return;
    flow_netpoll_init();
    if (g_np_fd < 0) {
        usleep((useconds_t)ms * 1000u);
        return;
    }
    struct kevent ch, ev;
    EV_SET(&ch, 0, EVFILT_TIMER, EV_ADD | EV_ONESHOT, 0, ms, NULL);
    struct timespec ts;
    ts.tv_sec = (ms / 1000) + 1;
    ts.tv_nsec = 0;
    (void)kevent(g_np_fd, &ch, 1, &ev, 1, &ts);
}

#elif defined(FLOW_NETPOLL_EPOLL)

int32_t flow_netpoll_poll_read(int32_t fd, int32_t timeout_ms) {
    flow_netpoll_init();
    if (g_np_fd < 0) return -1;
    struct epoll_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.events = EPOLLIN | EPOLLONESHOT;
    ev.data.fd = fd;
    if (epoll_ctl(g_np_fd, EPOLL_CTL_ADD, fd, &ev) != 0 && errno != EEXIST) {
        if (epoll_ctl(g_np_fd, EPOLL_CTL_MOD, fd, &ev) != 0) return -1;
    }
    struct epoll_event out;
    int n = epoll_wait(g_np_fd, &out, 1, timeout_ms);
    if (n < 0) return -1;
    if (n == 0) return 0;
    return 1;
}

int32_t flow_netpoll_poll_write(int32_t fd, int32_t timeout_ms) {
    flow_netpoll_init();
    if (g_np_fd < 0) return -1;
    struct epoll_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.events = EPOLLOUT | EPOLLONESHOT;
    ev.data.fd = fd;
    if (epoll_ctl(g_np_fd, EPOLL_CTL_ADD, fd, &ev) != 0 && errno != EEXIST) {
        if (epoll_ctl(g_np_fd, EPOLL_CTL_MOD, fd, &ev) != 0) return -1;
    }
    struct epoll_event out;
    int n = epoll_wait(g_np_fd, &out, 1, timeout_ms);
    if (n < 0) return -1;
    if (n == 0) return 0;
    return 1;
}

void flow_netpoll_sleep_ms(int32_t ms) {
    if (ms <= 0) return;
    usleep((useconds_t)ms * 1000u);
}

#else

int32_t flow_netpoll_poll_read(int32_t fd, int32_t timeout_ms) {
    (void)fd;
    if (timeout_ms > 0) usleep((useconds_t)timeout_ms * 1000u);
    return 1;
}

int32_t flow_netpoll_poll_write(int32_t fd, int32_t timeout_ms) {
    (void)fd;
    if (timeout_ms > 0) usleep((useconds_t)timeout_ms * 1000u);
    return 1;
}

void flow_netpoll_sleep_ms(int32_t ms) {
    if (ms > 0) usleep((useconds_t)ms * 1000u);
}

#endif

/* flow_bench_netpoll_sleep_ns → lib/runtime/netpoll_bench.flow */
