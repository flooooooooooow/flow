/* Cooperative stackful fibers for WebAssembly — built on emscripten's fiber
 * API (Asyncify stack switching). This is the wasm analogue of the native
 * runtime/flow_fiber.c + runtime/flow_fctx_*.S asm context switch: wasm has
 * no way to hand-switch the stack pointer, and a plain setjmp/longjmp cannot
 * move between stacks, so emscripten_fiber_swap (itself setjmp/longjmp-class
 * machinery backed by Asyncify) is the supported context-switch primitive.
 *
 * wasm is single-threaded, so this scheduler is M:1 — every fiber multiplexes
 * on one OS/JS thread. flow_fiber_set_maxprocs() is accepted for API
 * compatibility, but the effective worker count is always 1 (reporting
 * maxprocs()=1 unless set, mirroring the native detect path).
 *
 * Linked into wasm builds that reach lib/runtime/fiber_async.flow
 * (FiberAsync / flow_fiber_run_main). runtime/flow_rt_fiber_async.c (the
 * async task storage) links alongside; the pthread-backed pieces of
 * flow_rt_task_store.c / flow_netpoll_fiber.c are replaced here by
 * single-threaded equivalents.
 */
#include "flow_fiber.h"
#include "flow_concurrency.h"

#include <emscripten/emscripten.h>
#include <emscripten/fiber.h>

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifndef FLOW_FIBER_MAX
#define FLOW_FIBER_MAX 256
#endif

/* Per-fiber C stack (native uses 64 KB; Flow bodies + printf get 4x). */
#ifndef FLOW_FIBER_C_STACK
#define FLOW_FIBER_C_STACK (256 * 1024)
#endif

/* Per-fiber Asyncify stack: must hold the deepest suspend's stack data. */
#ifndef FLOW_FIBER_ASYNCIFY_STACK
#define FLOW_FIBER_ASYNCIFY_STACK (64 * 1024)
#endif

enum {
    FIBER_FREE = 0,
    FIBER_READY,
    FIBER_RUNNING,
    FIBER_PARKED,
    FIBER_SLEEPING, /* parked until wake_at (flow_netpoll_fiber_sleep_ms) */
    FIBER_EXITING,  /* fn returned; slot reusable once run_one observes */
    FIBER_DONE
};

typedef struct wasm_fiber {
    emscripten_fiber_t ectx;
    void *c_stack;        /* malloc'd C stack region (kept for reuse) */
    void *asyncify_stack; /* malloc'd asyncify stack region */
    flow_fiber_fn fn;
    void *arg;
    int status;
    double wake_at; /* ms epoch (emscripten_get_now); valid while SLEEPING */
} wasm_fiber;

static wasm_fiber g_fibers[FLOW_FIBER_MAX];
static int g_inited = 0;
static int32_t g_maxprocs = 0; /* 0 = unset -> 1 on wasm */
static int32_t g_current = -1;
static int g_active = 0; /* spawned - exited */

/* Scheduler context, captured on the main C stack the first time the
 * scheduler runs (flow_fiber_run_main / flow_fiber_run call flow_fiber_init
 * before any spawn, so the first capture is always from main's stack). */
static emscripten_fiber_t g_sched;
static void *g_sched_asyncify;

/* FIFO ready queue. */
static int32_t g_rq[FLOW_FIBER_MAX];
static int g_rq_head = 0;
static int g_rq_tail = 0;

static int64_t g_stat_local = 0;
static int64_t g_stat_steal = 0;

/* ---- queue helpers ------------------------------------------------------ */

static int rq_empty(void) { return g_rq_head == g_rq_tail; }

static void rq_push(int32_t id) {
    int next = (g_rq_tail + 1) % FLOW_FIBER_MAX;
    if (next == g_rq_head) return; /* full: drop (spawner treats as lost) */
    g_rq[g_rq_tail] = id;
    g_rq_tail = next;
}

static int32_t rq_pop(void) {
    if (rq_empty()) return -1;
    int32_t id = g_rq[g_rq_head];
    g_rq_head = (g_rq_head + 1) % FLOW_FIBER_MAX;
    g_stat_local++;
    return id;
}

/* ---- public API (flow_fiber.h) ------------------------------------------ */

void flow_fiber_set_maxprocs(int32_t n) {
    if (n < 1) n = 1;
    g_maxprocs = n; /* advisory: wasm schedules M:1 regardless */
}

int32_t flow_fiber_maxprocs(void) {
    if (g_maxprocs > 0) return g_maxprocs;
    return 1; /* no OS threads on wasm */
}

static void sched_capture(void) {
    if (g_sched_asyncify) return;
    g_sched_asyncify = malloc(FLOW_FIBER_ASYNCIFY_STACK);
    emscripten_fiber_init_from_current_context(
        &g_sched, g_sched_asyncify, FLOW_FIBER_ASYNCIFY_STACK);
}

void flow_fiber_init(void) {
    if (g_inited) return;
    memset(g_fibers, 0, sizeof(g_fibers));
    g_rq_head = g_rq_tail = 0;
    g_stat_local = g_stat_steal = 0;
    g_active = 0;
    g_current = -1;
    sched_capture();
    g_inited = 1;
}

void flow_fiber_shutdown(void) {
    if (!g_inited) return;
    for (int i = 0; i < FLOW_FIBER_MAX; i++) {
        free(g_fibers[i].c_stack);
        free(g_fibers[i].asyncify_stack);
        g_fibers[i].c_stack = NULL;
        g_fibers[i].asyncify_stack = NULL;
        g_fibers[i].status = FIBER_FREE;
    }
    free(g_sched_asyncify);
    g_sched_asyncify = NULL;
    g_active = 0;
    g_inited = 0;
}

/* Yield the current fiber back to the scheduler, saving its context. */
static void fiber_swap_to_sched(void) {
    int32_t self = g_current;
    emscripten_fiber_swap(&g_fibers[self].ectx, &g_sched);
}

/* First-swap-in entry for every fiber. Runs the body; on return the fiber is
 * done and control goes back to the scheduler (never resumed again). */
static void wasm_fiber_entry(void *arg) {
    int32_t id = (int32_t)(intptr_t)arg;
    g_fibers[id].fn(g_fibers[id].arg);
    g_fibers[id].status = FIBER_EXITING;
    g_active--;
    emscripten_fiber_swap(&g_fibers[id].ectx, &g_sched);
    abort(); /* never resumed */
}

int32_t flow_fiber_spawn(flow_fiber_fn fn, void *arg) {
    if (!fn) return -1;
    flow_fiber_init();
    int32_t id = -1;
    for (int i = 0; i < FLOW_FIBER_MAX; i++) {
        if (g_fibers[i].status == FIBER_FREE || g_fibers[i].status == FIBER_DONE) {
            id = i;
            break;
        }
    }
    if (id < 0) return -1;
    wasm_fiber *f = &g_fibers[id];
    if (!f->c_stack) {
        f->c_stack = malloc(FLOW_FIBER_C_STACK);
        if (!f->c_stack) return -1;
    }
    if (!f->asyncify_stack) {
        f->asyncify_stack = malloc(FLOW_FIBER_ASYNCIFY_STACK);
        if (!f->asyncify_stack) {
            free(f->c_stack);
            f->c_stack = NULL;
            return -1;
        }
    }
    f->fn = fn;
    f->arg = arg;
    f->wake_at = 0;
    emscripten_fiber_init(&f->ectx, wasm_fiber_entry, (void *)(intptr_t)id,
                          f->c_stack, FLOW_FIBER_C_STACK,
                          f->asyncify_stack, FLOW_FIBER_ASYNCIFY_STACK);
    f->status = FIBER_READY;
    g_active++;
    rq_push(id);
    return id;
}

static void run_one(int32_t id) {
    g_current = id;
    g_fibers[id].status = FIBER_RUNNING;
    emscripten_fiber_swap(&g_sched, &g_fibers[id].ectx);
    g_current = -1;
    int st = g_fibers[id].status;
    if (st == FIBER_EXITING) {
        g_fibers[id].status = FIBER_DONE;
    } else if (st == FIBER_READY) {
        rq_push(id); /* yield: re-enqueue only now that the ctx is saved */
    }
    /* PARKED / SLEEPING: resume only via unpark / wake_due_sleepers */
}

static int have_sleepers(void) {
    for (int i = 0; i < FLOW_FIBER_MAX; i++) {
        if (g_fibers[i].status == FIBER_SLEEPING) return 1;
    }
    return 0;
}

static double earliest_wake(void) {
    double best = 0;
    int found = 0;
    for (int i = 0; i < FLOW_FIBER_MAX; i++) {
        if (g_fibers[i].status == FIBER_SLEEPING &&
            (!found || g_fibers[i].wake_at < best)) {
            best = g_fibers[i].wake_at;
            found = 1;
        }
    }
    return found ? best : 0;
}

/* Wake every sleeping fiber whose deadline has passed, in slot order, so
 * equal-delay tasks resume in the order they went to sleep (round-robin). */
static void wake_due_sleepers(void) {
    double now = emscripten_get_now();
    for (int i = 0; i < FLOW_FIBER_MAX; i++) {
        wasm_fiber *f = &g_fibers[i];
        if (f->status == FIBER_SLEEPING && f->wake_at <= now) {
            f->status = FIBER_READY;
            rq_push(i);
        }
    }
}

static void schedule_loop(int32_t until_id) {
    for (;;) {
        if (until_id >= 0) {
            if (g_fibers[until_id].status == FIBER_DONE) break;
        } else if (g_active <= 0 && rq_empty() && !have_sleepers()) {
            break;
        }

        wake_due_sleepers();

        int32_t id = rq_pop();
        if (id >= 0) {
            run_one(id);
            continue;
        }

        if (have_sleepers()) {
            /* Every fiber is asleep: busy-wait until the earliest deadline.
             * (There is no event loop to hand back to — this is a console
             * program running main to completion.) */
            double next = earliest_wake();
            while (emscripten_get_now() < next) { /* spin */ }
            continue;
        }
        break;
    }
}

void flow_fiber_run(void) {
    flow_fiber_init();
    schedule_loop(-1);
}

void flow_fiber_run_until(int32_t id) {
    flow_fiber_init();
    if (id < 0 || id >= FLOW_FIBER_MAX) return;
    if (g_current >= 0) return; /* no nested scheduling on M:1 */
    schedule_loop(id);
}

void flow_fiber_yield(void) {
    if (g_current < 0) return;
    g_fibers[g_current].status = FIBER_READY;
    fiber_swap_to_sched();
}

void flow_fiber_park(void) {
    if (g_current < 0) return;
    g_fibers[g_current].status = FIBER_PARKED;
    fiber_swap_to_sched();
}

void flow_fiber_unpark(int32_t id) {
    if (id < 0 || id >= FLOW_FIBER_MAX) return;
    if (g_fibers[id].status == FIBER_PARKED) {
        g_fibers[id].status = FIBER_READY;
        rq_push(id);
    }
}

int32_t flow_fiber_current_id(void) {
    return g_current;
}

int flow_fiber_prepare_park(void) {
    if (g_current < 0) return 0;
    g_fibers[g_current].status = FIBER_PARKED;
    return 1;
}

void flow_fiber_finish_park(void) {
    int32_t self = g_current;
    if (self < 0) return;
    if (g_fibers[self].status == FIBER_RUNNING) return; /* unpark raced */
    fiber_swap_to_sched();
}

void flow_fiber_steal_stats(uint64_t *local_pops, uint64_t *steals) {
    if (local_pops) *local_pops = (uint64_t)g_stat_local;
    if (steals) *steals = (uint64_t)g_stat_steal;
}

int64_t flow_rt_fiber_local_pops(void) { return g_stat_local; }
int64_t flow_rt_fiber_steals(void) { return g_stat_steal; }

void flow_rt_fiber_steal_stats_reset(void) {
    g_stat_local = 0;
    g_stat_steal = 0;
}

/* ---- run user main on a fiber (mid-function Flow-frame suspend) ---------- */

static flow_main_fn g_main_fn = NULL;
static int32_t g_main_result = 0;

static void main_fiber_entry(void *arg) {
    (void)arg;
    g_main_result = g_main_fn ? g_main_fn() : 0;
}

int32_t flow_fiber_run_main(flow_main_fn fn) {
    if (!fn) return 0;
    if (g_current >= 0) return fn(); /* already on a fiber: call through */
    flow_fiber_init();
    g_main_fn = fn;
    g_main_result = 0;
    int32_t id = flow_fiber_spawn(main_fiber_entry, NULL);
    if (id < 0) return fn();
    flow_fiber_run_until(id);
    return g_main_result;
}

/* ---- FiberAsync glue (wasm replacements for pthread-backed runtime) ------- */

void flow_rt_usleep(int32_t usec) {
    (void)usec;
    /* No-op on wasm: single-threaded, so the "fiber still running on a pool
     * worker" backoff inside flow_fiber_async_join can never trigger. */
}

/* flow_rt_call_task_fn lives in flow_rt_task_store.c (pthreads) natively;
 * this is the portable wasm definition. */
int32_t flow_rt_call_task_fn(void *fn, int32_t arg) {
    if (!fn) return 0;
    return ((int32_t (*)(int32_t))fn)(arg);
}

/* Fiber-aware sleep: park the current fiber and let the scheduler resume it
 * when its deadline passes (flow_fiber_async_delay's on-fiber path). */
void flow_netpoll_fiber_sleep_ms(int32_t ms) {
    if (ms <= 0) return;
    if (g_current < 0) return; /* off-fiber: no blocking sleep in wasm */
    g_fibers[g_current].wake_at = emscripten_get_now() + (double)ms;
    g_fibers[g_current].status = FIBER_SLEEPING;
    fiber_swap_to_sched();
}
