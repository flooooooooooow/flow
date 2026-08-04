/* FiberAsync task storage + fiber entry trampoline for Flow.
 * Logic: lib/runtime/fiber_async.flow
 */
#include "flow_fiber.h"
#include "flow_concurrency.h"

#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

#ifndef FLOW_FIBER_TASKS
#define FLOW_FIBER_TASKS 256
#endif

typedef struct {
    flow_task_fn fn;
    int32_t arg;
    int32_t result;
    int32_t done;
    int32_t fiber_id;
} flow_rt_fiber_task;

static flow_rt_fiber_task g_ftasks[FLOW_FIBER_TASKS];
static int g_ftasks_inited = 0;

static void ftasks_init_once(void) {
    if (g_ftasks_inited) return;
    for (int i = 0; i < FLOW_FIBER_TASKS; i++) {
        g_ftasks[i].fiber_id = -1;
        g_ftasks[i].done = 0;
    }
    g_ftasks_inited = 1;
}

/* Flow */
void flow_fiber_async_worker(int32_t task_id);

int32_t flow_rt_fiber_task_max(void) { return FLOW_FIBER_TASKS; }

void flow_rt_fiber_task_set_fn(int32_t id, void *fn) {
    ftasks_init_once();
    if (id < 0 || id >= FLOW_FIBER_TASKS) return;
    g_ftasks[id].fn = (flow_task_fn)fn;
}
void *flow_rt_fiber_task_get_fn(int32_t id) {
    ftasks_init_once();
    if (id < 0 || id >= FLOW_FIBER_TASKS) return NULL;
    return (void *)g_ftasks[id].fn;
}
void flow_rt_fiber_task_set_arg(int32_t id, int32_t arg) {
    ftasks_init_once();
    if (id < 0 || id >= FLOW_FIBER_TASKS) return;
    g_ftasks[id].arg = arg;
}
int32_t flow_rt_fiber_task_get_arg(int32_t id) {
    ftasks_init_once();
    if (id < 0 || id >= FLOW_FIBER_TASKS) return 0;
    return g_ftasks[id].arg;
}
void flow_rt_fiber_task_set_result(int32_t id, int32_t result) {
    ftasks_init_once();
    if (id < 0 || id >= FLOW_FIBER_TASKS) return;
    __atomic_store_n(&g_ftasks[id].result, result, __ATOMIC_RELEASE);
}
int32_t flow_rt_fiber_task_get_result(int32_t id) {
    ftasks_init_once();
    if (id < 0 || id >= FLOW_FIBER_TASKS) return 0;
    return __atomic_load_n(&g_ftasks[id].result, __ATOMIC_ACQUIRE);
}
void flow_rt_fiber_task_set_done(int32_t id, int32_t done) {
    ftasks_init_once();
    if (id < 0 || id >= FLOW_FIBER_TASKS) return;
    __atomic_store_n(&g_ftasks[id].done, done, __ATOMIC_RELEASE);
}
int32_t flow_rt_fiber_task_get_done(int32_t id) {
    ftasks_init_once();
    if (id < 0 || id >= FLOW_FIBER_TASKS) return 0;
    return __atomic_load_n(&g_ftasks[id].done, __ATOMIC_ACQUIRE);
}
void flow_rt_fiber_task_set_fiber_id(int32_t id, int32_t fid) {
    ftasks_init_once();
    if (id < 0 || id >= FLOW_FIBER_TASKS) return;
    __atomic_store_n(&g_ftasks[id].fiber_id, fid, __ATOMIC_RELEASE);
}
int32_t flow_rt_fiber_task_get_fiber_id(int32_t id) {
    ftasks_init_once();
    if (id < 0 || id >= FLOW_FIBER_TASKS) return -1;
    return __atomic_load_n(&g_ftasks[id].fiber_id, __ATOMIC_ACQUIRE);
}

int32_t flow_rt_call_task_fn(void *fn, int32_t arg); /* in flow_rt_task_store.c */

typedef struct {
    int32_t task_id;
} flow_rt_fiber_pack;

static void flow_rt_fiber_task_entry(void *p) {
    flow_rt_fiber_pack pack = *(flow_rt_fiber_pack *)p;
    free(p);
    flow_fiber_async_worker(pack.task_id);
}

int32_t flow_rt_fiber_spawn_task(int32_t task_id) {
    flow_rt_fiber_pack *pack = (flow_rt_fiber_pack *)malloc(sizeof(*pack));
    if (!pack) return -1;
    pack->task_id = task_id;
    int32_t fid = flow_fiber_spawn(flow_rt_fiber_task_entry, pack);
    if (fid < 0) {
        free(pack);
        return -1;
    }
    return fid;
}
