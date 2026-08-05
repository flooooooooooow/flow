/* Flow concurrency runtime */
#include "flow_concurrency.h"

#include <pthread.h>
#include <sched.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifndef FLOW_MAX_THREADS
#define FLOW_MAX_THREADS 256
#endif

#ifndef FLOW_MAX_TASKS
#define FLOW_MAX_TASKS 256
#endif

#ifndef FLOW_PAR_WORKERS
#define FLOW_PAR_WORKERS 8
#endif

/* ---- threads ----------------------------------------------------------- */

typedef struct {
    flow_thread_fn fn;
    void *arg;
} flow_thread_pack;

typedef struct {
    pthread_t handle;
    int used;
} flow_thread_slot;

static flow_thread_slot g_threads[FLOW_MAX_THREADS];
static pthread_mutex_t g_threads_mu = PTHREAD_MUTEX_INITIALIZER;

static void *flow_thread_trampoline(void *p) {
    flow_thread_pack pack = *(flow_thread_pack *)p;
    free(p);
    pack.fn(pack.arg);
    return NULL;
}

int64_t flow_rt_thread_spawn(flow_thread_fn fn, void *arg) {
    if (!fn) return -1;
    flow_thread_pack *pack = (flow_thread_pack *)malloc(sizeof(*pack));
    if (!pack) return -1;
    pack->fn = fn;
    pack->arg = arg;

    pthread_mutex_lock(&g_threads_mu);
    int slot = -1;
    for (int i = 0; i < FLOW_MAX_THREADS; i++) {
        if (!g_threads[i].used) {
            slot = i;
            g_threads[i].used = 1;
            break;
        }
    }
    pthread_mutex_unlock(&g_threads_mu);
    if (slot < 0) {
        free(pack);
        return -1;
    }

    if (pthread_create(&g_threads[slot].handle, NULL, flow_thread_trampoline, pack) != 0) {
        pthread_mutex_lock(&g_threads_mu);
        g_threads[slot].used = 0;
        pthread_mutex_unlock(&g_threads_mu);
        free(pack);
        return -1;
    }
    return (int64_t)slot;
}

int32_t flow_rt_thread_join(int64_t tid) {
    if (tid < 0 || tid >= FLOW_MAX_THREADS) return -1;
    pthread_mutex_lock(&g_threads_mu);
    if (!g_threads[tid].used) {
        pthread_mutex_unlock(&g_threads_mu);
        return -1;
    }
    pthread_t h = g_threads[tid].handle;
    pthread_mutex_unlock(&g_threads_mu);

    int rc = pthread_join(h, NULL);
    pthread_mutex_lock(&g_threads_mu);
    g_threads[tid].used = 0;
    pthread_mutex_unlock(&g_threads_mu);
    return rc == 0 ? 0 : -1;
}

void flow_rt_thread_yield(void) {
#if defined(_POSIX_PRIORITY_SCHEDULING) || defined(__APPLE__) || defined(__linux__)
    sched_yield();
#else
    usleep(0);
#endif
}

/* Parallel-for → lib/runtime/concurrency_parallel.flow (+ flow_rt_parallel.c).
 * Async → lib/runtime/concurrency_async.flow.
 * Microbenchmarks → lib/runtime/concurrency_benches.flow (+ flow_rt_cchan.c).
 */

/* ---- atomics wrappers -------------------------------------------------- */

int32_t flow_atomic_load_i32(int32_t *ptr, int32_t memorder) {
    (void)memorder;
    return __atomic_load_n(ptr, __ATOMIC_SEQ_CST);
}

void flow_atomic_store_i32(int32_t *ptr, int32_t val, int32_t memorder) {
    (void)memorder;
    __atomic_store_n(ptr, val, __ATOMIC_SEQ_CST);
}

int32_t flow_atomic_fetch_add_i32(int32_t *ptr, int32_t val, int32_t memorder) {
    (void)memorder;
    return __atomic_fetch_add(ptr, val, __ATOMIC_SEQ_CST);
}

int32_t flow_atomic_fetch_sub_i32(int32_t *ptr, int32_t val, int32_t memorder) {
    (void)memorder;
    return __atomic_fetch_sub(ptr, val, __ATOMIC_SEQ_CST);
}

_Bool flow_atomic_cas_i32(int32_t *ptr, int32_t *expected, int32_t desired,
                          _Bool weak, int32_t success, int32_t failure) {
    (void)success;
    (void)failure;
    return __atomic_compare_exchange_n(ptr, expected, desired, weak,
                                       __ATOMIC_SEQ_CST, __ATOMIC_SEQ_CST);
}

int64_t __atomic_load_n_i64(int64_t *ptr, int32_t memorder) {
    (void)memorder;
    return __atomic_load_n(ptr, __ATOMIC_SEQ_CST);
}

void __atomic_store_n_i64(int64_t *ptr, int64_t val, int32_t memorder) {
    (void)memorder;
    __atomic_store_n(ptr, val, __ATOMIC_SEQ_CST);
}

int64_t __atomic_fetch_add_i64(int64_t *ptr, int64_t val, int32_t memorder) {
    (void)memorder;
    return __atomic_fetch_add(ptr, val, __ATOMIC_SEQ_CST);
}

int64_t __atomic_fetch_sub_i64(int64_t *ptr, int64_t val, int32_t memorder) {
    (void)memorder;
    return __atomic_fetch_sub(ptr, val, __ATOMIC_SEQ_CST);
}

_Bool __atomic_compare_exchange_n_i64(int64_t *ptr, int64_t *expected, int64_t desired,
                                      _Bool weak, int32_t success, int32_t failure) {
    (void)success;
    (void)failure;
    return __atomic_compare_exchange_n(ptr, expected, desired, weak,
                                       __ATOMIC_SEQ_CST, __ATOMIC_SEQ_CST);
}

_Bool __atomic_load_n_bool(_Bool *ptr, int32_t memorder) {
    (void)memorder;
    return __atomic_load_n(ptr, __ATOMIC_SEQ_CST);
}

void __atomic_store_n_bool(_Bool *ptr, _Bool val, int32_t memorder) {
    (void)memorder;
    __atomic_store_n(ptr, val, __ATOMIC_SEQ_CST);
}

_Bool __atomic_compare_exchange_n_bool(_Bool *ptr, _Bool *expected, _Bool desired,
                                       _Bool weak, int32_t success, int32_t failure) {
    (void)success;
    (void)failure;
    return __atomic_compare_exchange_n(ptr, expected, desired, weak,
                                       __ATOMIC_SEQ_CST, __ATOMIC_SEQ_CST);
}
