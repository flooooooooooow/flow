/* Pthread trampoline + C-only task state for Flow ThreadedAsync.
 * Logic and slot bookkeeping (arg/result/done/spawned) live in
 * lib/runtime/concurrency_async.flow as module statics.
 *
 * What stays here, and why:
 *   - g_fn:      C function pointers. Flow module statics cannot hold
 *                arrays of pointers, and calling through one needs a C cast.
 *   - g_thread:  pthread_t is an opaque C type.
 *   - g_tasks_mu: the mutex itself needs pthreads. Flow code brackets every
 *                slot access with flow_rt_task_lock()/flow_rt_task_unlock();
 *                that mutex is what makes the (non-atomic) Flow statics safe
 *                to touch from both the spawning and the worker thread.
 */
#include <pthread.h>
#include <stdint.h>
#include <stdlib.h>

#ifndef FLOW_MAX_TASKS
#define FLOW_MAX_TASKS 256
#endif

typedef int32_t (*flow_task_fn)(int32_t arg);

static flow_task_fn g_fn[FLOW_MAX_TASKS];
static pthread_t g_thread[FLOW_MAX_TASKS];
static pthread_mutex_t g_tasks_mu = PTHREAD_MUTEX_INITIALIZER;

/* Implemented in lib/runtime/concurrency_async.flow */
void flow_async_worker(int32_t task_id);

void flow_rt_task_lock(void) { pthread_mutex_lock(&g_tasks_mu); }
void flow_rt_task_unlock(void) { pthread_mutex_unlock(&g_tasks_mu); }

void flow_rt_task_set_fn(int32_t id, void *fn) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return;
    g_fn[id] = (flow_task_fn)fn;
}

void *flow_rt_task_get_fn(int32_t id) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return NULL;
    return (void *)g_fn[id];
}

int32_t flow_rt_call_task_fn(void *fn, int32_t arg) {
    if (!fn) return 0;
    return ((flow_task_fn)fn)(arg);
}

static void *flow_rt_task_trampoline(void *p) {
    int32_t id = (int32_t)(intptr_t)p;
    flow_async_worker(id);
    return NULL;
}

/* Returns 0 on success, -1 if pthread_create failed (caller should run sync). */
int32_t flow_rt_task_pthread_create(int32_t id) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return -1;
    if (pthread_create(&g_thread[id], NULL, flow_rt_task_trampoline,
                       (void *)(intptr_t)id) != 0) {
        return -1;
    }
    return 0;
}

int32_t flow_rt_task_pthread_join(int32_t id) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return -1;
    return pthread_join(g_thread[id], NULL) == 0 ? 0 : -1;
}
