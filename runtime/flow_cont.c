#include "flow_cont.h"
#include "flow_fiber.h"
#include "flow_fctx.h"

#include <pthread.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifndef FLOW_FIBER_MAX
#define FLOW_FIBER_MAX 4096
#endif

struct flow_cont {
    void *stack;
    void *value;
    int live;
    int resumed;
};

typedef struct {
    flow_reset_body body;
    void *arg;
    void *result;
    flow_cont *captured;
    int shifted;
} reset_frame;

static _Thread_local reset_frame *g_reset = NULL;

/* Per-fiber one-shot shift state (M:N-safe). */
static int g_shift_pending[FLOW_FIBER_MAX];
static int32_t g_shift_value[FLOW_FIBER_MAX];
static pthread_mutex_t g_shift_mu = PTHREAD_MUTEX_INITIALIZER;

void *flow_reset_ex(flow_reset_body body, void *arg, flow_cont **out_k) {
    if (!body) {
        if (out_k) *out_k = NULL;
        return NULL;
    }
    reset_frame frame;
    memset(&frame, 0, sizeof(frame));
    frame.body = body;
    frame.arg = arg;
    reset_frame *prev = g_reset;
    g_reset = &frame;
    void *r = body(arg, NULL);
    if (frame.shifted) r = frame.result;
    g_reset = prev;
    if (out_k) {
        *out_k = frame.captured;
    } else if (frame.captured) {
        flow_cont_free(frame.captured);
    }
    return r;
}

void *flow_reset(flow_reset_body body, void *arg) {
    return flow_reset_ex(body, arg, NULL);
}

void *flow_shift(flow_cont **out_k, void *value) {
    if (!g_reset) {
        if (out_k) *out_k = NULL;
        return NULL;
    }
    flow_cont *k = (flow_cont *)calloc(1, sizeof(flow_cont));
    if (!k) return NULL;
    k->value = value;
    k->live = 1;
    g_reset->shifted = 1;
    g_reset->result = value;
    g_reset->captured = k;
    if (out_k) *out_k = k;
    return value;
}

void *flow_cont_resume(flow_cont *k, void *value) {
    if (!k || !k->live || k->resumed) return NULL;
    k->resumed = 1;
    k->value = value;
    return value;
}

/* Multi-shot: same captured k can be resumed repeatedly (scaffold; no stack copy). */
void *flow_cont_resume_multi(flow_cont *k, void *value) {
    if (!k || !k->live) return NULL;
    k->value = value;
    return value;
}

void flow_cont_free(flow_cont *k) {
    if (!k) return;
    free(k->stack);
    free(k);
}

int32_t flow_cont_has_pending(void) {
    for (int i = 0; i < FLOW_FIBER_MAX; i++) {
        if (__atomic_load_n(&g_shift_pending[i], __ATOMIC_ACQUIRE)) return 1;
    }
    return 0;
}

int32_t flow_cont_shift_i32(void) {
#if FLOW_FCTX_ASM
    int32_t self = flow_fiber_current_id();
    if (self < 0 || self >= FLOW_FIBER_MAX) return -1;
    __atomic_store_n(&g_shift_pending[self], 1, __ATOMIC_RELEASE);
    flow_fiber_park();
    /* Resumed: Flow stack/locals intact. */
    __atomic_store_n(&g_shift_pending[self], 0, __ATOMIC_RELEASE);
    return __atomic_load_n(&g_shift_value[self], __ATOMIC_ACQUIRE);
#else
    return -1;
#endif
}

int32_t flow_cont_resume_pending(int32_t value) {
#if FLOW_FCTX_ASM
    pthread_mutex_lock(&g_shift_mu);
    int32_t target = -1;
    for (int i = 0; i < FLOW_FIBER_MAX; i++) {
        if (__atomic_load_n(&g_shift_pending[i], __ATOMIC_ACQUIRE)) {
            target = i;
            break;
        }
    }
    if (target < 0) {
        pthread_mutex_unlock(&g_shift_mu);
        return -1;
    }
    __atomic_store_n(&g_shift_value[target], value, __ATOMIC_RELEASE);
    pthread_mutex_unlock(&g_shift_mu);
    flow_fiber_unpark(target);
    return value;
#else
    (void)value;
    return -1;
#endif
}

static void armed_resumer(void *arg) {
    int32_t value = (int32_t)(intptr_t)arg;
    for (int i = 0; i < 10000000; i++) {
        if (flow_cont_has_pending()) {
            flow_cont_resume_pending(value);
            return;
        }
        flow_fiber_yield();
    }
}

void flow_rt_cont_arm_resume(int32_t value) {
#if FLOW_FCTX_ASM
    flow_fiber_spawn(armed_resumer, (void *)(intptr_t)value);
#else
    (void)value;
#endif
}

/* flow_cont_arm_resume → lib/runtime/cont.flow */

static void *demo_shift_body(void *arg, flow_cont *unused) {
    (void)arg;
    (void)unused;
    flow_cont *k = NULL;
    flow_shift(&k, (void *)(intptr_t)10);
    return (void *)(intptr_t)999;
}

int32_t flow_rt_cont_demo(void) {
    /* Reliable scaffold path (no fiber scheduler): reset → shift → resume. */
    flow_cont *k = NULL;
    void *r = flow_reset_ex(demo_shift_body, NULL, &k);
    if ((intptr_t)r != 10 || !k) {
        flow_cont_free(k);
        return -1;
    }
    void *r2 = flow_cont_resume(k, (void *)(intptr_t)42);
    flow_cont_free(k);
    if ((intptr_t)r2 != 42) return -2;
    return 42;
}

/* Nested reset demo: outer reset sees shift abort value 7. */
static void *nested_shift_body(void *arg, flow_cont *unused) {
    (void)arg;
    (void)unused;
    flow_cont *k = NULL;
    flow_shift(&k, (void *)(intptr_t)7);
    return (void *)(intptr_t)999;
}

int32_t flow_rt_cont_reset_demo(void) {
    flow_cont *k = NULL;
    void *r = flow_reset_ex(nested_shift_body, NULL, &k);
    if ((intptr_t)r != 7 || !k) {
        flow_cont_free(k);
        return -1;
    }
    void *r2 = flow_cont_resume(k, (void *)(intptr_t)100);
    flow_cont_free(k);
    if ((intptr_t)r2 != 100) return -2;
    return 100;
}

int32_t flow_rt_cont_multishot_demo(void) {
    flow_cont *k = NULL;
    void *r = flow_reset_ex(demo_shift_body, NULL, &k);
    if ((intptr_t)r != 10 || !k) {
        flow_cont_free(k);
        return -1;
    }
    void *a = flow_cont_resume_multi(k, (void *)(intptr_t)10);
    void *b = flow_cont_resume_multi(k, (void *)(intptr_t)20);
    void *c = flow_cont_resume(k, (void *)(intptr_t)99);
    flow_cont_free(k);
    if ((intptr_t)a != 10 || (intptr_t)b != 20 || (intptr_t)c != 99) return -2;
    return (int32_t)((intptr_t)a + (intptr_t)b); /* 30 */
}
