/* Opt-in race / deadlock hooks. Enable with FLOW_RACE=1.
 *
 * Detection logic, both tables, and every diagnostic live in
 * lib/runtime/race.flow. This file keeps only the parts Flow cannot express:
 * the thread-local lock stack, pthread_self as a thread key, and the two
 * table mutexes. Flow is called with the matching mutex already held.
 */
#include "flow_race.h"

#include <pthread.h>
#include <string.h>

#ifndef FLOW_RACE_DEPTH
#define FLOW_RACE_DEPTH 16
#endif

static pthread_mutex_t g_edge_mu = PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t g_shadow_mu = PTHREAD_MUTEX_INITIALIZER;

typedef struct {
    void *locks[FLOW_RACE_DEPTH];
    int n;
} lock_stack;

static _Thread_local lock_stack g_stack;
static _Thread_local unsigned long g_tid_key;

static unsigned long tid_key(void) {
    if (g_tid_key == 0) {
        g_tid_key = (unsigned long)pthread_self();
        if (g_tid_key == 0) g_tid_key = 1;
    }
    return g_tid_key;
}

void flow_race_mutex_lock(void *mu) {
    if (!flow_race_enabled() || !mu) return;
    for (int i = 0; i < g_stack.n; i++) {
        if (g_stack.locks[i] == mu) continue;
        pthread_mutex_lock(&g_edge_mu);
        flow_race_note_edge(g_stack.locks[i], mu);
        pthread_mutex_unlock(&g_edge_mu);
    }
    if (g_stack.n < FLOW_RACE_DEPTH) {
        g_stack.locks[g_stack.n++] = mu;
    }
}

void flow_race_mutex_unlock(void *mu) {
    if (!flow_race_enabled() || !mu) return;
    for (int i = g_stack.n - 1; i >= 0; i--) {
        if (g_stack.locks[i] == mu) {
            memmove(&g_stack.locks[i], &g_stack.locks[i + 1],
                    (size_t)(g_stack.n - i - 1) * sizeof(void *));
            g_stack.n--;
            return;
        }
    }
}

static void race_touch(void *addr, int32_t size, int32_t is_write) {
    if (!addr) return;
    unsigned long me = tid_key();
    int32_t locked = g_stack.n > 0 ? 1 : 0;
    pthread_mutex_lock(&g_shadow_mu);
    flow_race_shadow_touch(addr, size, is_write, (int64_t)me, locked);
    pthread_mutex_unlock(&g_shadow_mu);
}

void flow_race_read(void *addr, int32_t size) {
    if (!flow_race_enabled()) return;
    race_touch(addr, size, 0);
}

void flow_race_write(void *addr, int32_t size) {
    if (!flow_race_enabled()) return;
    race_touch(addr, size, 1);
}
