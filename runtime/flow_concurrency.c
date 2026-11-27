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
    pthread_t handle;
    int used;
    int started;
    int pending;
    int done;
    flow_thread_fn fn;
    void *arg;
    pthread_cond_t wake;
    pthread_cond_t complete;
} flow_thread_slot;

static flow_thread_slot g_threads[FLOW_MAX_THREADS];
static pthread_mutex_t g_threads_mu = PTHREAD_MUTEX_INITIALIZER;
static pthread_once_t g_threads_once = PTHREAD_ONCE_INIT;

static void flow_thread_slots_init(void) {
    for (int i = 0; i < FLOW_MAX_THREADS; i++) {
        pthread_cond_init(&g_threads[i].wake, NULL);
        pthread_cond_init(&g_threads[i].complete, NULL);
    }
}

static void *flow_thread_worker(void *p) {
    flow_thread_slot *slot = (flow_thread_slot *)p;
    pthread_mutex_lock(&g_threads_mu);
    for (;;) {
        while (!slot->pending) pthread_cond_wait(&slot->wake, &g_threads_mu);
        flow_thread_fn fn = slot->fn;
        void *arg = slot->arg;
        slot->pending = 0;
        pthread_mutex_unlock(&g_threads_mu);
        fn(arg);
        pthread_mutex_lock(&g_threads_mu);
        slot->done = 1;
        pthread_cond_signal(&slot->complete);
    }
    return NULL;
}

int64_t flow_rt_thread_spawn(flow_thread_fn fn, void *arg) {
    if (!fn) return -1;
    pthread_once(&g_threads_once, flow_thread_slots_init);
    pthread_mutex_lock(&g_threads_mu);
    int slot = -1;
    for (int i = 0; i < FLOW_MAX_THREADS; i++) {
        if (!g_threads[i].used) {
            slot = i;
            g_threads[i].used = 1;
            break;
        }
    }
    if (slot < 0) {
        pthread_mutex_unlock(&g_threads_mu);
        return -1;
    }

    flow_thread_slot *worker = &g_threads[slot];
    worker->fn = fn;
    worker->arg = arg;
    worker->done = 0;
    worker->pending = 1;
    if (!worker->started) {
        if (pthread_create(&worker->handle, NULL, flow_thread_worker, worker) != 0) {
            worker->pending = 0;
            worker->fn = NULL;
            worker->arg = NULL;
            worker->used = 0;
            pthread_mutex_unlock(&g_threads_mu);
            return -1;
        }
        worker->started = 1;
    } else {
        pthread_cond_signal(&worker->wake);
    }
    pthread_mutex_unlock(&g_threads_mu);
    return (int64_t)slot;
}

int32_t flow_rt_thread_join(int64_t tid) {
    if (tid < 0 || tid >= FLOW_MAX_THREADS) return -1;
    pthread_once(&g_threads_once, flow_thread_slots_init);
    pthread_mutex_lock(&g_threads_mu);
    flow_thread_slot *worker = &g_threads[tid];
    if (!worker->used) {
        pthread_mutex_unlock(&g_threads_mu);
        return -1;
    }
    while (!worker->done) pthread_cond_wait(&worker->complete, &g_threads_mu);
    worker->used = 0;
    worker->fn = NULL;
    worker->arg = NULL;
    pthread_mutex_unlock(&g_threads_mu);
    return 0;
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
