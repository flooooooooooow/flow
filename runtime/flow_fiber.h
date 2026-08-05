/* Cooperative stackful fibers — M:N with asm context switch.
 * GOMAXPROCS-style: FLOW_MAXPROCS env or flow_fiber_set_maxprocs().
 */
#ifndef FLOW_FIBER_H
#define FLOW_FIBER_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*flow_fiber_fn)(void *arg);

/* Worker count (like GOMAXPROCS). Call before first spawn, or use env FLOW_MAXPROCS. */
void flow_fiber_set_maxprocs(int32_t n);
int32_t flow_fiber_maxprocs(void);

void flow_fiber_init(void);
void flow_fiber_shutdown(void);

int32_t flow_fiber_spawn(flow_fiber_fn fn, void *arg);
void flow_fiber_yield(void);
void flow_fiber_park(void);
void flow_fiber_unpark(int32_t id);

/* Current fiber id on this OS thread, or -1 if not on a fiber. */
int32_t flow_fiber_current_id(void);

/* Lost-wakeup-safe park for external waiters (netpoll):
 *   lock; if (!done) { prepare_park(); unlock; finish_park(); } else unlock;
 * Unpark may race after prepare: finish_park becomes a no-op if already READY. */
int flow_fiber_prepare_park(void);
void flow_fiber_finish_park(void);

/* Drain ready work on the calling thread (and wake pool workers). */
void flow_fiber_run(void);
void flow_fiber_run_until(int32_t id);

/* Work-stealing counters (local pops vs steals from other workers). */
void flow_fiber_steal_stats(uint64_t *local_pops, uint64_t *steals);
int64_t flow_rt_fiber_local_pops(void);
int64_t flow_rt_fiber_steals(void);
void flow_rt_fiber_steal_stats_reset(void);

void flow_fiber_async_spawn(int32_t task_id, int32_t arg);
int32_t flow_fiber_async_join(int32_t task_id);
void flow_fiber_async_delay(int32_t ms);

/* Run user main on a fiber so Flow frames can park/suspend mid-function. */
typedef int32_t (*flow_main_fn)(void);
int32_t flow_fiber_run_main(flow_main_fn fn);

/* Bench bodies (Flow wrappers in lib/runtime/fiber_benches.flow). */
int64_t flow_rt_bench_fiber_chan_pingpong_body(int32_t n, int32_t buf);
int64_t flow_rt_bench_fiber_fanout_sum_body(int32_t n, int32_t fibers);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_FIBER_H */
