/* Task-table storage + pthread trampoline for Flow ThreadedAsync.
 * Logic (register/spawn/join/delay) lives in lib/runtime/concurrency_async.flow.
 */
#include <pthread.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

#ifndef FLOW_MAX_TASKS
#define FLOW_MAX_TASKS 256
#endif

typedef int32_t (*flow_task_fn)(int32_t arg);

typedef struct {
    flow_task_fn fn;
    int32_t arg;
    int32_t result;
    int32_t done;
    int32_t spawned;
    pthread_t thread;
} flow_rt_task_slot;

static flow_rt_task_slot g_tasks[FLOW_MAX_TASKS];
static pthread_mutex_t g_tasks_mu = PTHREAD_MUTEX_INITIALIZER;

/* Implemented in lib/runtime/concurrency_async.flow */
void flow_async_worker(int32_t task_id);

void flow_rt_task_lock(void) { pthread_mutex_lock(&g_tasks_mu); }
void flow_rt_task_unlock(void) { pthread_mutex_unlock(&g_tasks_mu); }

int32_t flow_rt_task_max(void) { return FLOW_MAX_TASKS; }

void flow_rt_task_set_fn(int32_t id, void *fn) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return;
    g_tasks[id].fn = (flow_task_fn)fn;
}

void *flow_rt_task_get_fn(int32_t id) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return NULL;
    return (void *)g_tasks[id].fn;
}

void flow_rt_task_set_arg(int32_t id, int32_t arg) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return;
    g_tasks[id].arg = arg;
}

int32_t flow_rt_task_get_arg(int32_t id) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return 0;
    return g_tasks[id].arg;
}

void flow_rt_task_set_result(int32_t id, int32_t result) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return;
    g_tasks[id].result = result;
}

int32_t flow_rt_task_get_result(int32_t id) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return 0;
    return g_tasks[id].result;
}

void flow_rt_task_set_done(int32_t id, int32_t done) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return;
    g_tasks[id].done = done;
}

int32_t flow_rt_task_get_done(int32_t id) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return 0;
    return g_tasks[id].done;
}

void flow_rt_task_set_spawned(int32_t id, int32_t spawned) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return;
    g_tasks[id].spawned = spawned;
}

int32_t flow_rt_task_get_spawned(int32_t id) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return 0;
    return g_tasks[id].spawned;
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
    if (pthread_create(&g_tasks[id].thread, NULL, flow_rt_task_trampoline,
                       (void *)(intptr_t)id) != 0) {
        return -1;
    }
    return 0;
}

int32_t flow_rt_task_pthread_join(int32_t id) {
    if (id < 0 || id >= FLOW_MAX_TASKS) return -1;
    return pthread_join(g_tasks[id].thread, NULL) == 0 ? 0 : -1;
}
