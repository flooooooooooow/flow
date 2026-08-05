/* Fiber-aware netpoll: park current fiber while waiting on fd readiness. */
#include "flow_netpoll.h"
#include "flow_fiber.h"

#include <pthread.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#if defined(__APPLE__) || defined(__FreeBSD__) || defined(__OpenBSD__) || defined(__NetBSD__)
#define FLOW_USE_KQUEUE 1
#include <sys/event.h>
#include <sys/time.h>
#elif defined(__linux__)
#define FLOW_USE_EPOLL 1
#include <sys/epoll.h>
#include <sys/timerfd.h>
#include <fcntl.h>
#endif

#ifndef FLOW_NP_WAITS
#define FLOW_NP_WAITS 256
#endif

typedef struct {
    int32_t fiber_id;
    int32_t fd;
    int is_read;
    int done;
    int result; /* 1 ready, 0 timeout, -1 error */
    int in_use;
} np_wait;

static np_wait g_waits[FLOW_NP_WAITS];
static pthread_mutex_t g_waits_mu = PTHREAD_MUTEX_INITIALIZER;
static pthread_t g_np_thread;
static int g_np_thread_live = 0;
static int g_np_stop = 0;
static int g_np_fd = -1; /* kqueue or epoll fd */
static int g_waits_inited = 0;

static void waits_init_once(void) {
    if (g_waits_inited) return;
    for (int i = 0; i < FLOW_NP_WAITS; i++) {
        g_waits[i].fiber_id = -1;
        g_waits[i].in_use = 0;
        g_waits[i].done = 1;
    }
    g_waits_inited = 1;
}

#if defined(FLOW_USE_KQUEUE)

static void *netpoll_fiber_thread(void *arg) {
    (void)arg;
    while (!g_np_stop) {
        struct kevent ev;
        struct timespec ts = {0, 50 * 1000 * 1000};
        int n = kevent(g_np_fd, NULL, 0, &ev, 1, &ts);
        if (n <= 0) continue;

        int slot = (int)(intptr_t)ev.udata;
        if (slot < 0 || slot >= FLOW_NP_WAITS) continue;

        pthread_mutex_lock(&g_waits_mu);
        if (g_waits[slot].in_use && !g_waits[slot].done) {
            int32_t fid = g_waits[slot].fiber_id;
            if (ev.filter == EVFILT_TIMER) {
                g_waits[slot].result = 0;
            } else if (ev.flags & EV_ERROR) {
                g_waits[slot].result = -1;
            } else {
                g_waits[slot].result = 1;
            }
            g_waits[slot].done = 1;
            pthread_mutex_unlock(&g_waits_mu);
            if (fid >= 0) flow_fiber_unpark(fid);
        } else {
            pthread_mutex_unlock(&g_waits_mu);
        }
    }
    return NULL;
}

static void ensure_np_thread(void) {
    waits_init_once();
    if (g_np_thread_live) return;
    g_np_fd = kqueue();
    if (g_np_fd < 0) return;
    g_np_stop = 0;
    if (pthread_create(&g_np_thread, NULL, netpoll_fiber_thread, NULL) == 0) {
        g_np_thread_live = 1;
        pthread_detach(g_np_thread);
    }
}

static int32_t fiber_poll_filt(int32_t fd, int32_t timeout_ms, int16_t filt) {
    int32_t self = flow_fiber_current_id();
    if (self < 0) {
        return (filt == EVFILT_READ)
            ? flow_netpoll_poll_read(fd, timeout_ms)
            : flow_netpoll_poll_write(fd, timeout_ms);
    }
    ensure_np_thread();
    if (g_np_fd < 0) {
        return (filt == EVFILT_READ)
            ? flow_netpoll_poll_read(fd, timeout_ms)
            : flow_netpoll_poll_write(fd, timeout_ms);
    }

    pthread_mutex_lock(&g_waits_mu);
    int slot = -1;
    for (int i = 0; i < FLOW_NP_WAITS; i++) {
        if (!g_waits[i].in_use) {
            slot = i;
            break;
        }
    }
    if (slot < 0) {
        pthread_mutex_unlock(&g_waits_mu);
        return (filt == EVFILT_READ)
            ? flow_netpoll_poll_read(fd, timeout_ms)
            : flow_netpoll_poll_write(fd, timeout_ms);
    }
    g_waits[slot].in_use = 1;
    g_waits[slot].fiber_id = self;
    g_waits[slot].fd = fd;
    g_waits[slot].is_read = (filt == EVFILT_READ);
    g_waits[slot].done = 0;
    g_waits[slot].result = 0;
    pthread_mutex_unlock(&g_waits_mu);

    struct kevent ch[2];
    int nch = 0;
    EV_SET(&ch[nch++], (uintptr_t)fd, filt, EV_ADD | EV_ONESHOT, 0, 0,
           (void *)(intptr_t)slot);
    if (timeout_ms >= 0) {
        /* Unique timer ident per slot (avoid colliding with fds). */
        EV_SET(&ch[nch++], (uintptr_t)(0x40000000u + (unsigned)slot), EVFILT_TIMER,
               EV_ADD | EV_ONESHOT, 0, (intptr_t)timeout_ms, (void *)(intptr_t)slot);
    }
    if (kevent(g_np_fd, ch, nch, NULL, 0, NULL) < 0) {
        pthread_mutex_lock(&g_waits_mu);
        g_waits[slot].in_use = 0;
        g_waits[slot].fiber_id = -1;
        pthread_mutex_unlock(&g_waits_mu);
        return -1;
    }

    /* Lost-wakeup safe park: mark PARKED under waits_mu, then finish swap. */
    pthread_mutex_lock(&g_waits_mu);
    if (!g_waits[slot].done) {
        if (flow_fiber_prepare_park()) {
            pthread_mutex_unlock(&g_waits_mu);
            flow_fiber_finish_park();
            pthread_mutex_lock(&g_waits_mu);
        }
    }
    int32_t result = g_waits[slot].done ? g_waits[slot].result : 0;
    g_waits[slot].in_use = 0;
    g_waits[slot].fiber_id = -1;
    g_waits[slot].done = 1;
    pthread_mutex_unlock(&g_waits_mu);
    return result;
}

int32_t flow_netpoll_fiber_poll_read(int32_t fd, int32_t timeout_ms) {
    return fiber_poll_filt(fd, timeout_ms, EVFILT_READ);
}

int32_t flow_netpoll_fiber_poll_write(int32_t fd, int32_t timeout_ms) {
    return fiber_poll_filt(fd, timeout_ms, EVFILT_WRITE);
}

#elif defined(FLOW_USE_EPOLL)

static void *netpoll_fiber_thread(void *arg) {
    (void)arg;
    while (!g_np_stop) {
        struct epoll_event ev;
        int n = epoll_wait(g_np_fd, &ev, 1, 50);
        if (n <= 0) continue;
        int slot = (int)(intptr_t)ev.data.ptr;
        if (slot < 0 || slot >= FLOW_NP_WAITS) continue;
        pthread_mutex_lock(&g_waits_mu);
        if (g_waits[slot].in_use && !g_waits[slot].done) {
            int32_t fid = g_waits[slot].fiber_id;
            if (ev.events & (EPOLLERR | EPOLLHUP)) g_waits[slot].result = -1;
            else g_waits[slot].result = 1;
            g_waits[slot].done = 1;
            pthread_mutex_unlock(&g_waits_mu);
            if (fid >= 0) flow_fiber_unpark(fid);
        } else {
            pthread_mutex_unlock(&g_waits_mu);
        }
    }
    return NULL;
}

static void ensure_np_thread(void) {
    waits_init_once();
    if (g_np_thread_live) return;
    g_np_fd = epoll_create1(0);
    if (g_np_fd < 0) return;
    g_np_stop = 0;
    if (pthread_create(&g_np_thread, NULL, netpoll_fiber_thread, NULL) == 0) {
        g_np_thread_live = 1;
        pthread_detach(g_np_thread);
    }
}

static int32_t fiber_poll_epoll(int32_t fd, int32_t timeout_ms, int want_write) {
    int32_t self = flow_fiber_current_id();
    if (self < 0) {
        return want_write ? flow_netpoll_poll_write(fd, timeout_ms)
                          : flow_netpoll_poll_read(fd, timeout_ms);
    }
    ensure_np_thread();
    if (g_np_fd < 0) {
        return want_write ? flow_netpoll_poll_write(fd, timeout_ms)
                          : flow_netpoll_poll_read(fd, timeout_ms);
    }

    pthread_mutex_lock(&g_waits_mu);
    int slot = -1;
    for (int i = 0; i < FLOW_NP_WAITS; i++) {
        if (!g_waits[i].in_use) {
            slot = i;
            break;
        }
    }
    if (slot < 0) {
        pthread_mutex_unlock(&g_waits_mu);
        return want_write ? flow_netpoll_poll_write(fd, timeout_ms)
                          : flow_netpoll_poll_read(fd, timeout_ms);
    }
    g_waits[slot].in_use = 1;
    g_waits[slot].fiber_id = self;
    g_waits[slot].fd = fd;
    g_waits[slot].done = 0;
    g_waits[slot].result = 0;
    pthread_mutex_unlock(&g_waits_mu);

    struct epoll_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.events = want_write ? EPOLLOUT : EPOLLIN;
    ev.events |= EPOLLONESHOT | EPOLLET;
    ev.data.ptr = (void *)(intptr_t)slot;
    if (epoll_ctl(g_np_fd, EPOLL_CTL_ADD, fd, &ev) < 0) {
        /* Already registered — try MOD */
        if (epoll_ctl(g_np_fd, EPOLL_CTL_MOD, fd, &ev) < 0) {
            pthread_mutex_lock(&g_waits_mu);
            g_waits[slot].in_use = 0;
            g_waits[slot].fiber_id = -1;
            pthread_mutex_unlock(&g_waits_mu);
            return -1;
        }
    }

    /* Coarse timeout: yield-park loop with deadline (epoll timerfd optional later). */
    int waited = 0;
    for (;;) {
        pthread_mutex_lock(&g_waits_mu);
        if (g_waits[slot].done) {
            int32_t result = g_waits[slot].result;
            g_waits[slot].in_use = 0;
            g_waits[slot].fiber_id = -1;
            pthread_mutex_unlock(&g_waits_mu);
            return result;
        }
        if (timeout_ms >= 0 && waited >= timeout_ms) {
            g_waits[slot].done = 1;
            g_waits[slot].result = 0;
            g_waits[slot].in_use = 0;
            g_waits[slot].fiber_id = -1;
            pthread_mutex_unlock(&g_waits_mu);
            epoll_ctl(g_np_fd, EPOLL_CTL_DEL, fd, NULL);
            return 0;
        }
        if (flow_fiber_prepare_park()) {
            pthread_mutex_unlock(&g_waits_mu);
            flow_fiber_finish_park();
        } else {
            pthread_mutex_unlock(&g_waits_mu);
        }
        waited += 1;
        if (!g_waits[slot].done && timeout_ms >= 0) {
            /* brief wall sleep only when still waiting — unparks continue promptly */
            usleep(1000);
        }
    }
}

int32_t flow_netpoll_fiber_poll_read(int32_t fd, int32_t timeout_ms) {
    return fiber_poll_epoll(fd, timeout_ms, 0);
}

int32_t flow_netpoll_fiber_poll_write(int32_t fd, int32_t timeout_ms) {
    return fiber_poll_epoll(fd, timeout_ms, 1);
}

#else

int32_t flow_netpoll_fiber_poll_read(int32_t fd, int32_t timeout_ms) {
    return flow_netpoll_poll_read(fd, timeout_ms);
}

int32_t flow_netpoll_fiber_poll_write(int32_t fd, int32_t timeout_ms) {
    return flow_netpoll_poll_write(fd, timeout_ms);
}

#endif

void flow_netpoll_fiber_sleep_ms(int32_t ms) {
    if (ms <= 0) return;
    int32_t self = flow_fiber_current_id();
    if (self < 0) {
        flow_netpoll_sleep_ms(ms);
        return;
    }
#if defined(FLOW_USE_KQUEUE)
    ensure_np_thread();
    if (g_np_fd < 0) {
        flow_netpoll_sleep_ms(ms);
        return;
    }
    pthread_mutex_lock(&g_waits_mu);
    int slot = -1;
    for (int i = 0; i < FLOW_NP_WAITS; i++) {
        if (!g_waits[i].in_use) {
            slot = i;
            break;
        }
    }
    if (slot < 0) {
        pthread_mutex_unlock(&g_waits_mu);
        flow_netpoll_sleep_ms(ms);
        return;
    }
    g_waits[slot].in_use = 1;
    g_waits[slot].fiber_id = self;
    g_waits[slot].fd = -1;
    g_waits[slot].done = 0;
    g_waits[slot].result = 0;
    pthread_mutex_unlock(&g_waits_mu);

    struct kevent ch;
    EV_SET(&ch, (uintptr_t)(0x50000000u + (unsigned)slot), EVFILT_TIMER,
           EV_ADD | EV_ONESHOT, 0, (intptr_t)ms, (void *)(intptr_t)slot);
    if (kevent(g_np_fd, &ch, 1, NULL, 0, NULL) < 0) {
        pthread_mutex_lock(&g_waits_mu);
        g_waits[slot].in_use = 0;
        g_waits[slot].fiber_id = -1;
        pthread_mutex_unlock(&g_waits_mu);
        flow_netpoll_sleep_ms(ms);
        return;
    }
    pthread_mutex_lock(&g_waits_mu);
    if (!g_waits[slot].done) {
        if (flow_fiber_prepare_park()) {
            pthread_mutex_unlock(&g_waits_mu);
            flow_fiber_finish_park();
            pthread_mutex_lock(&g_waits_mu);
        }
    }
    g_waits[slot].in_use = 0;
    g_waits[slot].fiber_id = -1;
    pthread_mutex_unlock(&g_waits_mu);
#else
    /* Non-kqueue: yield then blocking sleep (still correct; less M:N friendly). */
    flow_fiber_yield();
    flow_netpoll_sleep_ms(ms);
#endif
}

/* Demo helper: fiber parks on pipe read; writer unblocks; returns 1 on success. */
typedef struct {
    int rfd;
    int32_t result;
} fiber_pipe_arg;

static void fiber_pipe_poller(void *arg) {
    fiber_pipe_arg *a = (fiber_pipe_arg *)arg;
    a->result = flow_netpoll_fiber_poll_read(a->rfd, 1000);
}

int32_t flow_rt_demo_fiber_netpoll_pipe(void) {
    int fds[2];
    if (pipe(fds) != 0) return -1;
    flow_fiber_set_maxprocs(1);
    flow_fiber_init();
    fiber_pipe_arg a = {.rfd = fds[0], .result = 0};
    int32_t id = flow_fiber_spawn(fiber_pipe_poller, &a);
    if (id < 0) {
        close(fds[0]);
        close(fds[1]);
        return -1;
    }
    char ch = 'A';
    (void)write(fds[1], &ch, 1);
    flow_fiber_run_until(id);
    close(fds[0]);
    close(fds[1]);
    return a.result == 1 ? 1 : 0;
}

/* flow_demo_fiber_netpoll_pipe → lib/runtime/fiber_netpoll.flow */
