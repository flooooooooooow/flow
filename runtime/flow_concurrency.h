/* Flow concurrency runtime — threads, parallel-for, async task table.
 * Linked by ./flow run when present. Requires -pthread.
 */
#ifndef FLOW_CONCURRENCY_H
#define FLOW_CONCURRENCY_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*flow_thread_fn)(void *arg);
typedef int32_t (*flow_task_fn)(int32_t arg);

/* OS threads */
int64_t flow_thread_spawn(flow_thread_fn fn, void *arg);
int32_t flow_thread_join(int64_t tid);
void flow_thread_yield(void);

/* Data-parallel helper (used when OpenMP is unavailable from C callers) */
typedef void (*flow_par_body_fn)(int32_t i, void *ctx);
void flow_parallel_for_i32(int32_t start, int32_t end, int32_t step,
                           flow_par_body_fn body, void *ctx);

/* Async task table for ThreadedAsync (effect capability) */
void flow_task_register(int32_t task_id, flow_task_fn fn);
void flow_async_spawn(int32_t task_id, int32_t arg);
int32_t flow_async_join(int32_t task_id);
void flow_async_delay(int32_t ms);

/* Microbenchmarks (OS threads; compare to Go goroutine equivalents) */
/* Ping-pong N messages over a buffered channel between 2 pthreads.
 * Returns wall-clock nanoseconds, or -1 on error. */
int64_t flow_bench_chan_pingpong_ns(int32_t n, int32_t buf);
/* Same workload on cooperative fibers (M:1) — see flow_fiber.h */
int64_t flow_bench_fiber_chan_pingpong_ns(int32_t n, int32_t buf);
/* Parallel sum 0..n-1 over worker threads. Returns checksum. */
int64_t flow_bench_parallel_sum(int32_t n);

/* Atomic wrappers (avoid redeclaring clang __atomic_* builtins) */
int32_t flow_atomic_load_i32(int32_t *ptr, int32_t memorder);
void flow_atomic_store_i32(int32_t *ptr, int32_t val, int32_t memorder);
int32_t flow_atomic_fetch_add_i32(int32_t *ptr, int32_t val, int32_t memorder);
int32_t flow_atomic_fetch_sub_i32(int32_t *ptr, int32_t val, int32_t memorder);
_Bool flow_atomic_cas_i32(int32_t *ptr, int32_t *expected, int32_t desired,
                          _Bool weak, int32_t success, int32_t failure);

int64_t __atomic_load_n_i64(int64_t *ptr, int32_t memorder);
void __atomic_store_n_i64(int64_t *ptr, int64_t val, int32_t memorder);
int64_t __atomic_fetch_add_i64(int64_t *ptr, int64_t val, int32_t memorder);
int64_t __atomic_fetch_sub_i64(int64_t *ptr, int64_t val, int32_t memorder);
_Bool __atomic_compare_exchange_n_i64(int64_t *ptr, int64_t *expected, int64_t desired,
                                      _Bool weak, int32_t success, int32_t failure);
_Bool __atomic_load_n_bool(_Bool *ptr, int32_t memorder);
void __atomic_store_n_bool(_Bool *ptr, _Bool val, int32_t memorder);
_Bool __atomic_compare_exchange_n_bool(_Bool *ptr, _Bool *expected, _Bool desired,
                                       _Bool weak, int32_t success, int32_t failure);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_CONCURRENCY_H */
