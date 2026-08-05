/* OS netpoller — kqueue (Darwin/BSD) / epoll (Linux). Go netpoller analogue. */
#ifndef FLOW_NETPOLL_H
#define FLOW_NETPOLL_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

void flow_netpoll_init(void);
void flow_netpoll_shutdown(void);

/* Wait until fd is readable/writable or timeout.
 * Returns 1 = ready, 0 = timeout, -1 = error. */
int32_t flow_netpoll_poll_read(int32_t fd, int32_t timeout_ms);
int32_t flow_netpoll_poll_write(int32_t fd, int32_t timeout_ms);

/* Sleep via the poller (no busy wait). */
void flow_netpoll_sleep_ms(int32_t ms);

/* Fiber-aware variants: park the current fiber instead of blocking the OS
 * thread. Off-fiber, identical to flow_netpoll_poll_*. */
int32_t flow_netpoll_fiber_poll_read(int32_t fd, int32_t timeout_ms);
int32_t flow_netpoll_fiber_poll_write(int32_t fd, int32_t timeout_ms);

/* Demo: fiber parks on pipe read; returns 1 if woken by write. */
int32_t flow_demo_fiber_netpoll_pipe(void); /* → lib/runtime/fiber_netpoll.flow */

/* Park current fiber for ms (timer via netpoller). Off-fiber: blocking sleep. */
void flow_netpoll_fiber_sleep_ms(int32_t ms);

/* Microbench: N timed sleeps of 1ms via netpoll; returns wall ns. */
int64_t flow_bench_netpoll_sleep_ns(int32_t n);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_NETPOLL_H */
