/* M:N cooperative fibers + asm context switch + fiber channels */
#include "flow_fiber.h"
#include "flow_concurrency.h"
#include "flow_fctx.h"

#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#ifndef FLOW_FIBER_MAX
#define FLOW_FIBER_MAX 4096
#endif

#ifndef FLOW_FIBER_STACK
#define FLOW_FIBER_STACK (64 * 1024)
#endif

#ifndef FLOW_FIBER_TASKS
#define FLOW_FIBER_TASKS 256
#endif

#ifndef FLOW_FIBER_WORKERS_MAX
#define FLOW_FIBER_WORKERS_MAX 64
#endif

#ifndef FLOW_STEAL_DEQUE
#define FLOW_STEAL_DEQUE 512
#endif

enum {
    FIBER_FREE = 0,
    FIBER_READY,
    FIBER_RUNNING,
    FIBER_PARKED,
    FIBER_EXITING, /* fn returned; stack still active until run_one observes */
    FIBER_DONE
};

typedef struct flow_fiber {
    flow_fctx ctx;
    void *stack;
    flow_fiber_fn fn;
    void *arg;
    int32_t id;
    int status;
    int32_t next_ready; /* unused with steal deques; kept for ABI stability */
} flow_fiber;

/* Per-worker deque: owner pushes/pops at tail; thieves steal at head. */
typedef struct {
    int32_t buf[FLOW_STEAL_DEQUE];
    int head;
    int tail;
    pthread_mutex_t mu;
} steal_deque;

static flow_fiber g_fibers[FLOW_FIBER_MAX];
static steal_deque g_deques[FLOW_FIBER_WORKERS_MAX];
static int g_nqueues = 1;
static unsigned g_spawn_rr = 0;
static uint64_t g_stat_local = 0;
static uint64_t g_stat_steal = 0;

static pthread_mutex_t g_run_mu = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t g_run_cv = PTHREAD_COND_INITIALIZER;
static pthread_mutex_t g_slot_mu = PTHREAD_MUTEX_INITIALIZER;

static _Thread_local int32_t g_current = -1;
static _Thread_local flow_fctx g_sched_fctx;
static _Thread_local int g_worker_id = 0; /* which deque this OS thread owns */

static int g_inited = 0;
static int g_stop = 0;
static int32_t g_maxprocs = 0; /* 0 = unset → detect */
static int g_workers_live = 0;
static pthread_t g_workers[FLOW_FIBER_WORKERS_MAX];
static int g_active_fibers = 0; /* spawned - done */

void flow_fiber_asm_done(void);

static int32_t detect_ncpu(void) {
    long n = sysconf(_SC_NPROCESSORS_ONLN);
    if (n < 1) n = 1;
    if (n > FLOW_FIBER_WORKERS_MAX) n = FLOW_FIBER_WORKERS_MAX;
    return (int32_t)n;
}

void flow_fiber_set_maxprocs(int32_t n) {
    if (n < 1) n = 1;
    if (n > FLOW_FIBER_WORKERS_MAX) n = FLOW_FIBER_WORKERS_MAX;
    g_maxprocs = n;
}

int32_t flow_fiber_maxprocs(void) {
    if (g_maxprocs > 0) return g_maxprocs;
    const char *e = getenv("FLOW_MAXPROCS");
    if (e && e[0]) {
        int v = atoi(e);
        if (v >= 1) {
            flow_fiber_set_maxprocs(v);
            return g_maxprocs;
        }
    }
    return detect_ncpu();
}

static int deque_empty(steal_deque *d) {
    return d->head == d->tail;
}

static int any_work(void) {
    for (int i = 0; i < g_nqueues; i++) {
        if (!deque_empty(&g_deques[i])) return 1;
    }
    return 0;
}

/* Caller holds d->mu. Returns 1 on push. */
static int deque_push_tail(steal_deque *d, int32_t id) {
    int next = (d->tail + 1) % FLOW_STEAL_DEQUE;
    if (next == d->head) return 0; /* full */
    d->buf[d->tail] = id;
    d->tail = next;
    return 1;
}

/* Claim READY→RUNNING so finish_park and thieves cannot both schedule. */
static int claim_ready(int32_t id) {
    int expected = FIBER_READY;
    return __atomic_compare_exchange_n(&g_fibers[id].status, &expected, FIBER_RUNNING,
                                       0, __ATOMIC_ACQ_REL, __ATOMIC_ACQUIRE);
}

/* Owner pop from tail. Caller holds d->mu. Skips stale / already-claimed. */
static int32_t deque_pop_tail(steal_deque *d) {
    while (d->head != d->tail) {
        int prev = (d->tail - 1 + FLOW_STEAL_DEQUE) % FLOW_STEAL_DEQUE;
        int32_t id = d->buf[prev];
        d->tail = prev;
        if (id >= 0 && id < FLOW_FIBER_MAX && claim_ready(id)) {
            return id;
        }
    }
    return -1;
}

/* Thief steal from head. Caller holds d->mu. */
static int32_t deque_steal_head(steal_deque *d) {
    while (d->head != d->tail) {
        int32_t id = d->buf[d->head];
        d->head = (d->head + 1) % FLOW_STEAL_DEQUE;
        if (id >= 0 && id < FLOW_FIBER_MAX && claim_ready(id)) {
            return id;
        }
    }
    return -1;
}

static void wake_workers(void) {
    pthread_mutex_lock(&g_run_mu);
    pthread_cond_signal(&g_run_cv);
    pthread_mutex_unlock(&g_run_mu);
}

/* Enqueue a fiber already marked READY. Never nests with g_run_mu. */
static void ready_enqueue(int32_t id) {
    int q = g_worker_id;
    if (q < 0 || q >= g_nqueues) {
        q = (int)(g_spawn_rr++ % (unsigned)g_nqueues);
    }
    if (q < 0 || q >= g_nqueues) q = 0;

    steal_deque *d = &g_deques[q];
    pthread_mutex_lock(&d->mu);
    if (deque_push_tail(d, id)) {
        pthread_mutex_unlock(&d->mu);
        wake_workers();
        return;
    }
    pthread_mutex_unlock(&d->mu);

    for (int i = 0; i < g_nqueues; i++) {
        steal_deque *o = &g_deques[i];
        pthread_mutex_lock(&o->mu);
        if (deque_push_tail(o, id)) {
            pthread_mutex_unlock(&o->mu);
            wake_workers();
            return;
        }
        pthread_mutex_unlock(&o->mu);
    }
    /* Overflow: leave PARKED so a later unpark can retry. */
    g_fibers[id].status = FIBER_PARKED;
}

static void ready_push(int32_t id) {
    g_fibers[id].status = FIBER_READY;
    ready_enqueue(id);
}

/* Pop local or steal. Updates stats. May block briefly on empty. */
static int32_t ready_take(void) {
    int me = g_worker_id;
    if (me < 0 || me >= g_nqueues) me = 0;

    steal_deque *local = &g_deques[me];
    pthread_mutex_lock(&local->mu);
    int32_t id = deque_pop_tail(local);
    pthread_mutex_unlock(&local->mu);
    if (id >= 0) {
        __atomic_fetch_add(&g_stat_local, 1, __ATOMIC_RELAXED);
        return id;
    }

    /* Steal from victims */
    for (int off = 1; off < g_nqueues; off++) {
        int v = (me + off) % g_nqueues;
        steal_deque *victim = &g_deques[v];
        pthread_mutex_lock(&victim->mu);
        id = deque_steal_head(victim);
        pthread_mutex_unlock(&victim->mu);
        if (id >= 0) {
            __atomic_fetch_add(&g_stat_steal, 1, __ATOMIC_RELAXED);
            return id;
        }
    }
    return -1;
}

static void fiber_entry(void *unused) {
    (void)unused;
    int32_t id = g_current;
    flow_fiber *f = &g_fibers[id];
    f->fn(f->arg);
    flow_fiber_asm_done();
}

void flow_fiber_asm_done(void) {
    int32_t id = g_current;
    if (id >= 0) {
        /* EXITING: stack/ctx still live until the hosting worker's swap returns */
        g_fibers[id].status = FIBER_EXITING;
        pthread_mutex_lock(&g_run_mu);
        g_active_fibers--;
        pthread_cond_broadcast(&g_run_cv);
        pthread_mutex_unlock(&g_run_mu);
        g_current = -1;
        flow_fctx_swap(&g_fibers[id].ctx, &g_sched_fctx);
    }
    for (;;) pause();
}

static void run_one(int32_t id) {
    g_current = id;
    /* Already claimed READY→RUNNING in ready_take (or handoff path). */
    if (g_fibers[id].status != FIBER_RUNNING) {
        g_fibers[id].status = FIBER_RUNNING;
    }
    flow_fctx_swap(&g_sched_fctx, &g_fibers[id].ctx);
    g_current = -1;
    /* Only now is the fiber stack idle and the slot reusable. */
    if (g_fibers[id].status == FIBER_EXITING) {
        g_fibers[id].status = FIBER_DONE;
    } else if (g_fibers[id].status == FIBER_READY) {
        /* Yield: enqueue only after ctx is saved (avoids dual-stack race). */
        ready_enqueue(id);
    }
}

void flow_fiber_steal_stats(uint64_t *local_pops, uint64_t *steals) {
    if (local_pops) *local_pops = __atomic_load_n(&g_stat_local, __ATOMIC_RELAXED);
    if (steals) *steals = __atomic_load_n(&g_stat_steal, __ATOMIC_RELAXED);
}

/* Flow-friendly accessors (no out-params). Namespaced flow_rt_* to avoid
 * colliding with @flow_api wrappers in lib/runtime/fiber_benches.flow. */
int64_t flow_rt_fiber_local_pops(void) {
    return (int64_t)__atomic_load_n(&g_stat_local, __ATOMIC_RELAXED);
}

int64_t flow_rt_fiber_steals(void) {
    return (int64_t)__atomic_load_n(&g_stat_steal, __ATOMIC_RELAXED);
}

void flow_rt_fiber_steal_stats_reset(void) {
    __atomic_store_n(&g_stat_local, 0, __ATOMIC_RELAXED);
    __atomic_store_n(&g_stat_steal, 0, __ATOMIC_RELAXED);
}

typedef struct {
    int worker_id;
} worker_arg;

static void *worker_main(void *arg) {
    worker_arg *wa = (worker_arg *)arg;
    g_worker_id = wa ? wa->worker_id : 1;
    free(wa);
    for (;;) {
        int32_t id = ready_take();
        if (id >= 0) {
            run_one(id);
            continue;
        }
        pthread_mutex_lock(&g_run_mu);
        while (!any_work() && !g_stop) {
            pthread_cond_wait(&g_run_cv, &g_run_mu);
        }
        int stop = g_stop && !any_work();
        pthread_mutex_unlock(&g_run_mu);
        if (stop) break;
    }
    return NULL;
}

static void start_workers(void) {
    int32_t n = flow_fiber_maxprocs();
    g_maxprocs = n;
    g_nqueues = n < 1 ? 1 : n;
    if (g_nqueues > FLOW_FIBER_WORKERS_MAX) g_nqueues = FLOW_FIBER_WORKERS_MAX;
    /* Worker 0 = calling thread (schedule_loop / run_main). Extra = n-1. */
    int extra = n - 1;
    if (extra < 0) extra = 0;
    g_workers_live = 0;
    g_stop = 0;
    g_worker_id = 0;
    for (int i = 0; i < extra; i++) {
        worker_arg *wa = (worker_arg *)malloc(sizeof(*wa));
        if (!wa) continue;
        wa->worker_id = i + 1;
        if (pthread_create(&g_workers[i], NULL, worker_main, wa) == 0) {
            g_workers_live++;
        } else {
            free(wa);
        }
    }
}

void flow_fiber_init(void) {
    if (g_inited) return;
    memset(g_fibers, 0, sizeof(g_fibers));
    for (int i = 0; i < FLOW_FIBER_MAX; i++) {
        g_fibers[i].id = i;
        g_fibers[i].status = FIBER_FREE;
        g_fibers[i].next_ready = -1;
    }
    for (int i = 0; i < FLOW_FIBER_WORKERS_MAX; i++) {
        g_deques[i].head = g_deques[i].tail = 0;
        pthread_mutex_init(&g_deques[i].mu, NULL);
    }
    g_stat_local = g_stat_steal = 0;
    g_spawn_rr = 0;
    g_active_fibers = 0;
    g_inited = 1;
    start_workers();
}

void flow_fiber_shutdown(void) {
    if (!g_inited) return;
    pthread_mutex_lock(&g_run_mu);
    g_stop = 1;
    pthread_cond_broadcast(&g_run_cv);
    pthread_mutex_unlock(&g_run_mu);
    for (int i = 0; i < g_workers_live; i++) {
        pthread_join(g_workers[i], NULL);
    }
    g_workers_live = 0;
    for (int i = 0; i < FLOW_FIBER_MAX; i++) {
        free(g_fibers[i].stack);
        g_fibers[i].stack = NULL;
        g_fibers[i].status = FIBER_FREE;
    }
    for (int i = 0; i < FLOW_FIBER_WORKERS_MAX; i++) {
        g_deques[i].head = g_deques[i].tail = 0;
    }
    g_active_fibers = 0;
    g_inited = 0;
    g_stop = 0;
}

int32_t flow_fiber_spawn(flow_fiber_fn fn, void *arg) {
    if (!fn) return -1;
#if !FLOW_FCTX_ASM
    (void)arg;
    return -1;
#else
    flow_fiber_init();
    pthread_mutex_lock(&g_slot_mu);
    int32_t id = -1;
    for (int i = 0; i < FLOW_FIBER_MAX; i++) {
        if (g_fibers[i].status == FIBER_FREE || g_fibers[i].status == FIBER_DONE) {
            id = i;
            break;
        }
    }
    if (id < 0) {
        pthread_mutex_unlock(&g_slot_mu);
        return -1;
    }
    flow_fiber *f = &g_fibers[id];
    f->status = FIBER_READY; /* reserve */
    pthread_mutex_unlock(&g_slot_mu);

    if (!f->stack) {
        if (posix_memalign(&f->stack, 16, FLOW_FIBER_STACK) != 0) {
            f->stack = NULL;
            f->status = FIBER_FREE;
            return -1;
        }
    }
    f->fn = fn;
    f->arg = arg;
    flow_fctx_init(&f->ctx, f->stack, FLOW_FIBER_STACK, fiber_entry, NULL);
    pthread_mutex_lock(&g_run_mu);
    g_active_fibers++;
    pthread_mutex_unlock(&g_run_mu);
    ready_enqueue(id); /* status already READY from slot reserve */
    return id;
#endif
}

static void schedule_loop(int32_t until_id) {
    g_worker_id = 0;
    for (;;) {
        if (until_id >= 0 && g_fibers[until_id].status == FIBER_DONE) break;
        if (until_id < 0 && g_active_fibers <= 0 && !any_work()) break;

        int32_t id = ready_take();
        if (id >= 0) {
            run_one(id);
            continue;
        }

        pthread_mutex_lock(&g_run_mu);
        while (!any_work() && !g_stop) {
            if (until_id >= 0 && g_fibers[until_id].status == FIBER_DONE) break;
            if (until_id < 0 && g_active_fibers <= 0) break;
            struct timespec ts;
            clock_gettime(CLOCK_REALTIME, &ts);
            ts.tv_nsec += 1000000L;
            if (ts.tv_nsec >= 1000000000L) {
                ts.tv_sec++;
                ts.tv_nsec -= 1000000000L;
            }
            pthread_cond_timedwait(&g_run_cv, &g_run_mu, &ts);
            if (until_id >= 0 && g_fibers[until_id].status == FIBER_DONE) break;
            if (until_id < 0 && g_active_fibers <= 0 && !any_work()) break;
        }
        pthread_mutex_unlock(&g_run_mu);

        if (until_id >= 0 && g_fibers[until_id].status == FIBER_DONE) break;
        if (until_id < 0 && g_active_fibers <= 0 && !any_work()) break;
    }
}

void flow_fiber_run(void) {
    flow_fiber_init();
    schedule_loop(-1);
}

void flow_fiber_run_until(int32_t id) {
    flow_fiber_init();
    if (id < 0 || id >= FLOW_FIBER_MAX) return;
    schedule_loop(id);
}

void flow_fiber_yield(void) {
    if (g_current < 0) return;
    int32_t self = g_current;
    /* Mark READY but do not enqueue until run_one observes the saved ctx. */
    g_fibers[self].status = FIBER_READY;
    flow_fctx_swap(&g_fibers[self].ctx, &g_sched_fctx);
}

void flow_fiber_park(void) {
    if (g_current < 0) return;
    int32_t self = g_current;
    g_fibers[self].status = FIBER_PARKED;
    flow_fctx_swap(&g_fibers[self].ctx, &g_sched_fctx);
}

void flow_fiber_unpark(int32_t id) {
    if (id < 0 || id >= FLOW_FIBER_MAX) return;
    int expected = FIBER_PARKED;
    if (__atomic_compare_exchange_n(&g_fibers[id].status, &expected, FIBER_READY,
                                    0, __ATOMIC_ACQ_REL, __ATOMIC_ACQUIRE)) {
        ready_enqueue(id);
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
    /* Unpark raced: claim READY→RUNNING and continue; deque slot is stale. */
    if (claim_ready(self)) return;
    if (g_fibers[self].status == FIBER_RUNNING) return;
    flow_fctx_swap(&g_fibers[self].ctx, &g_sched_fctx);
}

/* ---- fiber channel ----------------------------------------------------- */

typedef struct {
    int32_t *buf;
    int32_t cap;
    int32_t size;
    int32_t head;
    int32_t tail;
    int closed;
    int32_t send_wait;
    int32_t recv_wait;
    pthread_mutex_t mu;
} flow_fchan;

static void fchan_init(flow_fchan *ch, int32_t cap) {
    if (cap < 1) cap = 1;
    ch->buf = (int32_t *)malloc((size_t)cap * sizeof(int32_t));
    ch->cap = cap;
    ch->size = ch->head = ch->tail = 0;
    ch->closed = 0;
    ch->send_wait = ch->recv_wait = -1;
    pthread_mutex_init(&ch->mu, NULL);
}

static void fchan_destroy(flow_fchan *ch) {
    pthread_mutex_destroy(&ch->mu);
    free(ch->buf);
}

static void fiber_park_or_handoff(int32_t handoff) {
    int32_t self = g_current;
    g_fibers[self].status = FIBER_PARKED;
    /* Symmetric transfer only safe on M:1 (same OS thread). */
    if (flow_fiber_maxprocs() == 1 && handoff >= 0 &&
        (g_fibers[handoff].status == FIBER_PARKED ||
         g_fibers[handoff].status == FIBER_READY)) {
        /* Claim READY if already queued; leave stale deque entry. */
        if (g_fibers[handoff].status == FIBER_READY) {
            (void)claim_ready(handoff);
        } else {
            g_fibers[handoff].status = FIBER_RUNNING;
        }
        g_current = handoff;
        g_fibers[handoff].status = FIBER_RUNNING;
        flow_fctx_swap(&g_fibers[self].ctx, &g_fibers[handoff].ctx);
        return;
    }
    if (handoff >= 0) flow_fiber_unpark(handoff);
    flow_fctx_swap(&g_fibers[self].ctx, &g_sched_fctx);
}

static void fchan_send(flow_fchan *ch, int32_t v) {
    for (;;) {
        pthread_mutex_lock(&ch->mu);
        if (ch->closed) {
            pthread_mutex_unlock(&ch->mu);
            return;
        }
        if (ch->size < ch->cap) {
            ch->buf[ch->tail] = v;
            ch->tail = (ch->tail + 1) % ch->cap;
            ch->size++;
            int32_t w = ch->recv_wait;
            ch->recv_wait = -1;
            pthread_mutex_unlock(&ch->mu);
            if (w >= 0) flow_fiber_unpark(w);
            return;
        }
        int32_t waiter = ch->recv_wait;
        ch->send_wait = g_current;
        ch->recv_wait = -1;
        pthread_mutex_unlock(&ch->mu);
        fiber_park_or_handoff(waiter);
    }
}

static int fchan_recv(flow_fchan *ch, int32_t *out) {
    for (;;) {
        pthread_mutex_lock(&ch->mu);
        if (ch->size > 0) {
            *out = ch->buf[ch->head];
            ch->head = (ch->head + 1) % ch->cap;
            ch->size--;
            int32_t w = ch->send_wait;
            ch->send_wait = -1;
            pthread_mutex_unlock(&ch->mu);
            if (w >= 0) flow_fiber_unpark(w);
            return 1;
        }
        if (ch->closed) {
            pthread_mutex_unlock(&ch->mu);
            return 0;
        }
        int32_t waiter = ch->send_wait;
        ch->recv_wait = g_current;
        ch->send_wait = -1;
        pthread_mutex_unlock(&ch->mu);
        fiber_park_or_handoff(waiter);
    }
}

typedef struct {
    flow_fchan *ch;
    int32_t n;
} fiber_ping_args;

static void fiber_sender(void *p) {
    fiber_ping_args *a = (fiber_ping_args *)p;
    for (int32_t i = 0; i < a->n; i++) fchan_send(a->ch, i);
}

static void fiber_receiver(void *p) {
    fiber_ping_args *a = (fiber_ping_args *)p;
    int32_t v = 0;
    for (int32_t i = 0; i < a->n; i++) {
        if (!fchan_recv(a->ch, &v)) break;
    }
}

static int64_t now_ns(void) {
    struct timespec ts;
#if defined(CLOCK_MONOTONIC)
    clock_gettime(CLOCK_MONOTONIC, &ts);
#else
    clock_gettime(CLOCK_REALTIME, &ts);
#endif
    return (int64_t)ts.tv_sec * 1000000000LL + (int64_t)ts.tv_nsec;
}

int64_t flow_rt_bench_fiber_chan_pingpong_body(int32_t n, int32_t buf) {
    if (n <= 0) return 0;
#if !FLOW_FCTX_ASM
    (void)buf;
    return -1;
#else
    flow_fiber_shutdown();
    flow_fiber_set_maxprocs(1);
    flow_fiber_init();

    flow_fchan ch;
    fchan_init(&ch, buf);
    fiber_ping_args args = {&ch, n};

    int64_t t0 = now_ns();
    if (flow_fiber_spawn(fiber_receiver, &args) < 0 ||
        flow_fiber_spawn(fiber_sender, &args) < 0) {
        fchan_destroy(&ch);
        return -1;
    }
    flow_fiber_run();
    int64_t t1 = now_ns();

    fchan_destroy(&ch);
    flow_fiber_shutdown();
    return t1 - t0;
#endif
}

/* flow_bench_fiber_chan_pingpong_ns → lib/runtime/fiber_benches.flow */

/* ---- fan-out sum (M:N) ------------------------------------------------- */

typedef struct {
    int32_t start;
    int32_t end;
    int64_t *out;
} fanout_args;

static void fanout_worker(void *p) {
    fanout_args *a = (fanout_args *)p;
    int64_t s = 0;
    for (int32_t i = a->start; i < a->end; i++) s += i;
    *a->out = s;
}

int64_t flow_rt_bench_fiber_fanout_sum_body(int32_t n, int32_t fibers) {
    if (n <= 0) return 0;
    if (fibers < 1) fibers = 1;
#if !FLOW_FCTX_ASM
    return -1;
#else
    flow_fiber_shutdown();
    g_maxprocs = 0;
    flow_fiber_init();

    int64_t *partials = (int64_t *)calloc((size_t)fibers, sizeof(int64_t));
    fanout_args *args = (fanout_args *)calloc((size_t)fibers, sizeof(fanout_args));
    if (!partials || !args) {
        free(partials);
        free(args);
        return -1;
    }
    int32_t chunk = (n + fibers - 1) / fibers;
    for (int32_t i = 0; i < fibers; i++) {
        int32_t s = i * chunk;
        int32_t e = s + chunk;
        if (s >= n) {
            args[i].start = 0;
            args[i].end = 0;
        } else {
            if (e > n) e = n;
            args[i].start = s;
            args[i].end = e;
        }
        args[i].out = &partials[i];
        if (args[i].end > args[i].start) {
            flow_fiber_spawn(fanout_worker, &args[i]);
        }
    }
    flow_fiber_run();
    int64_t total = 0;
    for (int32_t i = 0; i < fibers; i++) total += partials[i];
    free(partials);
    free(args);
    flow_fiber_shutdown();
    return total;
#endif
}

/* flow_bench_fiber_fanout_sum → lib/runtime/fiber_benches.flow */

/* FiberAsync → lib/runtime/fiber_async.flow (+ flow_rt_fiber_async.c) */

static flow_main_fn g_main_fn = NULL;
static int32_t g_main_result = 0;

static void main_fiber_entry(void *arg) {
    (void)arg;
    g_main_result = g_main_fn ? g_main_fn() : 0;
}

int32_t flow_fiber_run_main(flow_main_fn fn) {
    if (!fn) return 0;
    /* Already on a fiber (nested): just call through. */
    if (g_current >= 0) return fn();
    flow_fiber_init();
    g_main_fn = fn;
    g_main_result = 0;
    int32_t id = flow_fiber_spawn(main_fiber_entry, NULL);
    if (id < 0) return fn();
    flow_fiber_run_until(id);
    return g_main_result;
}
